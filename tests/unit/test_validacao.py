"""Testes das validações de entrada do usuário."""
import pytest

from app.domain.erros import ErroDeValidacao
from app.domain.validacao import (
    MAX_PARTICIPANTES, normalizar_participantes, validar_formato, validar_jogo,
    validar_nome_torneio, validar_placar, validar_pontuacoes,
)


def test_nome_do_torneio_vazio_e_rejeitado():
    with pytest.raises(ErroDeValidacao, match="nome do torneio"):
        validar_nome_torneio("   ")


def test_nome_do_torneio_muito_longo_e_rejeitado():
    with pytest.raises(ErroDeValidacao, match="no máximo"):
        validar_nome_torneio("x" * 41)


def test_nome_do_torneio_tem_os_espacos_das_pontas_removidos():
    assert validar_nome_torneio("  Copa da Galera ") == "Copa da Galera"


def test_jogo_e_opcional():
    assert validar_jogo(None) == ""


def test_jogo_muito_longo_e_rejeitado():
    with pytest.raises(ErroDeValidacao):
        validar_jogo("y" * 41)


def test_formato_invalido_e_rejeitado():
    with pytest.raises(ErroDeValidacao, match="formato"):
        validar_formato("liga_dos_campeoes")


def test_participantes_ignoram_linhas_vazias_e_espacos_repetidos():
    assert normalizar_participantes("  Ana   Maria \n\nBia\n") == ["Ana Maria", "Bia"]


def test_participantes_repetidos_sao_rejeitados_sem_diferenciar_maiusculas():
    with pytest.raises(ErroDeValidacao, match="mais de uma vez"):
        normalizar_participantes(["Ana", "ANA"])


def test_participantes_exigem_pelo_menos_dois_nomes():
    with pytest.raises(ErroDeValidacao, match="pelo menos 2"):
        normalizar_participantes(["Ana"])


def test_participantes_respeitam_o_limite_maximo():
    nomes = [f"Jogador {i}" for i in range(MAX_PARTICIPANTES + 1)]
    with pytest.raises(ErroDeValidacao, match="limite"):
        normalizar_participantes(nomes)


def test_participante_com_nome_muito_longo_e_rejeitado():
    with pytest.raises(ErroDeValidacao, match="no máximo"):
        normalizar_participantes(["Ana", "z" * 41])


def test_placar_aceita_numeros_em_formato_de_texto():
    assert validar_placar("2", "1", permite_empate=False) == (2, 1)


def test_placar_com_texto_nao_numerico_e_rejeitado():
    with pytest.raises(ErroDeValidacao, match="números inteiros"):
        validar_placar("abc", "1", permite_empate=True)


def test_placar_ausente_e_rejeitado():
    with pytest.raises(ErroDeValidacao):
        validar_placar(None, None, permite_empate=True)


def test_placar_negativo_e_rejeitado():
    with pytest.raises(ErroDeValidacao, match="negativos"):
        validar_placar(-1, 0, permite_empate=True)


def test_placar_acima_do_maximo_e_rejeitado():
    with pytest.raises(ErroDeValidacao, match="máximo"):
        validar_placar(1000, 0, permite_empate=True)


def test_empate_e_rejeitado_no_mata_mata():
    with pytest.raises(ErroDeValidacao, match="empate"):
        validar_placar(1, 1, permite_empate=False)


def test_empate_e_permitido_nos_pontos_corridos():
    assert validar_placar(1, 1, permite_empate=True) == (1, 1)


def test_pontuacoes_aceitam_inteiros_e_empate_zero():
    assert validar_pontuacoes("4", 0) == (4, 0)


@pytest.mark.parametrize(
    ("vitoria", "empate", "mensagem"),
    [
        ("3.5", 1, "números inteiros"),
        (3.0, 1, "números inteiros"),
        (0, 0, "maior que zero"),
        (3, -1, "maior ou igual a zero"),
        (2, 2, "maior que a de empate"),
    ],
)
def test_pontuacoes_invalidas_sao_rejeitadas(vitoria, empate, mensagem):
    with pytest.raises(ErroDeValidacao, match=mensagem):
        validar_pontuacoes(vitoria, empate)
