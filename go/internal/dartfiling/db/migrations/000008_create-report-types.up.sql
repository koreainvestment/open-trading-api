CREATE TABLE IF NOT EXISTS report_types (
  id                   BIGSERIAL PRIMARY KEY,
  name                 VARCHAR(255) NOT NULL,
  structure            JSONB NOT NULL,
  source_raw_report_id BIGINT NOT NULL,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);