-- DataNest Migration 013: Complete MTG03 Remaining Fields
-- Phase 2C: Add 46 missing MTG03 fields for 100% third mortgage completion
-- Engineer: Master Database Engineer
-- Date: June 27, 2025
-- Objective: Complete MTG03 category (6 → 52 fields) - THIRD MORTGAGE INTELLIGENCE

-- TRIPLE-LOCK STEP 2: UPDATE FOUNDATION
-- Adding 46 missing MTG03 fields for complete third mortgage intelligence
-- ENHANCED QA: Proper data type handling, zero data loss approach

SET search_path TO datnest, public;

-- Add missing MTG03 adjustable rate fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_adjustable_rate_index VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_adjustable_rate_rider VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_change_index VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_first_change_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_first_change_period VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_interest_only_period VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_interest_rate_not_greater_than DECIMAL(5,3);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_interest_rate_not_less_than DECIMAL(5,3);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_maximum_interest_rate DECIMAL(5,3);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_rate_change_frequency VARCHAR(50);

-- Add missing MTG03 lender information fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_assigned_lender_name VARCHAR(255);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_lender_name VARCHAR(255);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_lender_type VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_lender_mail_city VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_lender_mail_full_street_address VARCHAR(255);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_lender_mail_state VARCHAR(10);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_lender_mail_unit VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_lender_mail_zip_code VARCHAR(10);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_lender_mail_zip_plus4code VARCHAR(4);

-- Add missing MTG03 loan details fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_loan_number VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_loan_term_months INTEGER;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_loan_term_years INTEGER;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_purpose_of_loan VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_type_financing VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_due_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_original_date_of_contract DATE;

-- Add missing MTG03 assignment and transfer fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_assignment_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_number_of_assignments INTEGER;

-- Add missing MTG03 estimated amounts and rates
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_curr_est_int_rate DECIMAL(5,3);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_est_monthly_interest DECIMAL(10,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_est_monthly_pi DECIMAL(10,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_est_monthly_principal DECIMAL(10,2);

-- Add missing MTG03 loan type and status fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_cash_purchase VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_construction_loan VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_equity_credit_line VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_purchase_mtg_ind VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_standalone_refi VARCHAR(50);

-- Add missing MTG03 rider and prepayment fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_prepayment_rider VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_prepayment_term_penalty_rider VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_fixed_step_conversion_rate_rider VARCHAR(100);

-- Add missing MTG03 pre-foreclosure fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_prefcl_auction_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_prefcl_case_trustee_sale_nbr VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_prefcl_filing_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_prefcl_recording_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_preforeclosure_status VARCHAR(100);

-- Add missing MTG03 title company field
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg03_title_company_name VARCHAR(255);

-- Add comments for documentation
COMMENT ON COLUMN properties.mtg03_adjustable_rate_index IS 'Third mortgage adjustable rate index reference';
COMMENT ON COLUMN properties.mtg03_adjustable_rate_rider IS 'Third mortgage adjustable rate rider type';
COMMENT ON COLUMN properties.mtg03_lender_name IS 'Third mortgage primary lender name';
COMMENT ON COLUMN properties.mtg03_lender_type IS 'Third mortgage lender classification type';
COMMENT ON COLUMN properties.mtg03_loan_number IS 'Third mortgage loan identification number';
COMMENT ON COLUMN properties.mtg03_purpose_of_loan IS 'Third mortgage purpose/use of loan proceeds';
COMMENT ON COLUMN properties.mtg03_type_financing IS 'Third mortgage financing type classification';
COMMENT ON COLUMN properties.mtg03_title_company_name IS 'Third mortgage title company name';

-- Migration complete
SELECT 'Migration 013: Added 46 MTG03 fields for complete third mortgage intelligence' AS status; 