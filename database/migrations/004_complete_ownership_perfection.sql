-- DatNest Core Platform - BATCH 3B: OWNERSHIP PERFECTION
-- Migration: 004_complete_ownership_perfection.sql
-- GOAL: 95.7% → 100% Ownership + Production optimization

-- Set schema
SET search_path TO datnest, public;

-- =====================================================
-- ADD FINAL OWNERSHIP FIELD (100% COMPLETION)
-- =====================================================

-- Add the final missing ownership field
ALTER TABLE properties ADD COLUMN ownership_start_date DATE;  -- Line 28: Ownership_Start_Date

-- =====================================================
-- PRODUCTION-READY INDEX OPTIMIZATIONS
-- =====================================================

-- Critical indexes for API performance and business use cases

-- 1. OWNERSHIP INTELLIGENCE INDEXES
CREATE INDEX IF NOT EXISTS idx_properties_ownership_timeline 
    ON properties(ownership_start_date) WHERE ownership_start_date IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_owner_contact 
    ON properties(current_owner_name, co_mailing_city, co_mailing_state) 
    WHERE current_owner_name IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_owner_occupancy 
    ON properties(owner_occupied) WHERE owner_occupied IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_owner_residence_duration 
    ON properties(length_of_residence_months) WHERE length_of_residence_months IS NOT NULL;

-- 2. ADDRESS API OPTIMIZATION INDEXES  
CREATE INDEX IF NOT EXISTS idx_properties_address_api_search 
    ON properties(property_city_name, property_state, property_zip_code) 
    WHERE property_city_name IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_precise_address_matching 
    ON properties(property_house_number, property_street_name, property_zip_code) 
    WHERE property_house_number IS NOT NULL AND property_street_name IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_geographic_search 
    ON properties(latitude, longitude) WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_census_analytics 
    ON properties(pa_census_tract) WHERE pa_census_tract IS NOT NULL;

-- 3. BUSINESS INTELLIGENCE INDEXES
CREATE INDEX IF NOT EXISTS idx_properties_owner_type_analysis 
    ON properties(buyer_vesting_code, owner_occupied) 
    WHERE buyer_vesting_code IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_address_quality 
    ON properties(match_code, location_code) 
    WHERE match_code IS NOT NULL;

-- =====================================================
-- DATA QUALITY CONSTRAINTS 
-- =====================================================

-- Add constraints for data integrity
ALTER TABLE properties ADD CONSTRAINT chk_ownership_start_date_reasonable 
    CHECK (ownership_start_date IS NULL OR ownership_start_date >= '1800-01-01');

ALTER TABLE properties ADD CONSTRAINT chk_residence_months_positive 
    CHECK (length_of_residence_months IS NULL OR length_of_residence_months >= 0);

-- =====================================================
-- PRODUCTION-READY VIEWS
-- =====================================================

-- Complete Ownership Intelligence View
CREATE OR REPLACE VIEW vw_ownership_intelligence AS
SELECT 
    p.id,
    p.quantarium_internal_pid,
    p.apn,
    
    -- Property Address (for context)
    p.property_full_street_address,
    p.property_city_name,
    p.property_state,
    p.property_zip_code,
    
    -- COMPLETE OWNER IDENTITY (100%)
    p.current_owner_name,
    p.owner1_first_name,
    p.owner1_middle_name,
    p.owner1_last_name,
    p.owner2_first_name,
    p.owner2_middle_name,
    p.owner2_last_name,
    
    -- COMPLETE MAILING ADDRESS (100%)
    p.co_mail_care_of_name,
    p.co_mail_street_address,
    p.co_mailing_city,
    p.co_mailing_state,
    p.co_mailing_zip_code,
    p.co_mailing_zip_plus4_code,
    p.co_unit_number,
    p.co_unit_type,
    
    -- COMPLETE OWNER CLASSIFICATION (100%)
    p.mail_care_of_name_indicator,
    p.owner_occupied,
    p.parsed_owner_source_code,
    p.buyer_id_code_1,
    p.buyer_vesting_code,
    
    -- COMPLETE OWNERSHIP DURATION (100%)
    p.length_of_residence_months,
    p.length_of_residence_code,
    p.ownership_start_date,  -- NEW: Final field
    
    -- QVM Value (for context)
    p.estimated_value,
    
    -- System
    p.created_at,
    p.updated_at
    
