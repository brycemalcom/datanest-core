-- DatNest Core Platform - Customer Priority Fields Migration
-- Migration: 002_customer_priority_fields.sql
-- Adds 24 customer priority fields + intelligent land use code system

-- Set schema
SET search_path TO datnest, public;

-- =====================================================
-- LAND USE CODES LOOKUP TABLE
-- =====================================================
CREATE TABLE land_use_codes (
    code VARCHAR(10) PRIMARY KEY,
    description VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    is_residential BOOLEAN DEFAULT FALSE,
    is_commercial BOOLEAN DEFAULT FALSE,
    is_industrial BOOLEAN DEFAULT FALSE,
    is_agricultural BOOLEAN DEFAULT FALSE,
    is_vacant BOOLEAN DEFAULT FALSE,
    is_exempt BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ADD CUSTOMER PRIORITY FIELDS TO PROPERTIES TABLE
-- =====================================================

-- Mortgage/Lien Information (HIGH PRIORITY)
ALTER TABLE properties ADD COLUMN first_mtg_date DATE;
ALTER TABLE properties ADD COLUMN first_mtg_amount DECIMAL(12,2);
ALTER TABLE properties ADD COLUMN first_mtg_rate DECIMAL(6,4);
ALTER TABLE properties ADD COLUMN first_mtg_lender_name VARCHAR(200);
ALTER TABLE properties ADD COLUMN first_mtg_bal DECIMAL(12,2);
ALTER TABLE properties ADD COLUMN second_mtg_date DATE;
ALTER TABLE properties ADD COLUMN second_mtg_amount DECIMAL(12,2);
ALTER TABLE properties ADD COLUMN second_mtg_rate DECIMAL(6,4);
ALTER TABLE properties ADD COLUMN second_mtg_lender_name VARCHAR(200);
ALTER TABLE properties ADD COLUMN second_mtg_bal DECIMAL(12,2);

-- Property Classification (HIGH PRIORITY)
ALTER TABLE properties ADD COLUMN property_land_use_standardized_code VARCHAR(10);
ALTER TABLE properties ADD COLUMN property_land_use_description VARCHAR(200);
ALTER TABLE properties ADD COLUMN property_type VARCHAR(100);
ALTER TABLE properties ADD COLUMN property_use_general VARCHAR(100);
ALTER TABLE properties ADD COLUMN property_subtype VARCHAR(100);

-- Sales Intelligence (HIGH PRIORITY)
ALTER TABLE properties ADD COLUMN last_sale_date DATE;
ALTER TABLE properties ADD COLUMN last_sale_price DECIMAL(12,2);
ALTER TABLE properties ADD COLUMN last_sale_recording_date DATE;
ALTER TABLE properties ADD COLUMN prior_sale_date DATE;
ALTER TABLE properties ADD COLUMN prior_sale_price DECIMAL(12,2);
ALTER TABLE properties ADD COLUMN sales_history_count INTEGER DEFAULT 0;

-- Enhanced Property Details (MEDIUM PRIORITY)
ALTER TABLE properties ADD COLUMN stories_number DECIMAL(3,1);
ALTER TABLE properties ADD COLUMN garage_spaces INTEGER;
ALTER TABLE properties ADD COLUMN fireplace_count INTEGER;
ALTER TABLE properties ADD COLUMN pool_flag BOOLEAN DEFAULT FALSE;
ALTER TABLE properties ADD COLUMN air_conditioning_flag BOOLEAN DEFAULT FALSE;

-- Add foreign key reference to land use codes
ALTER TABLE properties ADD CONSTRAINT fk_properties_land_use_code 
    FOREIGN KEY (property_land_use_standardized_code) 
    REFERENCES land_use_codes(code);

-- =====================================================
-- INDEXES FOR NEW FIELDS
-- =====================================================

-- Mortgage/Lien indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_first_mtg_date 
    ON properties(first_mtg_date) WHERE first_mtg_date IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_first_mtg_amount 
    ON properties(first_mtg_amount) WHERE first_mtg_amount IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_first_mtg_lender 
    ON properties USING gin(first_mtg_lender_name gin_trgm_ops);

-- Property classification indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_land_use_code 
    ON properties(property_land_use_standardized_code);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_property_type 
    ON properties(property_type);

-- Sales intelligence indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_last_sale_date 
    ON properties(last_sale_date) WHERE last_sale_date IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_last_sale_price 
    ON properties(last_sale_price) WHERE last_sale_price IS NOT NULL;

-- =====================================================
-- POPULATE LAND USE CODES LOOKUP TABLE
-- =====================================================
INSERT INTO land_use_codes (code, description, category, is_residential, is_commercial, is_industrial, is_agricultural, is_vacant, is_exempt) VALUES
('0010', 'Miscellaneous (General)', 'Miscellaneous', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('0011', 'Pipeline or Right-of-Way', 'Miscellaneous', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('0012', 'Rail (Right-of-way & track)', 'Miscellaneous', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('0013', 'Road (Right-of-way)', 'Miscellaneous', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('0014', 'Utilities (Right-of-way ONLY)', 'Miscellaneous', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE),
('1000', 'Residential (General) (Single)', 'Residential', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('1001', 'Single Family Residential', 'Residential', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('1002', 'Townhouse (Residential)', 'Residential', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('1003', 'Cluster home (Residential)', 'Residential', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('1004', 'Condominium Unit (Residential)', 'Residential', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('1005', 'Cooperative Unit (Residential)', 'Residential', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('1006', 'Mobile/Manufactured Home (regardless of Land ownership)', 'Residential', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('1100', 'Residential Income (General) (Multi-Family)', 'Residential', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('1101', 'Duplex (2 units, any combination)', 'Residential', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('1102', 'Triplex (3 units, any combination)', 'Residential', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('1103', 'Quadruplex (4 units, any combination)', 'Residential', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('1104', 'Apartment House (5+ units)', 'Residential', TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('2000', 'Commercial (General)', 'Commercial', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('2001', 'Retail Stores ( Personal Services, Photography, Travel)', 'Commercial', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('2006', 'Grocery, Supermarket', 'Commercial', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('2012', 'Restaurant', 'Commercial', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('2013', 'Fast Food Restaurant / Drive-thru', 'Commercial', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('2020', 'Service station (full service)', 'Commercial', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('2034', 'Hotel', 'Commercial', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('3000', 'Commercial Office (General)', 'Commercial', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('3001', 'Professional Bldg (legal; insurance; real estate; business)', 'Commercial', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
('5000', 'Industrial (General)', 'Industrial', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE),
('5001', 'Manufacturing (light)', 'Industrial', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE),
('5003', 'Warehouse (Industrial)', 'Industrial', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE),
('6000', 'Heavy Industrial (General)', 'Industrial', FALSE, FALSE, TRUE, FALSE, FALSE, FALSE),
('7000', 'Agricultural / Rural (General)', 'Agricultural', FALSE, FALSE, FALSE, TRUE, FALSE, FALSE),
('7001', 'Farm (Irrigated or Dry)', 'Agricultural', FALSE, FALSE, FALSE, TRUE, FALSE, FALSE),
('7002', 'Ranch', 'Agricultural', FALSE, FALSE, FALSE, TRUE, FALSE, FALSE),
('8000', 'Vacant Land (General)', 'Vacant', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('8001', 'Residential-Vacant Land', 'Vacant', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('8002', 'Commercial-Vacant Land', 'Vacant', FALSE, FALSE, FALSE, FALSE, TRUE, FALSE),
('9000', 'Exempt (full or partial)', 'Exempt', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('9100', 'Institutional (General)', 'Exempt', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE),
('9200', 'Governmental/Public Use (General)', 'Exempt', FALSE, FALSE, FALSE, FALSE, FALSE, TRUE);

-- =====================================================
-- TRIGGER TO AUTO-POPULATE LAND USE DESCRIPTION
-- =====================================================
CREATE OR REPLACE FUNCTION update_land_use_description()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.property_land_use_standardized_code IS NOT NULL THEN
        -- Update description from lookup table
        SELECT description INTO NEW.property_land_use_description
        FROM land_use_codes 
        WHERE code = NEW.property_land_use_standardized_code;
        
        -- If no match found, set to 'Unknown Code: XXXX'
        IF NEW.property_land_use_description IS NULL THEN
            NEW.property_land_use_description := 'Unknown Code: ' || NEW.property_land_use_standardized_code;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_properties_land_use_description
    BEFORE INSERT OR UPDATE ON properties
    FOR EACH ROW EXECUTE FUNCTION update_land_use_description();

-- =====================================================
-- ENHANCED VIEWS WITH NEW FIELDS
-- =====================================================

-- Update complete properties view
DROP VIEW IF EXISTS vw_properties_complete;
CREATE VIEW vw_properties_complete AS
SELECT 
    p.id,
    p.quantarium_internal_pid,
    p.apn,
    p.fips_code,
    
    -- QVM Data
    p.estimated_value,
    p.price_range_max,
    p.price_range_min,
    p.confidence_score,
    p.qvm_asof_date,
    
    -- Location
    p.property_full_street_address,
    p.property_city_name,
    p.property_state,
    p.property_zip_code,
    p.latitude,
    p.longitude,
    
    -- Property Classification (NEW)
    p.property_land_use_standardized_code,
    p.property_land_use_description,
    p.property_type,
    p.property_use_general,
    
    -- Property Details
    p.building_area_total,
    p.lot_size_square_feet,
    p.number_of_bedrooms,
    p.number_of_bathrooms,
    p.year_built,
    p.stories_number,
    p.garage_spaces,
    p.pool_flag,
    
    -- Mortgage Information (NEW)
    p.first_mtg_date,
    p.first_mtg_amount,
    p.first_mtg_lender_name,
    p.first_mtg_bal,
    
    -- Sales Intelligence (NEW)
    p.last_sale_date,
    p.last_sale_price,
    p.prior_sale_date,
    p.prior_sale_price,
    
    -- Values
    p.total_assessed_value,
    p.total_market_value,
    
    -- Owner info (latest)
    po.current_owner_name,
    po.co_mailing_city,
    po.co_mailing_state,
    
    -- System
    p.created_at,
    p.updated_at,
    p.data_quality_score
    
FROM properties p
LEFT JOIN property_owners po ON p.id = po.property_id;

-- Customer Priority View (NEW)
CREATE VIEW vw_properties_customer_priority AS
SELECT 
    p.apn,
    p.property_full_street_address,
    p.property_city_name,
    p.property_state,
    p.property_zip_code,
    
    -- Property Classification
    p.property_land_use_standardized_code,
    p.property_land_use_description,
    p.property_type,
    
    -- QVM Valuation
    p.estimated_value,
    p.confidence_score,
    p.qvm_asof_date,
    
    -- Mortgage Information
    p.first_mtg_date,
    p.first_mtg_amount,
    p.first_mtg_rate,
    p.first_mtg_lender_name,
    p.first_mtg_bal,
    p.second_mtg_date,
    p.second_mtg_amount,
    p.second_mtg_lender_name,
    p.second_mtg_bal,
    
    -- Sales Intelligence
    p.last_sale_date,
    p.last_sale_price,
    p.prior_sale_date,
    p.prior_sale_price,
    
    -- Property Details
    p.building_area_total,
    p.lot_size_square_feet,
    p.number_of_bedrooms,
    p.number_of_bathrooms,
    p.year_built,
    p.stories_number,
    p.garage_spaces,
    p.pool_flag,
    
    -- Owner Information
    po.current_owner_name,
    po.co_mailing_city,
    po.co_mailing_state,
    
    -- System
    p.data_quality_score
    
FROM properties p
LEFT JOIN property_owners po ON p.id = po.property_id
WHERE p.estimated_value IS NOT NULL;

-- =====================================================
-- SCHEMA VERSIONING TABLE (FUTURE-PROOFING)
-- =====================================================
CREATE TABLE schema_versions (
    id SERIAL PRIMARY KEY,
    version_number VARCHAR(20) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    fields_added TEXT[], -- Array of field names added
    migration_file VARCHAR(200),
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    applied_by VARCHAR(100) DEFAULT CURRENT_USER
);

-- Record this migration
INSERT INTO schema_versions (version_number, description, fields_added, migration_file) VALUES
('002', 'Customer Priority Fields + Land Use Intelligence', 
ARRAY['first_mtg_date', 'first_mtg_amount', 'first_mtg_rate', 'first_mtg_lender_name', 'first_mtg_bal', 
      'second_mtg_date', 'second_mtg_amount', 'second_mtg_rate', 'second_mtg_lender_name', 'second_mtg_bal',
      'property_land_use_standardized_code', 'property_land_use_description', 'property_type', 
      'property_use_general', 'property_subtype', 'last_sale_date', 'last_sale_price', 
      'last_sale_recording_date', 'prior_sale_date', 'prior_sale_price', 'sales_history_count',
      'stories_number', 'garage_spaces', 'fireplace_count', 'pool_flag', 'air_conditioning_flag'],
'002_customer_priority_fields.sql');

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================
COMMENT ON TABLE land_use_codes IS 'Standardized land use code lookup table with intelligent categorization';
COMMENT ON COLUMN properties.property_land_use_standardized_code IS 'Raw standardized land use code';
COMMENT ON COLUMN properties.property_land_use_description IS 'Human-readable land use description (auto-populated)';
COMMENT ON COLUMN properties.first_mtg_amount IS 'First mortgage original amount';
COMMENT ON COLUMN properties.first_mtg_bal IS 'First mortgage current balance';
COMMENT ON COLUMN properties.last_sale_price IS 'Most recent sale price';
COMMENT ON TABLE schema_versions IS 'Schema version tracking for future-proofing field additions';

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Function to check if field exists before adding (for future migrations)
CREATE OR REPLACE FUNCTION column_exists(table_name TEXT, column_name TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'datnest' 
          AND table_name = $1 
          AND column_name = $2
    );
END;
$$ LANGUAGE plpgsql;

-- Function to safely add column if it doesn't exist
CREATE OR REPLACE FUNCTION safe_add_column(
    table_name TEXT, 
    column_name TEXT, 
    column_definition TEXT
)
RETURNS BOOLEAN AS $$
BEGIN
    IF NOT column_exists(table_name, column_name) THEN
        EXECUTE format('ALTER TABLE %I ADD COLUMN %I %s', table_name, column_name, column_definition);
        RETURN TRUE;
    END IF;
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions for new objects
-- GRANT SELECT ON land_use_codes TO datnest_api_user;
-- GRANT SELECT ON schema_versions TO datnest_api_user;
-- GRANT SELECT ON vw_properties_customer_priority TO datnest_api_user; 