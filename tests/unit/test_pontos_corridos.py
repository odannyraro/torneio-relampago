"""Testes do calendário de pontos corridos (todos contra todos)."""
import pytest

from app.domain.pontos_corridos import gerar_rodadas, quem_folga


def _todos_os_pares(rodadas):
    return [frozenset(par) for rodada in rodadas for par in rodada]


def test_quatro_participantes_geram_tres_rodadas_com_dois_jogos():
    rodadas = gerar_rodadas(4)
    assert len(rodadas) == 3
    assert all(len(rodada) == 2 for rodada in rodadas)


def test_dois_participantes_geram_uma_unica_partida():
    assert gerar_rodadas(2) == [[(0, 1)]]


def test_todos_se_enfrentam_exatamente_uma_vez():
    pares = _todos_os_pares(gerar_rodadas(6))
    assert len(pares) == 15            # 6 * 5 / 2
    assert len(set(pares)) == 15       # sem repetição


def test_ninguem_joga_duas_vezes_na_mesma_rodada():
    for rodada in gerar_rodadas(6):
        jogadores = [indice for par in rodada for indice in par]
        assert len(jogadores) == len(set(jogadores))


def test_numero_impar_de_participantes_gera_folga_em_toda_rodada():
    rodadas = gerar_rodadas(5)
    assert len(rodadas) == 5
    assert all(len(rodada) == 2 for rodada in rodadas)
    assert all(len(quem_folga(rodada, 5)) == 1 for rodada in rodadas)


def test_com_numero_impar_cada_participante_folga_uma_vez():
    folgas = [quem_folga(rodada, 5)[0] for rodada in gerar_rodadas(5)]
    assert sorted(folgas) == [0, 1, 2, 3, 4]


def test_ida_e_volta_dobra_as_rodadas_e_inverte_os_lados():
    rodadas = gerar_rodadas(4, ida_e_volta=True)
    assert len(rodadas) == 6
    assert rodadas[3] == [(b, a) for a, b in rodadas[0]]


def test_quem_folga_devolve_vazio_quando_todos_jogam():
    assert quem_folga([(0, 1), (2, 3)], 4) == []


def test_pontos_corridos_rejeitam_menos_de_dois_participantes():
    with pytest.raises(ValueError):
        gerar_rodadas(1)
