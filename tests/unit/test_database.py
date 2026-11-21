"""Testes de criação e migração do esquema SQLite."""
from app.database import migrar


def test_migracao_adiciona_pontuacoes_a_bancos_existentes(conexao):
    conexao.execute("DROP TABLE torneios")
    conexao.execute(
        "CREATE TABLE torneios (id INTEGER PRIMARY KEY, chave_hash TEXT)"
    )
    conexao.execute(
        "INSERT INTO torneios (id, chave_hash) VALUES (1, NULL)"
    )

    migrar(conexao)
    migrar(conexao)

    torneio = conexao.execute(
        "SELECT pontos_vitoria, pontos_empate FROM torneios WHERE id = 1"
    ).fetchone()
    assert tuple(torneio) == (3, 1)
