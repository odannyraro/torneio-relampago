"""Fixtures compartilhadas pelos testes de unidade (banco em memória ou arquivo temporário)."""
import random

import pytest

from app import create_app
from app.database import conectar, criar_tabelas
from app.services.torneio_service import TorneioService


@pytest.fixture
def conexao():
    """Banco SQLite em memória, novo a cada teste (isolamento total)."""
    conn = conectar(":memory:")
    criar_tabelas(conn)
    yield conn
    conn.close()


@pytest.fixture
def servico(conexao):
    """Serviço com sorteio previsível (semente fixa)."""
    return TorneioService(conexao, sorteio=random.Random(1))


@pytest.fixture
def app(tmp_path):
    """Aplicação Flask apontando para um arquivo SQLite temporário."""
    return create_app({"DATABASE": str(tmp_path / "teste.db"), "TESTING": True})


@pytest.fixture
def client(app):
    """Cliente HTTP de teste (não precisa subir servidor)."""
    return app.test_client()
