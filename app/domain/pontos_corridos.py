"""Geração do calendário de pontos corridos (todos contra todos).

Usa o "método do círculo": um participante fica fixo e os demais giram a cada
rodada. Com número ímpar de participantes entra uma vaga fantasma (None) e
quem enfrentaria essa vaga folga na rodada.
"""


def gerar_rodadas(quantidade, ida_e_volta=False):
    """Devolve uma lista de rodadas; cada rodada é uma lista de pares (índice1, índice2).

    Com `ida_e_volta=True` o returno repete as rodadas invertendo os lados.
    """
    if quantidade < 2:
        raise ValueError("Pontos corridos precisam de pelo menos 2 participantes.")

    indices = list(range(quantidade))
    if quantidade % 2 == 1:
        indices.append(None)  # vaga fantasma: quem pegar essa vaga folga

    total = len(indices)
    rodadas = []
    for _ in range(total - 1):
        rodada = []
        for i in range(total // 2):
            a, b = indices[i], indices[total - 1 - i]
            if a is not None and b is not None:
                rodada.append((a, b))
        rodadas.append(rodada)
        # Gira todos, exceto o primeiro, que fica fixo.
        indices = [indices[0], indices[-1]] + indices[1:-1]

    if ida_e_volta:
        returno = [[(b, a) for a, b in rodada] for rodada in rodadas]
        rodadas = rodadas + returno
    return rodadas


def quem_folga(rodada, quantidade):
    """Índices dos participantes que não jogam na rodada (útil com número ímpar)."""
    jogando = {indice for par in rodada for indice in par}
    return sorted(set(range(quantidade)) - jogando)
