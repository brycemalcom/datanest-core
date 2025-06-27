-- MIGRATION: 009b_fix_missing_tax_delinquent_year
-- GOAL: Add the missing tax_delinquent_year column for complete County Values/Taxes mapping

ALTER TABLE datnest.properties
    ADD COLUMN IF NOT EXISTS tax_delinquent_year INTEGER;

-- Add performance index for tax delinquency analysis
CREATE INDEX IF NOT EXISTS idx_properties_tax_delinquent_year ON datnest.properties(tax_delinquent_year) WHERE tax_delinquent_year IS NOT NULL; 