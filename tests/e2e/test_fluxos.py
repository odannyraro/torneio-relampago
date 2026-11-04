"""Testes end-to-end: simulam um usuário usando o sistema no navegador."""
from playwright.sync_api import expect


def criar_torneio(pagina, servidor, nome, formato, participantes):
    """Preenche o formulário de novo torneio (sem sorteio, para o resultado ser previsível)."""
    pagina.goto(f"{servidor}/torneios/novo")
    pagina.fill("#nome", nome)
    pagina.check(f"input[value={formato}]")
    pagina.fill("#participantes", "\n".join(participantes))
    pagina.uncheck("input[name=embaralhar]")
    pagina.click("[data-testid=criar-torneio]")


def registrar_placar(pagina, partida_id, placar1, placar2):
    pagina.fill(f"[data-testid=placar1-{partida_id}]", str(placar1))
    pagina.fill(f"[data-testid=placar2-{partida_id}]", str(placar2))
    pagina.click(f"[data-testid=salvar-{partida_id}]")


def test_criar_mata_mata_com_numero_impar_mostra_chave_com_folgas(pagina, servidor):
    criar_torneio(pagina, servidor, "Copa Impar", "mata_mata", ["Ana", "Bia", "Caio", "Duda", "Eli"])

    expect(pagina.locator("[data-testid=nome-torneio]")).to_have_text("Copa Impar")
    expect(pagina.locator("[data-testid=rodada-1] h2")).to_have_text("Quartas de final")
    expect(pagina.get_by_text("Avança direto (folga)")).to_have_count(3)


def test_jogar_mata_mata_inteiro_ate_o_campeao(pagina, servidor):
    criar_torneio(pagina, servidor, "Copa Completa", "mata_mata", ["Ana", "Bia", "Caio", "Duda"])

    registrar_placar(pagina, 1, 2, 0)  # semifinal: Ana x Duda
    expect(pagina.locator("[data-testid=mensagem]")).to_contain_text("Resultado salvo")
    registrar_placar(pagina, 2, 1, 0)  # semifinal: Bia x Caio
    registrar_placar(pagina, 3, 3, 1)  # final: Ana x Bia

    expect(pagina.locator("[data-testid=campeao]")).to_contain_text("Ana")


def test_resultado_em_pontos_corridos_atualiza_a_tabela(pagina, servidor):
    criar_torneio(pagina, servidor, "Liga Trio", "pontos_corridos", ["Ana", "Bia", "Caio"])

    registrar_placar(pagina, 1, 2, 1)  # primeira partida da rodada 1: Bia x Caio

    lider = pagina.locator("[data-testid=linha-1]")
    expect(lider).to_contain_text("Bia")
    expect(lider.locator("td").nth(2)).to_have_text("3")


def test_formulario_com_um_participante_mostra_erro_e_mantem_os_dados(pagina, servidor):
    criar_torneio(pagina, servidor, "Copa Solo", "mata_mata", ["Ana"])

    expect(pagina.locator("[data-testid=mensagem]")).to_contain_text("pelo menos 2 participantes")
    expect(pagina.locator("#nome")).to_have_value("Copa Solo")


def test_excluir_torneio_remove_da_lista(pagina, servidor):
    criar_torneio(pagina, servidor, "Copa Efemera", "mata_mata", ["Ana", "Bia"])

    pagina.click("[data-testid=excluir-torneio]")

    expect(pagina.locator("[data-testid=mensagem]")).to_contain_text("Torneio excluído")
    expect(pagina.locator("[data-testid=sem-torneios]")).to_be_visible()
