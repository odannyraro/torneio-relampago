"""Fixtures dos testes end-to-end: sobem a aplicação de verdade e abrem um navegador (Playwright)."""
import threading

import pytest
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

from app import create_app


@pytest.fixture(scope="session")
def navegador():
    """Um único Chromium (sem janela) para toda a sessão de testes."""
    with sync_playwright() as playwright:
        chromium = playwright.chromium.launch()
        yield chromium
        chromium.close()


@pytest.fixture
def servidor(tmp_path):
    """Sobe o app em uma porta livre, com banco novo (estado conhecido) a cada teste."""
    app = create_app({"DATABASE": str(tmp_path / "e2e.db"), "TESTING": True})
    servidor_http = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=servidor_http.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{servidor_http.server_port}"
    servidor_http.shutdown()
    thread.join(timeout=5)


@pytest.fixture
def pagina(navegador):
    """Uma aba limpa do navegador, com tempo limite curto para falhar rápido."""
    contexto = navegador.new_context()
    aba = contexto.new_page()
    aba.set_default_timeout(5000)
    yield aba
    contexto.close()
