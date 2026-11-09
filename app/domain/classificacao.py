"""Cálculo da tabela de classificação dos pontos corridos."""
from dataclasses import dataclass, asdict
from typing import Iterable, Sequence, Tuple

PONTOS_VITORIA = 3
PONTOS_EMPATE = 1


@dataclass(frozen=True)
class Resultado:
    """Resultado de uma partida já jogada."""

    participante1_id: int
    participante2_id: int
    placar1: int
    placar2: int


@dataclass
class LinhaClassificacao:
    """Uma linha da tabela de classificação."""

    participante_id: int
    nome: str
    posicao: int = 0
    jogos: int = 0
    vitorias: int = 0
    empates: int = 0
    derrotas: int = 0
    gols_pro: int = 0
    gols_contra: int = 0
    pontos: int = 0

    @property
    def saldo(self):
        """Saldo de gols (gols pró menos gols contra)."""
        return self.gols_pro - self.gols_contra

    def para_dict(self):
        """Versão em dicionário (inclui o saldo) para JSON e templates."""
        dados = asdict(self)
        dados["saldo"] = self.saldo
        return dados


def _registrar_jogo(linha, gols_pro, gols_contra):
    """Atualiza a linha de um participante com o resultado de uma partida."""
    linha.jogos += 1
    linha.gols_pro += gols_pro
    linha.gols_contra += gols_contra
    if gols_pro > gols_contra:
        linha.vitorias += 1
        linha.pontos += PONTOS_VITORIA
    elif gols_pro == gols_contra:
        linha.empates += 1
        linha.pontos += PONTOS_EMPATE
    else:
        linha.derrotas += 1


def _chave_de_ordenacao(linha):
    """Critérios de desempate, em ordem: pontos, vitórias, saldo, gols pró e nome."""
    return (-linha.pontos, -linha.vitorias, -linha.saldo, -linha.gols_pro, linha.nome.casefold())


def calcular_classificacao(
    participantes: Sequence[Tuple[int, str]], resultados: Iterable[Resultado]
):
    """Monta a tabela ordenada a partir dos participantes (id, nome) e dos resultados."""
    tabela = {pid: LinhaClassificacao(pid, nome) for pid, nome in participantes}

    for resultado in resultados:
        _registrar_jogo(tabela[resultado.participante1_id], resultado.placar1, resultado.placar2)
        _registrar_jogo(tabela[resultado.participante2_id], resultado.placar2, resultado.placar1)

    linhas = sorted(tabela.values(), key=_chave_de_ordenacao)
    for posicao, linha in enumerate(linhas, start=1):
        linha.posicao = posicao
    return linhas
