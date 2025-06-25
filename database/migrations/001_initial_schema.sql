-- DatNest Core Platform - Initial Database Schema
-- Optimized for 150M+ property records with QVM focus
-- Migration: 001_initial_schema.sql

-- Enable necessary PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schema for our application
CREATE SCHEMA IF NOT EXISTS datnest;

-- Set default schema
SET search_path TO datnest, public;

-- =====================================================
-- CORE PROPERTIES TABLE
-- =====================================================
-- Main table containing all property records with QVM data
CREATE TABLE properties (
    id BIGSERIAL PRIMARY KEY,
    
    -- Unique Identifiers
    quantarium_internal_pid VARCHAR(100) UNIQUE NOT NULL,
    apn VARCHAR(100) NOT NULL, -- Assessors_Parcel_Number
    fips_code VARCHAR(10) NOT NULL,
    duplicate_apn VARCHAR(100),
    tax_account_number VARCHAR(100),
    
    -- QVM Valuation Data (TIER 1 - HIGHEST PRIORITY)
    -- Note: Field names verified against TSV schema documentation
    estimated_value DECIMAL(12,2),              -- Quantarium Value / ESTIMATED_VALUE
    price_range_max DECIMAL(12,2),              -- Quantarium Value High / PRICE_RANGE_MAX
    price_range_min DECIMAL(12,2),              -- Quantarium Value Low / PRICE_RANGE_MIN
    confidence_score INTEGER,                   -- Quantarium Value Confidence / CONFIDENCE_SCORE
    qvm_asof_date DATE,                        -- QVM_asof_Date
    qvm_value_range_code VARCHAR(10),          -- QVM_Value_Range_Code
    
    -- Property Location (TIER 1)
    property_full_street_address VARCHAR(200),  -- Property_Full_Street_Address / Site Address
    property_city_name VARCHAR(100),           -- Property_City_Name / Site City
    property_state CHAR(2),                    -- Property_State / Site State
    property_zip_code CHAR(5),                 -- Property_Zip_Code / Site Zip5
    property_zip_plus4_code CHAR(4),           -- Property_Zip_Plus4Code
    
    -- Property Characteristics (TIER 1)
    building_area_total DECIMAL(10,0),         -- Building_Area_1 / Building Area 1
    lot_size_square_feet DECIMAL(12,2),        -- LotSize_Square_Feet / Lot Size SqFt
    lot_size_acres DECIMAL(10,4),              -- LotSize_Acres
    number_of_bedrooms INTEGER,                -- Number of Bedroom
    number_of_bathrooms DECIMAL(4,2),          -- Number of Baths
    
    -- Assessed Values (TIER 2)
    assessed_improvement_value DECIMAL(12,2),   -- Assessed_Improvement_Value
    assessed_land_value DECIMAL(12,2),         -- Assessed_Land_Value
    total_assessed_value DECIMAL(12,2),        -- Total_Assessed_Value / Assessed_Value
    assessment_year INTEGER,                   -- Assessment_Year
    
    -- Market Values (TIER 2)
    market_value_improvement DECIMAL(12,2),    -- Market_Value_Improvement
    market_value_land DECIMAL(12,2),          -- Market_Value_Land
    total_market_value DECIMAL(12,2),         -- Total_Market_Value / Market Value
    market_value_year INTEGER,                -- Market_Value_Year
    
    -- Geographic Data
    latitude DECIMAL(10,8),                   -- PA_Latitude
    longitude DECIMAL(11,8),                  -- PA_Longitude
    census_tract VARCHAR(20),                 -- PA_Census_Tract
    carrier_route VARCHAR(10),                -- PA_Carrier_Route
    
    -- Property Details
    year_built INTEGER,                       -- Effective_Year_Built
    building_class VARCHAR(50),               -- Building_Class
    building_condition VARCHAR(50),           -- Building_Condition
    building_quality VARCHAR(50),             -- Building_Quality
    property_use_code VARCHAR(10),            -- Property_Use_Code
    
    -- Tax Information
    tax_amount DECIMAL(10,2),                 -- Tax_Amount
    tax_year INTEGER,                         -- Tax_Year
    tax_delinquent_year INTEGER,              -- Tax_Delinquent_Year
    
    -- Owner Occupancy
    owner_occupied BOOLEAN,                   -- Owner_Occupied
    length_of_residence_months INTEGER,       -- Length_of_Residence_Months
    ownership_start_date DATE,                -- Ownership_Start_Date
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(50) DEFAULT 'quantarium_openlien',
    data_quality_score INTEGER CHECK (data_quality_score >= 0 AND data_quality_score <= 100),
    
    -- Constraints
    CONSTRAINT chk_estimated_value_positive CHECK (estimated_value > 0 OR estimated_value IS NULL),
    CONSTRAINT chk_confidence_score_range CHECK (confidence_score >= 0 AND confidence_score <= 100),
    CONSTRAINT chk_coordinates CHECK (
        (latitude IS NULL AND longitude IS NULL) OR 
        (latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180)
    )
);

