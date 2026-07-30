ALTER TABLE companies ADD COLUMN category VARCHAR(8) DEFAULT 'E';

UPDATE companies SET category = 'Y';
UPDATE companies SET category = 'E' WHERE corp_name LIKE '%전문회사';
UPDATE companies SET category = 'E' WHERE corp_name LIKE '%유한회사';
UPDATE companies SET category = 'E' WHERE corp_name LIKE '%펀드';