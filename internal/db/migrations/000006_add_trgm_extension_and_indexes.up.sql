CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX trgm_idx_companies_corp_name ON companies USING GIST (corp_name gist_trgm_ops);
CREATE INDEX trgm_idx_companies_corp_eng_name ON companies USING GIST (corp_eng_name gist_trgm_ops);