-- =====================================================
-- PROPERTY OWNERS TABLE
-- =====================================================
CREATE TABLE property_owners (
    id BIGSERIAL PRIMARY KEY,
    property_id BIGINT NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    
    -- Owner Information
    current_owner_name VARCHAR(200),           -- Current_Owner_Name
    owner1_first_name VARCHAR(100),           -- Owner1FirstName
    owner1_middle_name VARCHAR(100),          -- Owner1MiddleName
    owner1_last_name VARCHAR(100),            -- Owner1LastName
    owner2_first_name VARCHAR(100),           -- Owner2Firstname
    owner2_middle_name VARCHAR(100),          -- Owner2MiddleName
    owner2_last_name VARCHAR(100),            -- Owner2LastName
    
    -- Mailing Address
    co_mail_care_of_name VARCHAR(200),        -- CO_Mail_Care_of_Name
    co_mail_street_address VARCHAR(200),      -- CO_Mail_Street_Address
    co_mailing_city VARCHAR(100),             -- CO_Mailing_City
    co_mailing_state CHAR(2),                 -- CO_Mailing_State
    co_mailing_zip_code CHAR(5),              -- CO_Mailing_Zip_Code
    co_mailing_zip_plus4_code CHAR(4),        -- CO_Mailing_Zip_Plus4Code
    co_unit_number VARCHAR(20),               -- CO_Unit_Number
    co_unit_type VARCHAR(20),                 -- CO_Unit_Type
    
    -- Ownership Details
    buyer_id_code_1 VARCHAR(50),              -- Buyer_ID_Code_1
    buyer_vesting_code VARCHAR(50),           -- Buyer_Vesting_Code
    parsed_owner_source_code VARCHAR(50),     -- ParsedOwnerSourceCode
    mail_care_of_name_indicator BOOLEAN,      -- Mail_Care_Of_Name_Indicator
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- PROPERTY SALES TABLE
-- =====================================================
CREATE TABLE property_sales (
    id BIGSERIAL PRIMARY KEY,
    property_id BIGINT NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    
    -- Sale Type (last_sale, last_valid, prior_sale, prior_valid)
    sale_type VARCHAR(20) NOT NULL,
    
    -- Sale Information
    sale_book_number VARCHAR(50),
    sale_page_number VARCHAR(50),
    sale_document_number VARCHAR(100),
    sale_document_type_code VARCHAR(20),
    sale_price DECIMAL(12,2),
    sale_price_code VARCHAR(10),
    sale_recording_date DATE,
    sale_transfer_date DATE,
    
    -- Sale Flags
    reo_flag BOOLEAN DEFAULT FALSE,
    distressed_sale_flag BOOLEAN DEFAULT FALSE,
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_sale_type CHECK (sale_type IN ('last_sale', 'last_valid', 'prior_sale', 'prior_valid')),
    CONSTRAINT chk_sale_price_positive CHECK (sale_price > 0 OR sale_price IS NULL)
);

-- =====================================================
-- PROPERTY LOANS TABLE (TIER 3 - Future Enhancement)
-- =====================================================
CREATE TABLE property_loans (
    id BIGSERIAL PRIMARY KEY,
    property_id BIGINT NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    
    -- Loan Information
    loan_number INTEGER CHECK (loan_number BETWEEN 1 AND 4),
    loan_amount DECIMAL(12,2),                -- Loan Amount 1-4
    current_balance DECIMAL(12,2),            -- Estimated Amount Bal 1-4
    lender_name VARCHAR(200),
    loan_type VARCHAR(50),
    loan_date DATE,
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_loan_amount_positive CHECK (loan_amount > 0 OR loan_amount IS NULL),
    CONSTRAINT chk_current_balance_positive CHECK (current_balance >= 0 OR current_balance IS NULL)
);

-- =====================================================
-- DATA PROCESSING AUDIT TABLE
-- =====================================================
CREATE TABLE data_processing_audit (
    id BIGSERIAL PRIMARY KEY,
    
    -- Processing Information
    file_name VARCHAR(200) NOT NULL,
    file_size_bytes BIGINT,
    processing_started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    processing_status VARCHAR(20) DEFAULT 'in_progress',
    
    -- Statistics
    total_records_processed INTEGER DEFAULT 0,
    successful_inserts INTEGER DEFAULT 0,
    failed_inserts INTEGER DEFAULT 0,
    duplicate_records INTEGER DEFAULT 0,
    
    -- Error Information
    error_message TEXT,
    lambda_function_name VARCHAR(100),
    lambda_request_id VARCHAR(100),
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_processing_status CHECK (
        processing_status IN ('in_progress', 'completed', 'failed', 'partial')
    )
);

-- =====================================================
-- INDEXES FOR PERFORMANCE (150M+ RECORDS)
-- =====================================================

-- Primary business indexes (QVM and search)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_estimated_value 
    ON properties(estimated_value) WHERE estimated_value IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_qvm_date 
    ON properties(qvm_asof_date) WHERE qvm_asof_date IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_confidence_score 
    ON properties(confidence_score) WHERE confidence_score IS NOT NULL;

-- Location-based searches
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_location 
    ON properties(property_state, property_city_name, property_zip_code);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_coords 
    ON properties(latitude, longitude) WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- Hash index for exact APN lookups (very fast for 150M records)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_apn_hash 
    ON properties USING hash(apn);

-- Unique identifier indexes
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_quantarium_pid 
    ON properties(quantarium_internal_pid);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_fips_apn 
    ON properties(fips_code, apn);

-- Property characteristics for filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_building_area 
    ON properties(building_area_total) WHERE building_area_total IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_lot_size 
    ON properties(lot_size_square_feet) WHERE lot_size_square_feet IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_bedrooms_baths 
    ON properties(number_of_bedrooms, number_of_bathrooms) 
    WHERE number_of_bedrooms IS NOT NULL OR number_of_bathrooms IS NOT NULL;

-- Text search index for addresses
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_address_gin 
    ON properties USING gin(property_full_street_address gin_trgm_ops);

-- Foreign key indexes for JOINs
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_property_owners_property_id 
    ON property_owners(property_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_property_sales_property_id 
    ON property_sales(property_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_property_loans_property_id 
    ON property_loans(property_id);

-- Audit table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_file_name 
    ON data_processing_audit(file_name);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_processing_status 
    ON data_processing_audit(processing_status);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_started_at 
    ON data_processing_audit(processing_started_at);

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Complete property view with QVM data
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
    
    -- Property Details
    p.building_area_total,
    p.lot_size_square_feet,
    p.number_of_bedrooms,
    p.number_of_bathrooms,
    p.year_built,
    
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

-- QVM-focused view for valuation analysis
CREATE VIEW vw_properties_qvm AS
SELECT 
    apn,
    property_full_street_address,
    property_city_name,
    property_state,
    property_zip_code,
    estimated_value,
    price_range_max,
    price_range_min,
    confidence_score,
    qvm_asof_date,
    building_area_total,
    lot_size_square_feet,
    number_of_bedrooms,
    number_of_bathrooms
FROM properties 
WHERE estimated_value IS NOT NULL 
  AND confidence_score IS NOT NULL;

-- =====================================================
-- TRIGGERS FOR UPDATED_AT
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all main tables
CREATE TRIGGER update_properties_updated_at 
    BEFORE UPDATE ON properties 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_property_owners_updated_at 
    BEFORE UPDATE ON property_owners 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_property_sales_updated_at 
    BEFORE UPDATE ON property_sales 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_property_loans_updated_at 
    BEFORE UPDATE ON property_loans 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- INITIAL DATA QUALITY RULES
-- =====================================================

-- Function to calculate data quality score
CREATE OR REPLACE FUNCTION calculate_data_quality_score(
    p_estimated_value DECIMAL,
    p_confidence_score INTEGER,
    p_address VARCHAR,
    p_city VARCHAR,
    p_state CHAR,
    p_zip CHAR,
    p_building_area DECIMAL
) RETURNS INTEGER AS $$
DECLARE
    quality_score INTEGER := 0;
BEGIN
    -- QVM data present (40 points max)
    IF p_estimated_value IS NOT NULL THEN quality_score := quality_score + 20; END IF;
    IF p_confidence_score IS NOT NULL THEN quality_score := quality_score + 20; END IF;
    
    -- Location data complete (30 points max)
    IF p_address IS NOT NULL AND LENGTH(TRIM(p_address)) > 0 THEN quality_score := quality_score + 10; END IF;
    IF p_city IS NOT NULL AND LENGTH(TRIM(p_city)) > 0 THEN quality_score := quality_score + 10; END IF;
    IF p_state IS NOT NULL AND LENGTH(TRIM(p_state)) = 2 THEN quality_score := quality_score + 5; END IF;
    IF p_zip IS NOT NULL AND LENGTH(TRIM(p_zip)) = 5 THEN quality_score := quality_score + 5; END IF;
    
    -- Property characteristics (30 points max)
    IF p_building_area IS NOT NULL AND p_building_area > 0 THEN quality_score := quality_score + 30; END IF;
    
    RETURN quality_score;
END;
$$ LANGUAGE plpgsql;

-- Trigger to calculate data quality score on insert/update
CREATE OR REPLACE FUNCTION set_data_quality_score()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_quality_score := calculate_data_quality_score(
        NEW.estimated_value,
        NEW.confidence_score,
        NEW.property_full_street_address,
        NEW.property_city_name,
        NEW.property_state,
        NEW.property_zip_code,
        NEW.building_area_total
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_properties_data_quality_score 
    BEFORE INSERT OR UPDATE ON properties 
    FOR EACH ROW EXECUTE FUNCTION set_data_quality_score();

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE properties IS 'Main property records table with QVM valuations, optimized for 150M+ records';
COMMENT ON COLUMN properties.estimated_value IS 'Quantarium Value - Primary QVM valuation amount';
COMMENT ON COLUMN properties.confidence_score IS 'QVM confidence score (0-100)';
COMMENT ON COLUMN properties.data_quality_score IS 'Computed data completeness score (0-100)';

COMMENT ON TABLE property_owners IS 'Property ownership and mailing information';
COMMENT ON TABLE property_sales IS 'Historical sales transactions';
COMMENT ON TABLE property_loans IS 'Loan and mortgage information (future enhancement)';
COMMENT ON TABLE data_processing_audit IS 'ETL processing audit log';

COMMENT ON VIEW vw_properties_complete IS 'Complete property view with owner info for API responses';
COMMENT ON VIEW vw_properties_qvm IS 'QVM-focused view for valuation analysis and search';

-- Grant permissions (adjust as needed for your environment)
-- GRANT ALL ON SCHEMA datnest TO datnest_api_user;
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA datnest TO datnest_api_user;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA datnest TO datnest_api_user; 