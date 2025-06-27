-- DataNest Migration 012: Complete MTG02 Remaining Fields
-- Phase 2B: Add 38 missing MTG02 fields for 100% second mortgage completion
-- Engineer: Master Database Engineer
-- Date: June 27, 2025
-- Objective: Complete MTG02 category (14 → 52 fields) - SECOND MORTGAGE DOMINATION

-- TRIPLE-LOCK STEP 2: UPDATE FOUNDATION
-- Adding 38 missing MTG02 fields for complete second mortgage intelligence

SET search_path TO datnest, public;

-- Add missing MTG02 adjustable rate fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_adjustable_rate_index VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_adjustable_rate_rider VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_change_index VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_first_change_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_first_change_period VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_rate_change_frequency VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_interest_rate_not_greater_than DECIMAL(8,4);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_interest_rate_not_less_than DECIMAL(8,4);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_maximum_interest_rate DECIMAL(8,4);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_interest_only_period VARCHAR(50);

-- Add missing MTG02 lender and assignment fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_assigned_lender_name VARCHAR(200);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_assignment_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_number_of_assignments INTEGER;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_lender_name VARCHAR(200);

-- Add missing MTG02 lender mailing address fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_lender_mail_city VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_lender_mail_full_street_address VARCHAR(200);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_lender_mail_state VARCHAR(10);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_lender_mail_unit VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_lender_mail_zip_code VARCHAR(20);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_lender_mail_zip_plus4code VARCHAR(20);

