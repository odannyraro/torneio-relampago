"""Testes da geração de chaves de mata-mata."""
import pytest

from app.domain.chaveamento import (
    destino_do_vencedor, gerar_chaveamento, nome_da_rodada, ordem_das_cabecas,
    proxima_potencia_de_dois, total_de_rodadas,
)


@pytest.mark.parametrize("quantidade, esperado", [(1, 1), (2, 2), (3, 4), (5, 8), (8, 8), (9, 16)])
def test_proxima_potencia_de_dois_arredonda_para_cima(quantidade, esperado):
    assert proxima_potencia_de_dois(quantidade) == esperado


def test_proxima_potencia_de_dois_rejeita_zero():
    with pytest.raises(ValueError):
        proxima_potencia_de_dois(0)


@pytest.mark.parametrize("quantidade, esperado", [(2, 1), (3, 2), (4, 2), (5, 3), (8, 3), (9, 4)])
def test_total_de_rodadas_cresce_com_a_potencia_de_dois(quantidade, esperado):
    assert total_de_rodadas(quantidade) == esperado


def test_ordem_das_cabecas_para_oito_separa_os_melhores():
    assert ordem_das_cabecas(8) == [1, 8, 4, 5, 2, 7, 3, 6]


def test_chaveamento_potencia_de_dois_nao_tem_folga():
    partidas = gerar_chaveamento(8)
    primeira_rodada = [p for p in partidas if p.rodada == 1]
    assert len(partidas) == 7
    assert len(primeira_rodada) == 4
    assert not any(p.eh_bye for p in partidas)


def test_chaveamento_com_cinco_participantes_tem_tres_folgas():
    folgas = [p for p in gerar_chaveamento(5) if p.eh_bye]
    assert len(folgas) == 3


def test_folgas_ficam_com_as_melhores_cabecas_de_chave():
    folgas = [p for p in gerar_chaveamento(5) if p.eh_bye]
    quem_folga = {p.lado1 if p.lado1 is not None else p.lado2 for p in folgas}
    assert quem_folga == {0, 1, 2}  # cabeças 1, 2 e 3


def test_cabecas_um_e_dois_ficam_em_metades_opostas_da_chave():
    primeira_rodada = [p for p in gerar_chaveamento(8) if p.rodada == 1]
    posicao_da_cabeca = {}
    for partida in primeira_rodada:
        for lado in (partida.lado1, partida.lado2):
            posicao_da_cabeca[lado] = partida.posicao
    assert posicao_da_cabeca[0] < 2 <= posicao_da_cabeca[1]


def test_chaveamento_so_preenche_participantes_na_primeira_rodada():
    partidas = gerar_chaveamento(4)
    finais = [p for p in partidas if p.rodada == 2]
    assert len(finais) == 1
    assert finais[0].lado1 is None and finais[0].lado2 is None


def test_chaveamento_rejeita_menos_de_dois_participantes():
    with pytest.raises(ValueError):
        gerar_chaveamento(1)


def test_vencedor_avanca_alternando_os_lados_da_proxima_partida():
    assert destino_do_vencedor(1, 0, 3) == (2, 0, 1)
    assert destino_do_vencedor(1, 1, 3) == (2, 0, 2)
    assert destino_do_vencedor(1, 2, 3) == (2, 1, 1)


def test_vencedor_da_final_nao_tem_destino():
    assert destino_do_vencedor(3, 0, 3) is None


def test_nome_da_rodada_conta_a_partir_da_final():
    assert nome_da_rodada(3, 3) == "Final"
    assert nome_da_rodada(2, 3) == "Semifinal"
    assert nome_da_rodada(1, 3) == "Quartas de final"
    assert nome_da_rodada(1, 4) == "Oitavas de final"
    assert nome_da_rodada(1, 5) == "Rodada 1"
