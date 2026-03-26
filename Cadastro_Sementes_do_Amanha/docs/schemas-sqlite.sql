-- docs/schema.sqlite.sql
-- Cadastro Sementes do Amanhã - Esquema SQLite (DEV)
-- Observação: SQLite não suporta ENUM/COMMENT ON; Enums são representados por CHECK constraints.

PRAGMA foreign_keys = ON;

-- ==========================
-- TABELA: atendidos
-- ==========================
CREATE TABLE IF NOT EXISTS atendidos (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  nome             TEXT        NOT NULL,
  data_nascimento  DATE        NOT NULL,

  -- ENUM: 'Menina' | 'Menino'
  genero           TEXT        CHECK (genero IN ('Menina','Menino')),

  unidade          TEXT        NOT NULL,

  -- ENUM: 'Manhã' | 'Tarde'
  periodo          TEXT        NOT NULL CHECK (periodo IN ('Manhã','Tarde')),

  turma            TEXT,  -- calculada pela regra de idade (ex.: 'Turma 10–12')

  escola           TEXT,
  bairro           TEXT,

  data_matricula   DATE        NOT NULL DEFAULT (date('now')),

  -- ENUM: 'Ativo' | 'Desativado' | 'Lista de espera'
  situacao         TEXT        NOT NULL CHECK (situacao IN ('Ativo','Desativado','Lista de espera')) DEFAULT 'Ativo',

  motivo_desligamento TEXT
);

-- Índices úteis para filtros
CREATE INDEX IF NOT EXISTS ix_atendidos_turma     ON atendidos (turma);
CREATE INDEX IF NOT EXISTS ix_atendidos_situacao  ON atendidos (situacao);
CREATE INDEX IF NOT EXISTS ix_atendidos_unidade   ON atendidos (unidade);
CREATE INDEX IF NOT EXISTS ix_atendidos_periodo   ON atendidos (periodo);
CREATE INDEX IF NOT EXISTS ix_atendidos_genero    ON atendidos (genero);

-- ==========================
-- TABELA: transportes (1:1 com atendidos)
-- ==========================
CREATE TABLE IF NOT EXISTS transportes (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  atendido_id   INTEGER NOT NULL UNIQUE, -- 1:1 (um registro por atendido)

  -- ENUM: 'Sim' | 'Não' | 'Lista de espera'
  utiliza_van   TEXT    CHECK (utiliza_van IN ('Sim','Não','Lista de espera')),

  endereco_rota TEXT,
  observacoes   TEXT,

  FOREIGN KEY (atendido_id) REFERENCES atendidos (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_transportes_utiliza_van ON transportes (utiliza_van);

-- ==========================
-- TABELA: frequencias (1:N com atendidos)
-- ==========================
CREATE TABLE IF NOT EXISTS frequencias (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  atendido_id  INTEGER NOT NULL,
  data         DATE    NOT NULL,

  -- ENUM: 'Presença' | 'Falta'
  status       TEXT    NOT NULL CHECK (status IN ('Presença','Falta')),

  -- Impede duplicidade (um registro por atendido por data)
  CONSTRAINT uq_freq_atendido_data UNIQUE (atendido_id, data),

  FOREIGN KEY (atendido_id) REFERENCES atendidos (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_frequencias_data ON frequencias (data);

-- ==========================
-- NOTAS:
-- - Regras de negócio:
--   * turma é calculada pela idade no backend.
--   * se 'situacao' = 'Desativado', o backend exige 'motivo_desligamento'.
--   * frequencias é idempotente por (atendido_id, data).
-- - Para recriar em DEV: apagar o arquivo sementes.db e subir a API.