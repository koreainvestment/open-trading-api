CREATE TABLE IF NOT EXISTS raw_reports (
  id              BIGSERIAL PRIMARY KEY,
  receipt_number  VARCHAR(64) UNIQUE NOT NULL,
  corp_code       VARCHAR(64) NOT NULL,
  blob_data       BYTEA NOT NULL,
  blob_size       INTEGER NOT NULL,
  json_data       JSONB NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);