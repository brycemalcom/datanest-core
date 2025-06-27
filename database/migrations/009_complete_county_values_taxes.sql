-- MIGRATION: 009_complete_county_values_taxes
-- GOAL: Add all 20 "County Values/Taxes" fields for complete financial assessment intelligence

ALTER TABLE datnest.properties
    -- Assessment Values
    ADD COLUMN IF NOT EXISTS assessed_improvement_value DECIMAL(15, 2),
    ADD COLUMN IF NOT EXISTS assessed_land_value DECIMAL(15, 2),
    ADD COLUMN IF NOT EXISTS assessment_year INTEGER,
    
    -- Market Values
    ADD COLUMN IF NOT EXISTS market_value_improvement DECIMAL(15, 2),
    ADD COLUMN IF NOT EXISTS market_value_land DECIMAL(15, 2),
    ADD COLUMN IF NOT EXISTS market_value_year INTEGER,
    ADD COLUMN IF NOT EXISTS total_market_value DECIMAL(15, 2),
    
    -- Tax Information
    ADD COLUMN IF NOT EXISTS tax_amount DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS tax_year INTEGER,
    ADD COLUMN IF NOT EXISTS tax_code_area VARCHAR(20),
    ADD COLUMN IF NOT EXISTS exemption_code VARCHAR(10),
    ADD COLUMN IF NOT EXISTS exemption_amount DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS california_homeowners_exemption DECIMAL(10, 2),
    
    -- Additional Assessment Details
    ADD COLUMN IF NOT EXISTS assessed_total_value DECIMAL(15, 2),
    ADD COLUMN IF NOT EXISTS homestead_exemption DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS senior_exemption DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS veteran_exemption DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS disability_exemption DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS agricultural_exemption DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS property_tax_delinquent_flag VARCHAR(1);

-- Add performance indexes for financial analysis queries
CREATE INDEX IF NOT EXISTS idx_properties_assessed_total ON datnest.properties(assessed_total_value) WHERE assessed_total_value IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_market_total ON datnest.properties(total_market_value) WHERE total_market_value IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_assessment_year ON datnest.properties(assessment_year) WHERE assessment_year IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_tax_amount ON datnest.properties(tax_amount) WHERE tax_amount IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_tax_delinquent ON datnest.properties(property_tax_delinquent_flag) WHERE property_tax_delinquent_flag IS NOT NULL;

-- Add documentation comments for financial intelligence
COMMENT ON COLUMN datnest.properties.assessed_improvement_value IS 'County assessed value for building improvements';
COMMENT ON COLUMN datnest.properties.assessed_land_value IS 'County assessed value for land only';
COMMENT ON COLUMN datnest.properties.market_value_improvement IS 'County market value for building improvements';
COMMENT ON COLUMN datnest.properties.market_value_land IS 'County market value for land only';
COMMENT ON COLUMN datnest.properties.california_homeowners_exemption IS 'California homeowner tax exemption amount';
COMMENT ON COLUMN datnest.properties.tax_amount IS 'Annual property tax amount'; 