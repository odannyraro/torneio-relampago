-- Esquema do banco de dados do Torneio Relâmpago (SQLite).
-- O status do torneio e a classificação NÃO são armazenados: são derivados
-- das partidas, o que evita dados inconsistentes.

CREATE TABLE IF NOT EXISTS torneios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL,
    jogo        TEXT    NOT NULL DEFAULT '',
    formato     TEXT    NOT NULL CHECK (formato IN ('mata_mata', 'pontos_corridos')),
    ida_e_volta INTEGER NOT NULL DEFAULT 0,
    pontos_vitoria INTEGER NOT NULL DEFAULT 3 CHECK (pontos_vitoria > 0),
    pontos_empate INTEGER NOT NULL DEFAULT 1
        CHECK (pontos_empate >= 0 AND pontos_empate < pontos_vitoria),
    chave_hash  TEXT,
    criado_em   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS participantes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    torneio_id  INTEGER NOT NULL REFERENCES torneios (id),
    nome        TEXT    NOT NULL,
    ordem       INTEGER NOT NULL,                       -- posição no sorteio/cabeça de chave
    UNIQUE (torneio_id, nome COLLATE NOCASE)            -- sem nomes repetidos no mesmo torneio
);

CREATE TABLE IF NOT EXISTS partidas (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    torneio_id        INTEGER NOT NULL REFERENCES torneios (id),
    rodada            INTEGER NOT NULL,
    posicao           INTEGER NOT NULL,                 -- posição da partida dentro da rodada
    participante1_id  INTEGER REFERENCES participantes (id),   -- NULL = ainda a definir
    participante2_id  INTEGER REFERENCES participantes (id),
    placar1           INTEGER CHECK (placar1 IS NULL OR placar1 >= 0),
    placar2           INTEGER CHECK (placar2 IS NULL OR placar2 >= 0),
    vencedor_id       INTEGER REFERENCES participantes (id),   -- NULL em empate ou sem resultado
    eh_bye            INTEGER NOT NULL DEFAULT 0,       -- 1 = avanço direto por folga
    UNIQUE (torneio_id, rodada, posicao)
);

CREATE INDEX IF NOT EXISTS idx_partidas_torneio ON partidas (torneio_id);
CREATE INDEX IF NOT EXISTS idx_participantes_torneio ON participantes (torneio_id);