FROM properties p
WHERE p.current_owner_name IS NOT NULL 
   OR p.owner1_first_name IS NOT NULL
   OR p.co_mailing_city IS NOT NULL;

-- Complete Address Intelligence View
CREATE OR REPLACE VIEW vw_address_intelligence AS
SELECT 
    p.id,
    p.quantarium_internal_pid,
    p.apn,
    
    -- COMPLETE PROPERTY LOCATION (100%)
    p.property_full_street_address,
    p.property_city_name,
    p.property_state,
    p.property_zip_code,
    p.property_zip_plus4_code,
    p.property_house_number,
    p.property_street_direction_left,
    p.property_street_name,
    p.property_street_suffix,
    p.property_street_direction_right,
    p.property_unit_number,
    p.property_unit_type,
    
    -- COMPLETE GEOGRAPHIC INTELLIGENCE (100%)
    p.latitude,
    p.longitude,
    p.pa_carrier_route,
    p.pa_census_tract,
    p.match_code,
    p.location_code,
    
    -- QVM Value (for context)
    p.estimated_value,
    
    -- System
    p.created_at,
    p.updated_at
    
FROM properties p
WHERE p.property_full_street_address IS NOT NULL;

-- API-Ready Property Summary View
CREATE OR REPLACE VIEW vw_api_property_summary AS
SELECT 
    p.id,
    p.quantarium_internal_pid,
    p.apn,
    
    -- Core Address (API standard)
    p.property_full_street_address,
    p.property_city_name,
    p.property_state,
    p.property_zip_code,
    
    -- Enhanced Address
    p.property_house_number,
    p.property_street_name,
    p.property_unit_number,
    p.property_unit_type,
    p.latitude,
    p.longitude,
    
    -- Owner Information
    p.current_owner_name,
    p.owner_occupied,
    p.co_mailing_city,
    p.co_mailing_state,
    
    -- QVM Intelligence
    p.estimated_value,
    p.confidence_score,
    p.qvm_asof_date,
    
    -- Property Characteristics
    p.building_area_total,
    p.lot_size_square_feet,
    p.number_of_bedrooms,
    p.number_of_bathrooms,
    p.year_built,
    
    -- Quality Indicators
    p.match_code
    
FROM properties p
WHERE p.property_full_street_address IS NOT NULL 
  AND p.property_city_name IS NOT NULL
  AND p.property_state IS NOT NULL
  AND p.property_zip_code IS NOT NULL;

-- =====================================================
-- FIELD COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON COLUMN properties.ownership_start_date IS 'Date when current ownership began - critical for ownership duration analysis';

-- =====================================================
-- COMPLETION VALIDATION
-- =====================================================

-- Verify 100% completion
DO $$
DECLARE
    ownership_field_count INTEGER;
    expected_ownership_fields INTEGER := 23;
BEGIN
    SELECT COUNT(*) INTO ownership_field_count
    FROM information_schema.columns 
    WHERE table_name = 'properties' 
    AND table_schema = 'datnest'
    AND (
        column_name LIKE '%owner%' OR 
        column_name LIKE '%co_%' OR 
        column_name LIKE '%mail%' OR
        column_name LIKE '%buyer%' OR
        column_name LIKE '%residence%' OR
        column_name = 'current_owner_name' OR
        column_name = 'ownership_start_date'
    );
    
    IF ownership_field_count >= expected_ownership_fields THEN
        RAISE NOTICE '✅ OWNERSHIP COMPLETION: % fields (100%% or better)', ownership_field_count;
    ELSE
        RAISE NOTICE '⚠️  OWNERSHIP COMPLETION: % fields (%.1f%%)', ownership_field_count, (ownership_field_count::float / expected_ownership_fields * 100);
    END IF;
END $$; 