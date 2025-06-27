-- DataNest Migration 011: Complete MTG01 Remaining Fields
-- Phase 2A: Add 11 missing MTG01 fields for 100% primary mortgage completion
-- Engineer: Master Database Engineer
-- Date: June 27, 2025
-- Objective: Complete MTG01 category (41 → 52 fields)

-- TRIPLE-LOCK STEP 2: UPDATE FOUNDATION
-- Adding 11 missing MTG01 fields for complete primary mortgage intelligence

SET search_path TO datnest, public;

-- Add missing MTG01 adjustable rate fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg01_first_change_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg01_first_change_period VARCHAR(50);

-- Add missing MTG01 lender mailing address fields  
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg01_lender_mail_city VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg01_lender_mail_full_street_address VARCHAR(200);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg01_lender_mail_state VARCHAR(10);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg01_lender_mail_unit VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg01_lender_mail_zip_code VARCHAR(20);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg01_lender_mail_zip_plus4code VARCHAR(20);

-- Add missing MTG01 lender and title company fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg01_lender_name VARCHAR(200);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg01_title_company_name VARCHAR(200);

-- Add missing MTG01 rate rider field
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg01_fixed_step_conversion_rate_rider VARCHAR(100);

-- Add comments for field documentation
COMMENT ON COLUMN properties.mtg01_first_change_date IS 'Primary mortgage first rate change date for adjustable rate mortgages';
COMMENT ON COLUMN properties.mtg01_first_change_period IS 'Primary mortgage first rate change period specification';
COMMENT ON COLUMN properties.mtg01_lender_mail_city IS 'Primary mortgage lender mailing address city';
COMMENT ON COLUMN properties.mtg01_lender_mail_full_street_address IS 'Primary mortgage lender complete mailing street address';
COMMENT ON COLUMN properties.mtg01_lender_mail_state IS 'Primary mortgage lender mailing address state';
COMMENT ON COLUMN properties.mtg01_lender_mail_unit IS 'Primary mortgage lender mailing address unit number';
COMMENT ON COLUMN properties.mtg01_lender_mail_zip_code IS 'Primary mortgage lender mailing address ZIP code';
COMMENT ON COLUMN properties.mtg01_lender_mail_zip_plus4code IS 'Primary mortgage lender mailing address ZIP+4 code';
COMMENT ON COLUMN properties.mtg01_lender_name IS 'Primary mortgage lender name (alternative field)';
COMMENT ON COLUMN properties.mtg01_title_company_name IS 'Primary mortgage title company name';
COMMENT ON COLUMN properties.mtg01_fixed_step_conversion_rate_rider IS 'Primary mortgage fixed step conversion rate rider details';

-- Create indexes for performance on key fields
CREATE INDEX IF NOT EXISTS idx_mtg01_first_change_date ON properties(mtg01_first_change_date) WHERE mtg01_first_change_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_mtg01_lender_mail_city ON properties(mtg01_lender_mail_city) WHERE mtg01_lender_mail_city IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_mtg01_lender_name ON properties(mtg01_lender_name) WHERE mtg01_lender_name IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_mtg01_title_company ON properties(mtg01_title_company_name) WHERE mtg01_title_company_name IS NOT NULL;

-- Verification query
SELECT 
    COUNT(*) as total_columns,
    COUNT(CASE WHEN column_name LIKE 'mtg01_%' THEN 1 END) as mtg01_columns
FROM information_schema.columns 
WHERE table_name = 'properties' 
  AND table_schema = 'datnest'; 