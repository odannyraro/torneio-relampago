"""Casos de uso do torneio.

O serviço combina as regras puras do domínio com o repositório. Ele não conhece
Flask: recebe uma conexão SQLite e pode ser testado com um banco em memória.
"""
import random

from ..domain.chaveamento import (
    destino_do_vencedor, gerar_chaveamento, nome_da_rodada, total_de_rodadas,
)
from ..domain.classificacao import Resultado, calcular_classificacao
from ..domain.erros import ErroDeValidacao, NaoEncontrado
from ..domain.pontos_corridos import gerar_rodadas, quem_folga
from ..domain.validacao import (
    MATA_MATA, PONTOS_CORRIDOS, normalizar_participantes, validar_formato,
    validar_jogo, validar_nome_torneio, validar_placar,
)
from ..repositories.torneio_repository import TorneioRepository

A_DEFINIR = "A definir"


class TorneioService:
    """Operações de alto nível sobre torneios."""

    def __init__(self, conexao, sorteio=None):
        """`sorteio` é um random.Random; injetá-lo torna o embaralhamento previsível nos testes."""
        self._conexao = conexao
        self._repo = TorneioRepository(conexao)
        self._sorteio = sorteio or random.Random()

    # ================================================================ criação
    def criar_torneio(
        self, nome, jogo, formato, nomes_participantes, embaralhar=True, ida_e_volta=False
    ):
        """Valida os dados, sorteia a ordem (opcional) e gera todas as partidas. Devolve o id."""
        nome = validar_nome_torneio(nome)
        jogo = validar_jogo(jogo)
        formato = validar_formato(formato)
        nomes = normalizar_participantes(nomes_participantes)
        if embaralhar:
            self._sorteio.shuffle(nomes)
        ida_e_volta = bool(ida_e_volta) and formato == PONTOS_CORRIDOS

        with self._conexao:  # transação: ou cria tudo, ou nada
            torneio_id = self._repo.criar_torneio(nome, jogo, formato, ida_e_volta)
            ids = self._repo.adicionar_participantes(torneio_id, nomes)
            if formato == MATA_MATA:
                self._criar_partidas_mata_mata(torneio_id, ids)
            else:
                self._criar_partidas_pontos_corridos(torneio_id, ids, ida_e_volta)
        return torneio_id

    def _criar_partidas_mata_mata(self, torneio_id, ids):
        """Cria a chave inteira e já faz os participantes com folga avançarem."""
        rodadas_totais = total_de_rodadas(len(ids))
        folgas = []
        for partida in gerar_chaveamento(len(ids)):
            id1 = ids[partida.lado1] if partida.lado1 is not None else None
            id2 = ids[partida.lado2] if partida.lado2 is not None else None
            vencedor = None
            if partida.eh_bye:
                vencedor = id1 if id1 is not None else id2
                folgas.append((partida.rodada, partida.posicao, vencedor))
            self._repo.criar_partida(
                torneio_id, partida.rodada, partida.posicao, id1, id2, partida.eh_bye, vencedor
            )
        # As partidas da rodada seguinte só existem depois do laço acima.
        for rodada, posicao, vencedor in folgas:
            self._avancar_vencedor(torneio_id, rodada, posicao, vencedor, rodadas_totais)

    def _criar_partidas_pontos_corridos(self, torneio_id, ids, ida_e_volta):
        """Cria todas as rodadas do todos-contra-todos."""
        for numero, rodada in enumerate(gerar_rodadas(len(ids), ida_e_volta), start=1):
            for posicao, (i, j) in enumerate(rodada):
                self._repo.criar_partida(torneio_id, numero, posicao, ids[i], ids[j])

    def _avancar_vencedor(self, torneio_id, rodada, posicao, vencedor_id, rodadas_totais):
        """Coloca o vencedor no lado certo da partida da rodada seguinte (se houver)."""
        destino = destino_do_vencedor(rodada, posicao, rodadas_totais)
        if destino is None:
            return
        proxima_rodada, proxima_posicao, lado = destino
        proxima = self._repo.buscar_partida_por_posicao(torneio_id, proxima_rodada, proxima_posicao)
        self._repo.definir_participante(proxima["id"], lado, vencedor_id)

    # ====================================================== registro de resultado
    def registrar_resultado(self, torneio_id, partida_id, placar1, placar2):
        """Salva (ou corrige) o placar de uma partida e, no mata-mata, avança o vencedor."""
        torneio = self._obter_torneio_ou_falhar(torneio_id)
        partida = self._repo.buscar_partida(torneio_id, partida_id)
        if partida is None:
            raise NaoEncontrado("Partida não encontrada.")
        if partida["eh_bye"]:
            raise ErroDeValidacao("Esta partida é uma folga e não tem resultado.")
        if partida["participante1_id"] is None or partida["participante2_id"] is None:
            raise ErroDeValidacao("Esta partida ainda não tem os dois participantes definidos.")

        mata_mata = torneio["formato"] == MATA_MATA
        gols1, gols2 = validar_placar(placar1, placar2, permite_empate=not mata_mata)
        if gols1 > gols2:
            vencedor = partida["participante1_id"]
        elif gols2 > gols1:
            vencedor = partida["participante2_id"]
        else:
            vencedor = None  # empate (só possível em pontos corridos)

        with self._conexao:
            if mata_mata:
                self._atualizar_proxima_fase(torneio_id, partida, vencedor)
            self._repo.salvar_resultado(partida_id, gols1, gols2, vencedor)

    def _atualizar_proxima_fase(self, torneio_id, partida, vencedor):
        """Move o vencedor para a próxima partida, bloqueando correções que quebrariam a chave."""
        quantidade = len(self._repo.listar_participantes(torneio_id))
        destino = destino_do_vencedor(
            partida["rodada"], partida["posicao"], total_de_rodadas(quantidade)
        )
        if destino is None:
            return  # era a final
        proxima_rodada, proxima_posicao, lado = destino
        proxima = self._repo.buscar_partida_por_posicao(torneio_id, proxima_rodada, proxima_posicao)
        vencedor_mudou = vencedor != partida["vencedor_id"]
        if vencedor_mudou and proxima["placar1"] is not None:
            raise ErroDeValidacao(
                "Não é possível alterar o vencedor: a próxima partida já foi jogada."
            )
        self._repo.definir_participante(proxima["id"], lado, vencedor)

    # ================================================================ consultas
    def obter_torneio(self, torneio_id):
        """Devolve o torneio completo (partidas, rodadas, classificação e campeão) como dicionário."""
        torneio = self._obter_torneio_ou_falhar(torneio_id)
        participantes = self._repo.listar_participantes(torneio_id)
        nomes = {p["id"]: p["nome"] for p in participantes}
        partidas = [self._montar_partida(p, nomes) for p in self._repo.listar_partidas(torneio_id)]
        mata_mata = torneio["formato"] == MATA_MATA

        rodadas = self._agrupar_rodadas(partidas, participantes, mata_mata)
        jogaveis = [p for p in partidas if not p["eh_bye"]]
        jogadas = sum(1 for p in jogaveis if p["jogada"])
        progresso = {
            "jogadas": jogadas,
            "total": len(jogaveis),
            "percentual": round(100 * jogadas / len(jogaveis)) if jogaveis else 0,
        }

        classificacao = []
        if not mata_mata:
            resultados = [
                Resultado(p["participante1_id"], p["participante2_id"], p["placar1"], p["placar2"])
                for p in partidas if p["jogada"]
            ]
            linhas = calcular_classificacao([(p["id"], p["nome"]) for p in participantes], resultados)
            classificacao = [linha.para_dict() for linha in linhas]

        return {
            "id": torneio["id"],
            "nome": torneio["nome"],
            "jogo": torneio["jogo"],
            "formato": torneio["formato"],
            "ida_e_volta": bool(torneio["ida_e_volta"]),
            "criado_em": torneio["criado_em"],
            "participantes": [{"id": p["id"], "nome": p["nome"]} for p in participantes],
            "partidas": partidas,
            "rodadas": rodadas,
            "classificacao": classificacao,
            "campeao": self._descobrir_campeao(mata_mata, partidas, classificacao, progresso, nomes),
            "progresso": progresso,
        }

    def listar_torneios(self):
        """Resumo de todos os torneios, do mais recente para o mais antigo."""
        resumos = []
        for linha in self._repo.listar_torneios():
            detalhe = self.obter_torneio(linha["id"])
            resumos.append({
                "id": detalhe["id"],
                "nome": detalhe["nome"],
                "jogo": detalhe["jogo"],
                "formato": detalhe["formato"],
                "participantes": len(detalhe["participantes"]),
                "progresso": detalhe["progresso"],
                "campeao": detalhe["campeao"],
            })
        return resumos

    def excluir_torneio(self, torneio_id):
        """Remove o torneio e todos os dados ligados a ele."""
        self._obter_torneio_ou_falhar(torneio_id)
        with self._conexao:
            self._repo.excluir_torneio(torneio_id)

    # ========================================================= funções auxiliares
    def _obter_torneio_ou_falhar(self, torneio_id):
        torneio = self._repo.buscar_torneio(torneio_id)
        if torneio is None:
            raise NaoEncontrado("Torneio não encontrado.")
        return torneio

    @staticmethod
    def _montar_partida(linha, nomes):
        """Converte uma linha do banco em um dicionário pronto para a interface/JSON."""
        id1, id2 = linha["participante1_id"], linha["participante2_id"]
        eh_bye = bool(linha["eh_bye"])
        presente = id1 if id1 is not None else id2  # no bye só um lado está preenchido
        return {
            "id": linha["id"],
            "rodada": linha["rodada"],
            "posicao": linha["posicao"],
            "participante1_id": id1,
            "participante2_id": id2,
            "nome1": nomes.get(id1, A_DEFINIR),
            "nome2": nomes.get(id2, A_DEFINIR),
            "placar1": linha["placar1"],
            "placar2": linha["placar2"],
            "vencedor_id": linha["vencedor_id"],
            "nome_vencedor": nomes.get(presente) if eh_bye else nomes.get(linha["vencedor_id"]),
            "eh_bye": eh_bye,
            "jogada": linha["placar1"] is not None,
            "pode_registrar": not eh_bye and id1 is not None and id2 is not None,
        }

    @staticmethod
    def _agrupar_rodadas(partidas, participantes, mata_mata):
        """Agrupa as partidas por rodada e calcula quem folga em cada uma."""
        total = max((p["rodada"] for p in partidas), default=0)
        ids_dos_participantes = [p["id"] for p in participantes]
        rodadas = []
        for numero in range(1, total + 1):
            da_rodada = [p for p in partidas if p["rodada"] == numero]
            folgas = []
            if not mata_mata:
                pares = [(ids_dos_participantes.index(p["participante1_id"]),
                          ids_dos_participantes.index(p["participante2_id"])) for p in da_rodada]
                folgas = [participantes[i]["nome"] for i in quem_folga(pares, len(participantes))]
            rodadas.append({
                "numero": numero,
                "nome": nome_da_rodada(numero, total) if mata_mata else f"Rodada {numero}",
                "partidas": da_rodada,
                "folgas": folgas,
            })
        return rodadas

    @staticmethod
    def _descobrir_campeao(mata_mata, partidas, classificacao, progresso, nomes):
        """Mata-mata: vencedor da final. Pontos corridos: líder, depois que todos os jogos acabam."""
        if mata_mata:
            final = partidas[-1]
            if final["vencedor_id"] is None:
                return None
            return {"id": final["vencedor_id"], "nome": nomes[final["vencedor_id"]]}
        if progresso["total"] and progresso["jogadas"] == progresso["total"]:
            lider = classificacao[0]
            return {"id": lider["participante_id"], "nome": lider["nome"]}
        return None
