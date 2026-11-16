"""Repositório do torneio: consultas e comandos SQL sobre torneios, participantes e partidas.

Os métodos NÃO fazem commit; quem controla a transação é a camada de serviço.
"""


class TorneioRepository:
    """Encapsula o acesso ao SQLite para a camada de serviço."""

    # Mapeia o lado da partida (1 ou 2) para a coluna correspondente (valores fixos, sem SQL injection).
    _COLUNA_DO_LADO = {1: "participante1_id", 2: "participante2_id"}

    def __init__(self, conexao):
        self._conexao = conexao

    # ------------------------------------------------------------ torneios
    def criar_torneio(self, nome, jogo, formato, ida_e_volta, chave_hash=None):
        cursor = self._conexao.execute(
            "INSERT INTO torneios (nome, jogo, formato, ida_e_volta, chave_hash) VALUES (?, ?, ?, ?, ?)",
            (nome, jogo, formato, int(ida_e_volta), chave_hash),
        )
        return cursor.lastrowid

    def buscar_torneio(self, torneio_id):
        return self._conexao.execute(
            "SELECT * FROM torneios WHERE id = ?", (torneio_id,)
        ).fetchone()

    def listar_torneios(self):
        return self._conexao.execute("SELECT * FROM torneios ORDER BY id DESC").fetchall()

    def excluir_torneio(self, torneio_id):
        """Apaga o torneio e tudo que depende dele. Devolve True se algo foi removido."""
        self._conexao.execute("DELETE FROM partidas WHERE torneio_id = ?", (torneio_id,))
        self._conexao.execute("DELETE FROM participantes WHERE torneio_id = ?", (torneio_id,))
        cursor = self._conexao.execute("DELETE FROM torneios WHERE id = ?", (torneio_id,))
        return cursor.rowcount > 0

    def definir_chave(self, torneio_id, chave_hash):
        self._conexao.execute("UPDATE torneios SET chave_hash = ? WHERE id = ?", (chave_hash, torneio_id))

    # -------------------------------------------------------- participantes
    def adicionar_participantes(self, torneio_id, nomes):
        """Insere os participantes na ordem recebida e devolve os ids na mesma ordem."""
        ids = []
        for ordem, nome in enumerate(nomes):
            cursor = self._conexao.execute(
                "INSERT INTO participantes (torneio_id, nome, ordem) VALUES (?, ?, ?)",
                (torneio_id, nome, ordem),
            )
            ids.append(cursor.lastrowid)
        return ids

    def listar_participantes(self, torneio_id):
        return self._conexao.execute(
            "SELECT * FROM participantes WHERE torneio_id = ? ORDER BY ordem", (torneio_id,)
        ).fetchall()

    # ------------------------------------------------------------- partidas
    def criar_partida(
        self, torneio_id, rodada, posicao, participante1_id, participante2_id,
        eh_bye=False, vencedor_id=None,
    ):
        cursor = self._conexao.execute(
            """INSERT INTO partidas
               (torneio_id, rodada, posicao, participante1_id, participante2_id, eh_bye, vencedor_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (torneio_id, rodada, posicao, participante1_id, participante2_id, int(eh_bye), vencedor_id),
        )
        return cursor.lastrowid

    def listar_partidas(self, torneio_id):
        return self._conexao.execute(
            "SELECT * FROM partidas WHERE torneio_id = ? ORDER BY rodada, posicao", (torneio_id,)
        ).fetchall()

    def buscar_partida(self, torneio_id, partida_id):
        return self._conexao.execute(
            "SELECT * FROM partidas WHERE id = ? AND torneio_id = ?", (partida_id, torneio_id)
        ).fetchone()

    def buscar_partida_por_posicao(self, torneio_id, rodada, posicao):
        return self._conexao.execute(
            "SELECT * FROM partidas WHERE torneio_id = ? AND rodada = ? AND posicao = ?",
            (torneio_id, rodada, posicao),
        ).fetchone()

    def definir_participante(self, partida_id, lado, participante_id):
        """Coloca um participante no lado 1 ou 2 de uma partida (usado quando o vencedor avança)."""
        coluna = self._COLUNA_DO_LADO[lado]
        self._conexao.execute(
            f"UPDATE partidas SET {coluna} = ? WHERE id = ?", (participante_id, partida_id)
        )

    def salvar_resultado(self, partida_id, placar1, placar2, vencedor_id):
        self._conexao.execute(
            "UPDATE partidas SET placar1 = ?, placar2 = ?, vencedor_id = ? WHERE id = ?",
            (placar1, placar2, vencedor_id, partida_id),
        )
