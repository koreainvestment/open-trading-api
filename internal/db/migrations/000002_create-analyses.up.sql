CREATE TABLE IF NOT EXISTS analyses (
  id              BIGSERIAL PRIMARY KEY,
  raw_report_id   BIGINT NOT NULL,
  analysis        JSONB NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);