"""Testes das rotas web e da API JSON, usando o cliente de teste do Flask."""

FORMULARIO = {
    "nome": "Copa da Galera", "jogo": "FIFA", "formato": "mata_mata",
    "participantes": "Ana\nBia\nCaio\nDuda",
}


def _criar_pelo_formulario(client, **alteracoes):
    return client.post("/torneios/novo", data={**FORMULARIO, **alteracoes})


def _criar_pela_api(client, **alteracoes):
    corpo = {"nome": "Copa", "jogo": "FIFA", "formato": "mata_mata",
             "participantes": ["Ana", "Bia", "Caio", "Duda"], "embaralhar": False}
    return client.post("/api/torneios", json={**corpo, **alteracoes})


# ------------------------------------------------------------------ páginas HTML
def test_pagina_inicial_sem_torneios_mostra_mensagem_amigavel(client):
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert "Nenhum torneio ainda" in resposta.get_data(as_text=True)


def test_formulario_de_novo_torneio_e_exibido(client):
    assert client.get("/torneios/novo").status_code == 200


def test_criar_torneio_pelo_formulario_redireciona_para_a_pagina_dele(client):
    resposta = _criar_pelo_formulario(client)
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/torneios/1")


def test_chave_de_edicao_e_opcional_na_criacao(client):
    formulario = client.get("/torneios/novo").get_data(as_text=True)
    assert 'name="proteger_com_chave"' in formulario
    assert 'id="chave" name="chave" type="password"' in formulario

    _criar_pelo_formulario(client)
    pagina = client.get("/torneios/1").get_data(as_text=True)
    assert 'data-testid="chave-desbloqueio"' not in pagina
    assert 'data-testid="excluir-torneio"' in pagina


def test_torneio_protegido_exige_chave_antes_de_liberar_edicao(client):
    resposta = _criar_pelo_formulario(
        client, proteger_com_chave="on", chave="segredo"
    )
    assert resposta.status_code == 302
    pagina = client.get("/torneios/1").get_data(as_text=True)
    assert 'data-testid="chave-desbloqueio"' in pagina
    assert 'data-testid="excluir-torneio"' not in pagina

    client.post("/torneios/1/desbloquear", data={"chave": "incorreta"})
    pagina = client.get("/torneios/1").get_data(as_text=True)
    assert 'data-testid="chave-desbloqueio"' in pagina

    client.post("/torneios/1/desbloquear", data={"chave": "segredo"})
    pagina = client.get("/torneios/1").get_data(as_text=True)
    assert 'data-testid="chave-desbloqueio"' not in pagina
    assert 'data-testid="excluir-torneio"' in pagina


def test_chave_marcada_sem_valor_nao_cria_torneio(client):
    resposta = _criar_pelo_formulario(client, proteger_com_chave="on")
    assert resposta.status_code == 400
    assert "pelo menos 4 caracteres" in resposta.get_data(as_text=True)


def test_pagina_do_torneio_mostra_a_chave(client):
    _criar_pelo_formulario(client, embaralhar="")
    html = client.get("/torneios/1").get_data(as_text=True)
    assert "Copa da Galera" in html and "Semifinal" in html and "Final" in html


def test_pagina_de_pontos_corridos_mostra_a_tabela(client):
    _criar_pelo_formulario(client, formato="pontos_corridos")
    assert 'data-testid="classificacao"' in client.get("/torneios/1").get_data(as_text=True)


def test_formulario_invalido_mostra_erro_e_preserva_os_dados(client):
    resposta = _criar_pelo_formulario(client, participantes="Ana")
    html = resposta.get_data(as_text=True)
    assert resposta.status_code == 400
    assert "pelo menos 2 participantes" in html
    assert 'value="Copa da Galera"' in html


def test_registrar_resultado_pelo_formulario(client):
    _criar_pelo_formulario(client)
    resposta = client.post("/torneios/1/partidas/1/resultado",
                           data={"placar1": "2", "placar2": "0"}, follow_redirects=True)
    assert "Resultado salvo" in resposta.get_data(as_text=True)


def test_resultado_invalido_mostra_mensagem_de_erro(client):
    _criar_pelo_formulario(client)
    resposta = client.post("/torneios/1/partidas/1/resultado",
                           data={"placar1": "abc", "placar2": "0"}, follow_redirects=True)
    assert "números inteiros" in resposta.get_data(as_text=True)


def test_excluir_torneio_pelo_site(client):
    _criar_pelo_formulario(client)
    resposta = client.post("/torneios/1/excluir", follow_redirects=True)
    assert "Torneio excluído" in resposta.get_data(as_text=True)
    assert client.get("/torneios/1").status_code == 404


def test_torneio_inexistente_mostra_pagina_404(client):
    resposta = client.get("/torneios/123")
    assert resposta.status_code == 404
    assert "Torneio não encontrado" in resposta.get_data(as_text=True)


def test_rota_de_saude_responde_ok(client):
    assert client.get("/saude").get_json() == {"status": "ok"}


# --------------------------------------------------------------------- API JSON
def test_api_cria_e_consulta_um_torneio(client):
    criado = _criar_pela_api(client)
    assert criado.status_code == 201
    consultado = client.get(f"/api/torneios/{criado.get_json()['id']}").get_json()
    assert consultado["nome"] == "Copa"
    assert len(consultado["partidas"]) == 3


def test_api_torneio_com_chave_exige_chave_para_registrar_resultado(client):
    criado = _criar_pela_api(client, chave="segredo")
    assert criado.status_code == 201

    url = "/api/torneios/1/partidas/1/resultado"
    dados = {"placar1": 2, "placar2": 0}
    assert client.post(url, json=dados).status_code == 403
    assert client.post(url, json=dados, headers={"X-Chave-Torneio": "segredo"}).status_code == 200


def test_api_lista_os_torneios(client):
    _criar_pela_api(client)
    assert [t["nome"] for t in client.get("/api/torneios").get_json()] == ["Copa"]


def test_api_registra_resultado_e_devolve_o_torneio_atualizado(client):
    _criar_pela_api(client)
    resposta = client.post("/api/torneios/1/partidas/1/resultado", json={"placar1": 3, "placar2": 1})
    final = next(p for p in resposta.get_json()["partidas"] if p["rodada"] == 2)
    assert final["nome1"] == "Ana"


def test_api_devolve_400_com_mensagem_quando_os_dados_sao_invalidos(client):
    resposta = _criar_pela_api(client, participantes=["Ana"])
    assert resposta.status_code == 400
    assert "pelo menos 2" in resposta.get_json()["erro"]


def test_api_devolve_404_em_json_para_torneio_inexistente(client):
    resposta = client.get("/api/torneios/99")
    assert resposta.status_code == 404
    assert resposta.get_json()["erro"] == "Torneio não encontrado."
