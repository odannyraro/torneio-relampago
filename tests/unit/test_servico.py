"""Testes do serviço de torneios (domínio + banco SQLite em memória)."""
import random

import pytest

from app.domain.erros import ErroDeValidacao, NaoEncontrado

NOMES = ["Ana", "Bia", "Caio", "Duda"]


def _mata_mata(servico, nomes=NOMES, **opcoes):
    return servico.criar_torneio("Copa", "FIFA", "mata_mata", nomes, embaralhar=False, **opcoes)


def _pontos_corridos(servico, nomes=NOMES, **opcoes):
    return servico.criar_torneio("Liga", "Mario Kart", "pontos_corridos", nomes, embaralhar=False, **opcoes)


def _partida(servico, torneio_id, rodada, posicao):
    """Busca uma partida pela posição na chave."""
    partidas = servico.obter_torneio(torneio_id)["partidas"]
    return next(p for p in partidas if p["rodada"] == rodada and p["posicao"] == posicao)


# ------------------------------------------------------------------ criação
def test_mata_mata_com_quatro_participantes_cria_tres_partidas(servico):
    torneio = servico.obter_torneio(_mata_mata(servico))
    assert len(torneio["partidas"]) == 3
    assert [r["nome"] for r in torneio["rodadas"]] == ["Semifinal", "Final"]


def test_mata_mata_com_cinco_faz_as_melhores_cabecas_avancarem_com_folga(servico):
    torneio_id = _mata_mata(servico, ["Ana", "Bia", "Caio", "Duda", "Eli"])
    semi_1, semi_2 = _partida(servico, torneio_id, 2, 0), _partida(servico, torneio_id, 2, 1)
    assert (semi_1["nome1"], semi_1["nome2"]) == ("Ana", "A definir")
    assert (semi_2["nome1"], semi_2["nome2"]) == ("Bia", "Caio")
    assert semi_2["pode_registrar"] and not semi_1["pode_registrar"]


def test_sem_embaralhar_a_ordem_informada_e_mantida(servico):
    torneio = servico.obter_torneio(_mata_mata(servico))
    assert [p["nome"] for p in torneio["participantes"]] == NOMES


def test_embaralhar_usa_o_sorteio_injetado(servico):
    esperado = list(NOMES)
    random.Random(1).shuffle(esperado)  # mesma semente da fixture
    torneio_id = servico.criar_torneio("Copa", "", "mata_mata", NOMES, embaralhar=True)
    assert [p["nome"] for p in servico.obter_torneio(torneio_id)["participantes"]] == esperado


def test_pontos_corridos_com_quatro_participantes_criam_seis_partidas(servico):
    torneio = servico.obter_torneio(_pontos_corridos(servico))
    assert len(torneio["partidas"]) == 6
    assert len(torneio["rodadas"]) == 3


def test_ida_e_volta_dobra_as_partidas_dos_pontos_corridos(servico):
    torneio = servico.obter_torneio(_pontos_corridos(servico, ida_e_volta=True))
    assert len(torneio["partidas"]) == 12
    assert torneio["ida_e_volta"] is True


def test_ida_e_volta_e_ignorada_no_mata_mata(servico):
    torneio = servico.obter_torneio(_mata_mata(servico, ida_e_volta=True))
    assert torneio["ida_e_volta"] is False


def test_rodadas_de_pontos_corridos_informam_quem_folga(servico):
    torneio = servico.obter_torneio(_pontos_corridos(servico, ["Ana", "Bia", "Caio"]))
    assert len(torneio["rodadas"]) == 3
    assert all(len(r["folgas"]) == 1 for r in torneio["rodadas"])


def test_torneio_invalido_nao_grava_nada(servico):
    with pytest.raises(ErroDeValidacao):
        _mata_mata(servico, ["Ana"])
    assert servico.listar_torneios() == []


# ------------------------------------------------------- mata-mata: resultados
def test_vencedor_da_partida_avanca_para_a_proxima_fase(servico):
    torneio_id = _mata_mata(servico)  # semifinais: Ana x Duda e Bia x Caio
    servico.registrar_resultado(torneio_id, _partida(servico, torneio_id, 1, 0)["id"], 2, 0)
    final = _partida(servico, torneio_id, 2, 0)
    assert (final["nome1"], final["nome2"]) == ("Ana", "A definir")


def test_mata_mata_nao_aceita_empate(servico):
    torneio_id = _mata_mata(servico)
    with pytest.raises(ErroDeValidacao, match="empate"):
        servico.registrar_resultado(torneio_id, _partida(servico, torneio_id, 1, 0)["id"], 1, 1)


def test_campeao_e_o_vencedor_da_final(servico):
    torneio_id = _mata_mata(servico)
    servico.registrar_resultado(torneio_id, _partida(servico, torneio_id, 1, 0)["id"], 2, 0)  # Ana
    servico.registrar_resultado(torneio_id, _partida(servico, torneio_id, 1, 1)["id"], 0, 1)  # Caio
    assert servico.obter_torneio(torneio_id)["campeao"] is None
    servico.registrar_resultado(torneio_id, _partida(servico, torneio_id, 2, 0)["id"], 3, 2)
    assert servico.obter_torneio(torneio_id)["campeao"]["nome"] == "Ana"


