"""Geração de chaves de mata-mata (eliminatória simples).

Os participantes são identificados por índices (0, 1, 2...), em que o índice 0
é a "cabeça de chave 1". Quando o número de participantes não é potência de 2,
as vagas que sobram viram folgas (byes) e os melhores cabeças de chave avançam
direto para a rodada seguinte.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PartidaChave:
    """Uma partida da chave. lado1/lado2 são índices de participantes ou None (a definir/folga)."""

    rodada: int
    posicao: int
    lado1: Optional[int]
    lado2: Optional[int]
    eh_bye: bool = False


def proxima_potencia_de_dois(quantidade):
    """Menor potência de 2 maior ou igual a `quantidade` (ex.: 5 -> 8)."""
    if quantidade < 1:
        raise ValueError("A quantidade deve ser pelo menos 1.")
    potencia = 1
    while potencia < quantidade:
        potencia *= 2
    return potencia


def total_de_rodadas(quantidade):
    """Número de rodadas de um mata-mata com `quantidade` participantes (ex.: 5 -> 3)."""
    return proxima_potencia_de_dois(quantidade).bit_length() - 1


def ordem_das_cabecas(tamanho):
    """Ordem padrão das cabeças de chave na primeira rodada.

    Garante que os melhores só se enfrentem o mais tarde possível.
    Exemplo: tamanho 8 -> [1, 8, 4, 5, 2, 7, 3, 6] (partidas 1x8, 4x5, 2x7, 3x6).
    """
    ordem = [1]
    while len(ordem) < tamanho:
        soma = len(ordem) * 2 + 1  # cada cabeça enfrenta a que completa essa soma
        ordem = [cabeca for c in ordem for cabeca in (c, soma - c)]
    return ordem


def gerar_chaveamento(quantidade):
    """Gera todas as partidas da chave, da primeira rodada até a final.

    Só a primeira rodada vem com participantes; as demais são preenchidas
    conforme os vencedores avançam.
    """
    if quantidade < 2:
        raise ValueError("Um mata-mata precisa de pelo menos 2 participantes.")

    tamanho = proxima_potencia_de_dois(quantidade)
    ordem = ordem_das_cabecas(tamanho)
    partidas = []

    # Primeira rodada: cabeças acima de `quantidade` não existem e viram folga.
    for posicao in range(tamanho // 2):
        cabeca1, cabeca2 = ordem[2 * posicao], ordem[2 * posicao + 1]
        lado1 = cabeca1 - 1 if cabeca1 <= quantidade else None
        lado2 = cabeca2 - 1 if cabeca2 <= quantidade else None
        eh_bye = lado1 is None or lado2 is None
        partidas.append(PartidaChave(1, posicao, lado1, lado2, eh_bye))

    # Demais rodadas: vazias até os vencedores avançarem.
    for rodada in range(2, total_de_rodadas(quantidade) + 1):
        for posicao in range(tamanho // 2**rodada):
            partidas.append(PartidaChave(rodada, posicao, None, None))

    return partidas


def destino_do_vencedor(rodada, posicao, rodadas_totais):
    """Para onde vai o vencedor: (rodada, posição, lado) da próxima partida, ou None na final."""
    if rodada >= rodadas_totais:
        return None
    lado = 1 if posicao % 2 == 0 else 2
    return rodada + 1, posicao // 2, lado


def nome_da_rodada(rodada, rodadas_totais):
    """Nome amigável da rodada, contando a partir da final."""
    nomes = {0: "Final", 1: "Semifinal", 2: "Quartas de final", 3: "Oitavas de final"}
    return nomes.get(rodadas_totais - rodada, f"Rodada {rodada}")
