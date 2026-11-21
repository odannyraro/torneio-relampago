"""Acesso ao banco SQLite: conexão por requisição e criação do esquema."""
import sqlite3
from pathlib import Path

from flask import current_app, g

CAMINHO_ESQUEMA = Path(__file__).with_name("schema.sql")


def conectar(caminho):
    """Abre uma conexão SQLite com linhas acessíveis por nome e chaves estrangeiras ativas."""
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
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


def _colunas(conexao, tabela):
    return {linha["name"] for linha in conexao.execute(f"PRAGMA table_info({tabela})")}


def migrar(conexao):
    """Ajustes de esquema para bancos já existentes (seguro de rodar várias vezes)."""
    migracoes = (
        ("chave_hash", "TEXT"),
        ("pontos_vitoria", "INTEGER NOT NULL DEFAULT 3 CHECK (pontos_vitoria > 0)"),
        (
            "pontos_empate",
            "INTEGER NOT NULL DEFAULT 1 "
            "CHECK (pontos_empate >= 0 AND pontos_empate < pontos_vitoria)",
        ),
    )
    for coluna, definicao in migracoes:
        if coluna in _colunas(conexao, "torneios"):
            continue
        try:
            conexao.execute(f"ALTER TABLE torneios ADD COLUMN {coluna} {definicao}")
            conexao.commit()
        except sqlite3.OperationalError:
            # Outro worker pode ter feito o mesmo ao mesmo tempo; só ignore se a coluna já existe.
            if coluna not in _colunas(conexao, "torneios"):
                raise


def init_app(app):
    """Registra o ciclo de vida do banco na aplicação e garante que o esquema existe."""
    caminho = app.config["DATABASE"]
    if caminho != ":memory:":
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(fechar_db)
    with app.app_context():
        criar_tabelas(get_db())
        migrar(get_db())