-- Add missing MTG02 financial calculation fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_curr_est_int_rate DECIMAL(8,4);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_est_monthly_interest DECIMAL(10,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_est_monthly_pi DECIMAL(10,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_est_monthly_principal DECIMAL(10,2);

-- Add missing MTG02 loan type and purpose fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_cash_purchase VARCHAR(10);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_construction_loan VARCHAR(10);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_equity_credit_line VARCHAR(10);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_purchase_mtg_ind VARCHAR(10);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_standalone_refi VARCHAR(10);

-- Add missing MTG02 prepayment and rider fields  
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_prepayment_rider VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_prepayment_term_penalty_rider VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_fixed_step_conversion_rate_rider VARCHAR(100);

-- Add missing MTG02 foreclosure fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_preforeclosure_status VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_prefcl_recording_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_prefcl_filing_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_prefcl_case_trustee_sale_nbr VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_prefcl_auction_date DATE;

-- Add missing MTG02 title company field
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_title_company_name VARCHAR(200);

-- Add comments for field documentation
COMMENT ON COLUMN properties.mtg02_adjustable_rate_index IS 'Second mortgage adjustable rate index reference';
COMMENT ON COLUMN properties.mtg02_adjustable_rate_rider IS 'Second mortgage adjustable rate rider details';
COMMENT ON COLUMN properties.mtg02_change_index IS 'Second mortgage rate change index specification';
COMMENT ON COLUMN properties.mtg02_first_change_date IS 'Second mortgage first rate change date';
COMMENT ON COLUMN properties.mtg02_first_change_period IS 'Second mortgage first rate change period';
COMMENT ON COLUMN properties.mtg02_rate_change_frequency IS 'Second mortgage rate change frequency';
COMMENT ON COLUMN properties.mtg02_interest_rate_not_greater_than IS 'Second mortgage maximum interest rate cap';
COMMENT ON COLUMN properties.mtg02_interest_rate_not_less_than IS 'Second mortgage minimum interest rate floor';
COMMENT ON COLUMN properties.mtg02_maximum_interest_rate IS 'Second mortgage absolute maximum interest rate';
COMMENT ON COLUMN properties.mtg02_interest_only_period IS 'Second mortgage interest-only payment period';
COMMENT ON COLUMN properties.mtg02_assigned_lender_name IS 'Second mortgage assigned lender name';
COMMENT ON COLUMN properties.mtg02_assignment_date IS 'Second mortgage assignment date';
COMMENT ON COLUMN properties.mtg02_number_of_assignments IS 'Second mortgage total number of assignments';
COMMENT ON COLUMN properties.mtg02_lender_name IS 'Second mortgage lender name (alternative field)';
COMMENT ON COLUMN properties.mtg02_lender_mail_city IS 'Second mortgage lender mailing address city';
COMMENT ON COLUMN properties.mtg02_lender_mail_full_street_address IS 'Second mortgage lender complete mailing street address';
COMMENT ON COLUMN properties.mtg02_lender_mail_state IS 'Second mortgage lender mailing address state';
COMMENT ON COLUMN properties.mtg02_lender_mail_unit IS 'Second mortgage lender mailing address unit';
COMMENT ON COLUMN properties.mtg02_lender_mail_zip_code IS 'Second mortgage lender mailing address ZIP code';
COMMENT ON COLUMN properties.mtg02_lender_mail_zip_plus4code IS 'Second mortgage lender mailing address ZIP+4 code';
COMMENT ON COLUMN properties.mtg02_curr_est_int_rate IS 'Second mortgage current estimated interest rate';
COMMENT ON COLUMN properties.mtg02_est_monthly_interest IS 'Second mortgage estimated monthly interest payment';
COMMENT ON COLUMN properties.mtg02_est_monthly_pi IS 'Second mortgage estimated monthly principal and interest';
COMMENT ON COLUMN properties.mtg02_est_monthly_principal IS 'Second mortgage estimated monthly principal payment';
COMMENT ON COLUMN properties.mtg02_cash_purchase IS 'Second mortgage cash purchase indicator';
COMMENT ON COLUMN properties.mtg02_construction_loan IS 'Second mortgage construction loan indicator';
COMMENT ON COLUMN properties.mtg02_equity_credit_line IS 'Second mortgage equity credit line indicator';
COMMENT ON COLUMN properties.mtg02_purchase_mtg_ind IS 'Second mortgage purchase mortgage indicator';
COMMENT ON COLUMN properties.mtg02_standalone_refi IS 'Second mortgage standalone refinance indicator';
COMMENT ON COLUMN properties.mtg02_prepayment_rider IS 'Second mortgage prepayment rider details';
COMMENT ON COLUMN properties.mtg02_prepayment_term_penalty_rider IS 'Second mortgage prepayment penalty rider';
COMMENT ON COLUMN properties.mtg02_fixed_step_conversion_rate_rider IS 'Second mortgage fixed step conversion rate rider';
COMMENT ON COLUMN properties.mtg02_preforeclosure_status IS 'Second mortgage pre-foreclosure status';
COMMENT ON COLUMN properties.mtg02_prefcl_recording_date IS 'Second mortgage pre-foreclosure recording date';
COMMENT ON COLUMN properties.mtg02_prefcl_filing_date IS 'Second mortgage pre-foreclosure filing date';
COMMENT ON COLUMN properties.mtg02_prefcl_case_trustee_sale_nbr IS 'Second mortgage pre-foreclosure case/trustee sale number';
COMMENT ON COLUMN properties.mtg02_prefcl_auction_date IS 'Second mortgage pre-foreclosure auction date';
COMMENT ON COLUMN properties.mtg02_title_company_name IS 'Second mortgage title company name';

-- Create indexes for performance on key fields
CREATE INDEX IF NOT EXISTS idx_mtg02_first_change_date ON properties(mtg02_first_change_date) WHERE mtg02_first_change_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_mtg02_assignment_date ON properties(mtg02_assignment_date) WHERE mtg02_assignment_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_mtg02_lender_mail_city ON properties(mtg02_lender_mail_city) WHERE mtg02_lender_mail_city IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_mtg02_lender_name ON properties(mtg02_lender_name) WHERE mtg02_lender_name IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_mtg02_title_company ON properties(mtg02_title_company_name) WHERE mtg02_title_company_name IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_mtg02_preforeclosure_status ON properties(mtg02_preforeclosure_status) WHERE mtg02_preforeclosure_status IS NOT NULL;

-- Verification query
SELECT 
    COUNT(*) as total_columns,
    COUNT(CASE WHEN column_name LIKE 'mtg02_%' THEN 1 END) as mtg02_columns
FROM information_schema.columns 
WHERE table_name = 'properties' 
  AND table_schema = 'datnest'; 