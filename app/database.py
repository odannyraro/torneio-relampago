"""Acesso ao banco SQLite: conexão por requisição e criação do esquema."""
import sqlite3
from pathlib import Path

from flask import current_app, g

CAMINHO_ESQUEMA = Path(__file__).with_name("schema.sql")


def conectar(caminho):
    """Abre uma conexão SQLite com linhas acessíveis por nome e chaves estrangeiras ativas."""
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Rows
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_tabelas(conexao):
    """Cria as tabelas (se ainda não existirem) a partir do arquivo schema.sql."""
    conexao.executescript(CAMINHO_ESQUEMA.read_text(encoding="utf-8"))
    conexao.commit()


def get_db():
    """Devolve a conexão da requisição atual, abrindo-a na primeira chamada."""
    if "db" not in g:
        g.db = conectar(current_app.config["DATABASE"])
    return g.db


def fechar_db(_erro=None):
    """Fecha a conexão ao final da requisição."""
    conexao = g.pop("db", None)
    if conexao is not None:
        conexao.close()


def init_app(app):
    """Registra o ciclo de vida do banco na aplicação e garante que o esquema existe."""
    caminho = app.config["DATABASE"]
    if caminho != ":memory:":
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(fechar_db)
    with app.app_context():
        criar_tabelas(get_db())
