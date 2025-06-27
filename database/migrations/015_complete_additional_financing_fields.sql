-- DataNest Migration 015: Complete Additional Financing Fields
-- Phase 2E: Add 12 final additional financing fields for 100% financing completion
-- Engineer: Master Database Engineer
-- Date: June 27, 2025
-- Objective: Complete Additional Financing category - ACHIEVE 100% FINANCING INTELLIGENCE

-- TRIPLE-LOCK STEP 2: UPDATE FOUNDATION
-- Adding 12 final additional financing fields for complete financing intelligence
-- ENHANCED QA: Proper data type handling, zero data loss approach

SET search_path TO datnest, public;

-- Add Purchase LTV field (fix precision issue from before)
ALTER TABLE properties ADD COLUMN IF NOT EXISTS purchase_ltv DECIMAL(10,3);

-- Add purchase and financing indicator fields
ALTER TABLE properties ADD COLUMN IF NOT EXISTS purchase_money_mortgage VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS cash_purchase_flag VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS construction_loan_flag VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS owner_financed_flag VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS seller_financed_flag VARCHAR(50);

-- Add loan characteristic flags
ALTER TABLE properties ADD COLUMN IF NOT EXISTS assumable_loan_flag VARCHAR(50);

-- Add distress sale and transaction type flags
ALTER TABLE properties ADD COLUMN IF NOT EXISTS foreclosure_flag VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS reo_flag VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS short_sale_flag VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS estate_sale_flag VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS bankruptcy_flag VARCHAR(50);

-- Add comments for documentation
COMMENT ON COLUMN properties.purchase_ltv IS 'Purchase loan-to-value ratio (fixed precision)';
COMMENT ON COLUMN properties.purchase_money_mortgage IS 'Purchase money mortgage indicator';
COMMENT ON COLUMN properties.cash_purchase_flag IS 'Cash purchase transaction flag';
COMMENT ON COLUMN properties.construction_loan_flag IS 'Construction loan indicator flag';
COMMENT ON COLUMN properties.owner_financed_flag IS 'Owner financing indicator flag';
COMMENT ON COLUMN properties.seller_financed_flag IS 'Seller financing indicator flag';
COMMENT ON COLUMN properties.assumable_loan_flag IS 'Assumable loan characteristic flag';
COMMENT ON COLUMN properties.foreclosure_flag IS 'Foreclosure transaction indicator';
COMMENT ON COLUMN properties.reo_flag IS 'Real estate owned (REO) transaction flag';
COMMENT ON COLUMN properties.short_sale_flag IS 'Short sale transaction indicator';
COMMENT ON COLUMN properties.estate_sale_flag IS 'Estate sale transaction indicator';
COMMENT ON COLUMN properties.bankruptcy_flag IS 'Bankruptcy related transaction flag';

-- Migration complete
SELECT 'Migration 015: Added 12 additional financing fields for 100% financing intelligence' AS status; 