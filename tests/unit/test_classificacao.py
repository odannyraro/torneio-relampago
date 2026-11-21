"""Testes do cálculo da tabela de classificação e dos critérios de desempate."""
from app.domain.classificacao import Resultado, calcular_classificacao

ANA, BIA, CAIO, DUDA, ELI = (1, "Ana"), (2, "Bia"), (3, "Caio"), (4, "Duda"), (5, "Eli")


def _nomes_na_ordem(tabela):
    return [linha.nome for linha in tabela]


def test_vitoria_vale_tres_pontos_e_derrota_vale_zero():
    tabela = calcular_classificacao([ANA, BIA], [Resultado(1, 2, 2, 0)])
    assert (tabela[0].nome, tabela[0].pontos, tabela[0].vitorias) == ("Ana", 3, 1)
    assert (tabela[1].nome, tabela[1].pontos, tabela[1].derrotas) == ("Bia", 0, 1)


def test_empate_vale_um_ponto_para_cada_lado():
    tabela = calcular_classificacao([ANA, BIA], [Resultado(1, 2, 1, 1)])
    assert [linha.pontos for linha in tabela] == [1, 1]
    assert [linha.empates for linha in tabela] == [1, 1]


def test_classificacao_usa_pontuacoes_configuradas():
    resultados = [Resultado(1, 2, 2, 0), Resultado(1, 2, 1, 1)]
    tabela = calcular_classificacao(
        [ANA, BIA], resultados, pontos_vitoria=5, pontos_empate=2
    )
    assert [(linha.nome, linha.pontos) for linha in tabela] == [("Ana", 7), ("Bia", 2)]


def test_gols_pro_gols_contra_e_saldo_sao_acumulados():
    resultados = [Resultado(1, 2, 3, 1), Resultado(1, 3, 0, 2)]
    ana = next(l for l in calcular_classificacao([ANA, BIA, CAIO], resultados) if l.nome == "Ana")
    assert (ana.gols_pro, ana.gols_contra, ana.saldo, ana.jogos) == (3, 3, 0, 2)


def test_desempate_por_numero_de_vitorias():
    # Ana: 1 vitória (3 pts). Bia: 3 empates (3 pts). Ana fica na frente por ter mais vitórias.
    resultados = [
        Resultado(1, 5, 1, 0),
        Resultado(2, 3, 0, 0), Resultado(2, 4, 0, 0), Resultado(2, 5, 0, 0),
    ]
    tabela = calcular_classificacao([ANA, BIA, CAIO, DUDA, ELI], resultados)
    assert _nomes_na_ordem(tabela)[:2] == ["Ana", "Bia"]


def test_desempate_por_saldo_de_gols():
    resultados = [Resultado(2, 4, 1, 0), Resultado(1, 3, 3, 0)]  # Bia +1, Ana +3
    tabela = calcular_classificacao([ANA, BIA, CAIO, DUDA], resultados)
    assert _nomes_na_ordem(tabela)[:2] == ["Ana", "Bia"]


def test_desempate_por_gols_pro_quando_o_saldo_empata():
    resultados = [Resultado(2, 4, 1, 0), Resultado(1, 3, 2, 1)]  # ambas +1; Ana fez 2, Bia fez 1
    tabela = calcular_classificacao([BIA, ANA, CAIO, DUDA], resultados)
    assert _nomes_na_ordem(tabela)[:2] == ["Ana", "Bia"]


def test_desempate_final_por_ordem_alfabetica():
    tabela = calcular_classificacao([CAIO, ANA, BIA], [])
    assert _nomes_na_ordem(tabela) == ["Ana", "Bia", "Caio"]


def test_posicoes_sao_numeradas_a_partir_de_um():
    tabela = calcular_classificacao([ANA, BIA, CAIO], [Resultado(1, 2, 1, 0)])
    assert [linha.posicao for linha in tabela] == [1, 2, 3]


def test_dicionario_da_linha_inclui_o_saldo():
    linha = calcular_classificacao([ANA, BIA], [Resultado(1, 2, 4, 1)])[0].para_dict()
    assert linha["saldo"] == 3
    assert linha["nome"] == "Ana"