def test_partida_sem_os_dois_participantes_nao_aceita_resultado(servico):
    torneio_id = _mata_mata(servico)
    with pytest.raises(ErroDeValidacao, match="ainda não tem"):
        servico.registrar_resultado(torneio_id, _partida(servico, torneio_id, 2, 0)["id"], 1, 0)


def test_partida_de_folga_nao_aceita_resultado(servico):
    torneio_id = _mata_mata(servico, ["Ana", "Bia", "Caio", "Duda", "Eli"])
    folga = _partida(servico, torneio_id, 1, 0)
    with pytest.raises(ErroDeValidacao, match="folga"):
        servico.registrar_resultado(torneio_id, folga["id"], 1, 0)


def test_corrigir_resultado_troca_o_vencedor_se_a_proxima_partida_nao_foi_jogada(servico):
    torneio_id = _mata_mata(servico)
    id_partida = _partida(servico, torneio_id, 1, 0)["id"]
    servico.registrar_resultado(torneio_id, id_partida, 2, 0)   # Ana vence
    servico.registrar_resultado(torneio_id, id_partida, 0, 2)   # correção: Duda vence
    assert _partida(servico, torneio_id, 2, 0)["nome1"] == "Duda"


def test_corrigir_o_vencedor_e_bloqueado_se_a_proxima_partida_ja_foi_jogada(servico):
    torneio_id = _mata_mata(servico)
    semi_1, semi_2 = (_partida(servico, torneio_id, 1, p)["id"] for p in (0, 1))
    servico.registrar_resultado(torneio_id, semi_1, 2, 0)
    servico.registrar_resultado(torneio_id, semi_2, 1, 0)
    servico.registrar_resultado(torneio_id, _partida(servico, torneio_id, 2, 0)["id"], 1, 0)
    with pytest.raises(ErroDeValidacao, match="já foi jogada"):
        servico.registrar_resultado(torneio_id, semi_1, 0, 2)


def test_corrigir_o_placar_mantendo_o_vencedor_e_permitido_mesmo_depois_da_final(servico):
    torneio_id = _mata_mata(servico)
    semi_1, semi_2 = (_partida(servico, torneio_id, 1, p)["id"] for p in (0, 1))
    servico.registrar_resultado(torneio_id, semi_1, 2, 0)
    servico.registrar_resultado(torneio_id, semi_2, 1, 0)
    servico.registrar_resultado(torneio_id, _partida(servico, torneio_id, 2, 0)["id"], 1, 0)
    servico.registrar_resultado(torneio_id, semi_1, 5, 0)  # mesmo vencedor (Ana)
    assert _partida(servico, torneio_id, 1, 0)["placar1"] == 5


# --------------------------------------------------- pontos corridos: resultados
def test_resultado_atualiza_a_classificacao(servico):
    torneio_id = _pontos_corridos(servico)
    partida = servico.obter_torneio(torneio_id)["partidas"][0]
    servico.registrar_resultado(torneio_id, partida["id"], 3, 1)
    lider = servico.obter_torneio(torneio_id)["classificacao"][0]
    assert (lider["nome"], lider["pontos"], lider["saldo"]) == (partida["nome1"], 3, 2)


def test_pontos_corridos_aceitam_empate(servico):
    torneio_id = _pontos_corridos(servico)
    partida = servico.obter_torneio(torneio_id)["partidas"][0]
    servico.registrar_resultado(torneio_id, partida["id"], 2, 2)
    linhas = servico.obter_torneio(torneio_id)["classificacao"]
    assert sorted(l["pontos"] for l in linhas) == [0, 0, 1, 1]


def test_campeao_dos_pontos_corridos_so_aparece_depois_de_todos_os_jogos(servico):
    torneio_id = _pontos_corridos(servico, ["Ana", "Bia"])
    assert servico.obter_torneio(torneio_id)["campeao"] is None
    partida = servico.obter_torneio(torneio_id)["partidas"][0]
    servico.registrar_resultado(torneio_id, partida["id"], 1, 0)
    torneio = servico.obter_torneio(torneio_id)
    assert torneio["campeao"]["nome"] == partida["nome1"]
    assert torneio["progresso"] == {"jogadas": 1, "total": 1, "percentual": 100}


# ----------------------------------------------------------- consultas e exclusão
def test_torneio_inexistente_levanta_nao_encontrado(servico):
    with pytest.raises(NaoEncontrado):
        servico.obter_torneio(999)


def test_partida_inexistente_levanta_nao_encontrado(servico):
    torneio_id = _mata_mata(servico)
    with pytest.raises(NaoEncontrado):
        servico.registrar_resultado(torneio_id, 999, 1, 0)


def test_listar_torneios_mostra_o_mais_recente_primeiro(servico):
    _mata_mata(servico)
    _pontos_corridos(servico)
    resumos = servico.listar_torneios()
    assert [r["nome"] for r in resumos] == ["Liga", "Copa"]
    assert resumos[0]["participantes"] == 4


def test_excluir_torneio_remove_tudo(servico, conexao):
    torneio_id = _mata_mata(servico)
    servico.excluir_torneio(torneio_id)
    assert servico.listar_torneios() == []
    for tabela in ("participantes", "partidas"):
        assert conexao.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0] == 0


def test_excluir_torneio_inexistente_levanta_nao_encontrado(servico):
    with pytest.raises(NaoEncontrado):
        servico.excluir_torneio(42)
