"""Testes do comando de dados de demonstração."""
from app import create_app


def test_seed_demo_cria_torneios_somente_uma_vez(app):
    executor = app.test_cli_runner()
    assert "2 torneio(s)" in executor.invoke(args=["seed-demo"]).output
    assert "0 torneio(s)" in executor.invoke(args=["seed-demo"]).output


def test_app_com_seed_demo_ativo_ja_nasce_com_torneios(tmp_path):
    app = create_app({"DATABASE": str(tmp_path / "demo.db"), "TESTING": True, "SEED_DEMO": True})
    nomes = {t["nome"] for t in app.test_client().get("/api/torneios").get_json()}
    assert nomes == {"Copa do Fim de Semana", "Liga Kart"}
