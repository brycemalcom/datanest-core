-- DataNest Migration 014: Complete MTG04 All Fields
-- Phase 2D: Add 52 MTG04 fields for 100% fourth mortgage completion
-- Engineer: Master Database Engineer
-- Date: June 27, 2025
-- Objective: Complete MTG04 category (0 → 52 fields) - FOURTH MORTGAGE INTELLIGENCE

-- TRIPLE-LOCK STEP 2: UPDATE FOUNDATION
-- Adding 52 MTG04 fields for complete fourth mortgage intelligence
-- ENHANCED QA: Proper data type handling, zero data loss approach

SET search_path TO datnest, public;

-- Add MTG04 core loan fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_loan_amount BIGINT;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_interest_rate DECIMAL(5,3);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_loan_type VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_lender_name_beneficiary VARCHAR(255);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_lender_name VARCHAR(255);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_lender_type VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_curr_est_bal BIGINT;

-- Add MTG04 loan terms and dates
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_loan_term_months INTEGER;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_loan_term_years INTEGER;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_original_date_of_contract DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_recording_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_due_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_assignment_date DATE;

-- Add MTG04 adjustable rate fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_adjustable_rate_index VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_adjustable_rate_rider VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_change_index VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_first_change_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_first_change_period VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_interest_only_period VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_curr_est_int_rate DECIMAL(5,3);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_interest_rate_not_greater_than DECIMAL(5,3);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_interest_rate_not_less_than DECIMAL(5,3);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_maximum_interest_rate DECIMAL(5,3);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_rate_change_frequency VARCHAR(50);

-- Add MTG04 lender mailing address fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_lender_mail_city VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_lender_mail_full_street_address VARCHAR(255);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_lender_mail_state VARCHAR(10);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_lender_mail_unit VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_lender_mail_zip_code VARCHAR(10);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_lender_mail_zip_plus4code VARCHAR(4);

-- Add MTG04 loan details and purpose fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_loan_number VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_purpose_of_loan VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_type_financing VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_assigned_lender_name VARCHAR(255);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_number_of_assignments INTEGER;

-- Add MTG04 estimated monthly payment fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_est_monthly_interest DECIMAL(10,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_est_monthly_pi DECIMAL(10,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_est_monthly_principal DECIMAL(10,2);

-- Add MTG04 loan type and status fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_cash_purchase VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_construction_loan VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_equity_credit_line VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_purchase_mtg_ind VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_standalone_refi VARCHAR(50);

-- Add MTG04 rider and prepayment fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_prepayment_rider VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_prepayment_term_penalty_rider VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_fixed_step_conversion_rate_rider VARCHAR(100);

-- Add MTG04 pre-foreclosure fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_prefcl_auction_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_prefcl_case_trustee_sale_nbr VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_prefcl_filing_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_prefcl_recording_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_preforeclosure_status VARCHAR(100);

-- Add MTG04 title company field
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg04_title_company_name VARCHAR(255);

-- Add comments for documentation
COMMENT ON COLUMN properties.mtg04_loan_amount IS 'Fourth mortgage loan amount';
COMMENT ON COLUMN properties.mtg04_interest_rate IS 'Fourth mortgage interest rate';
COMMENT ON COLUMN properties.mtg04_lender_name IS 'Fourth mortgage primary lender name';
COMMENT ON COLUMN properties.mtg04_lender_type IS 'Fourth mortgage lender classification type';
COMMENT ON COLUMN properties.mtg04_loan_number IS 'Fourth mortgage loan identification number';
COMMENT ON COLUMN properties.mtg04_purpose_of_loan IS 'Fourth mortgage purpose/use of loan proceeds';
COMMENT ON COLUMN properties.mtg04_type_financing IS 'Fourth mortgage financing type classification';
COMMENT ON COLUMN properties.mtg04_title_company_name IS 'Fourth mortgage title company name';

-- Migration complete
SELECT 'Migration 014: Added 52 MTG04 fields for complete fourth mortgage intelligence' AS status; 