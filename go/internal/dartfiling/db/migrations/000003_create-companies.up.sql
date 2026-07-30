CREATE TABLE IF NOT EXISTS companies (
  id                 BIGSERIAL PRIMARY KEY,
  corp_code          VARCHAR(64) UNIQUE NOT NULL,
  corp_name          VARCHAR(255) NOT NULL,
  corp_eng_name      VARCHAR(255) NOT NULL,
  last_modified_date DATE NOT NULL,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);