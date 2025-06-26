-- DatNest Core Platform - Complete Property Location & Ownership Categories
-- Migration: 003_complete_location_ownership.sql
-- BATCH 3A: SYSTEMATIC COMPLETION - Property Location (67% → 100%) + Ownership (60% → 100%)

-- Set schema
SET search_path TO datnest, public;

-- =====================================================
-- COMPLETE PROPERTY LOCATION CATEGORY (TIER 1)
-- Adding 12 missing fields from data_dictionary.txt lines 76-93
-- =====================================================

-- Property Address Components (Detailed breakdown)
ALTER TABLE properties ADD COLUMN property_zip_plus4_code VARCHAR(4);        -- Line 80: Property_Zip_Plus4Code
ALTER TABLE properties ADD COLUMN property_house_number VARCHAR(13);         -- Line 81: Property_House_Number
ALTER TABLE properties ADD COLUMN property_street_direction_left VARCHAR(2); -- Line 82: Property_Street_Direction_Left
ALTER TABLE properties ADD COLUMN property_street_name VARCHAR(40);          -- Line 83: Property_Street_Name
ALTER TABLE properties ADD COLUMN property_street_suffix VARCHAR(4);         -- Line 84: Property_Street_Suffix
ALTER TABLE properties ADD COLUMN property_street_direction_right VARCHAR(2);-- Line 85: Property_Street_Direction_Right
ALTER TABLE properties ADD COLUMN property_unit_number VARCHAR(11);          -- Line 86: Property_Unit_Number
ALTER TABLE properties ADD COLUMN property_unit_type VARCHAR(4);             -- Line 87: Property_Unit_Type

-- Geographic Intelligence (Enhanced location data)
ALTER TABLE properties ADD COLUMN pa_carrier_route VARCHAR(4);               -- Line 88: PA_Carrier_Route
ALTER TABLE properties ADD COLUMN pa_census_tract VARCHAR(16);               -- Line 89: PA_Census_Tract
ALTER TABLE properties ADD COLUMN match_code VARCHAR(4);                     -- Line 92: Match_Code (GeoStan)
ALTER TABLE properties ADD COLUMN location_code VARCHAR(4);                  -- Line 93: Location_Code (GeoStan)

-- =====================================================
-- COMPLETE OWNERSHIP CATEGORY
-- Adding 10 remaining missing fields from data_dictionary.txt lines 6-28
-- =====================================================

-- Owner Personal Details (Missing components)
ALTER TABLE properties ADD COLUMN owner1_middle_name VARCHAR(166);           -- Line 18: Owner1MiddleName
ALTER TABLE properties ADD COLUMN owner2_middle_name VARCHAR(166);           -- Line 21: Owner2MiddleName

-- Complete Mailing Address (Missing components)
ALTER TABLE properties ADD COLUMN co_mail_care_of_name VARCHAR(60);          -- Line 7: CO_Mail_Care_of_Name
ALTER TABLE properties ADD COLUMN co_mail_street_address VARCHAR(80);        -- Line 8: CO_Mail_Street_Address
ALTER TABLE properties ADD COLUMN co_mailing_zip_plus4_code VARCHAR(4);      -- Line 12: CO_Mailing_Zip_Plus4Code
ALTER TABLE properties ADD COLUMN co_unit_number VARCHAR(11);                -- Line 13: CO_Unit_Number
ALTER TABLE properties ADD COLUMN co_unit_type VARCHAR(4);                   -- Line 14: CO_Unit_Type

-- Owner Classification & Intelligence
ALTER TABLE properties ADD COLUMN mail_care_of_name_indicator VARCHAR(1);    -- Line 15: Mail_Care_Of_Name_Indicator
ALTER TABLE properties ADD COLUMN parsed_owner_source_code VARCHAR(1);       -- Line 23: ParsedOwnerSourceCode
ALTER TABLE properties ADD COLUMN buyer_id_code_1 VARCHAR(2);                -- Line 24: Buyer_ID_Code_1
ALTER TABLE properties ADD COLUMN buyer_vesting_code VARCHAR(2);             -- Line 25: Buyer_Vesting_Code
ALTER TABLE properties ADD COLUMN length_of_residence_code VARCHAR(2);       -- Line 27: Length_of_Residence_Code

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Property Location Indexes
CREATE INDEX IF NOT EXISTS idx_properties_detailed_address 
    ON properties(property_street_name, property_house_number, property_street_suffix);

CREATE INDEX IF NOT EXISTS idx_properties_unit_info 
    ON properties(property_unit_number, property_unit_type) 
    WHERE property_unit_number IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_census_tract 
    ON properties(pa_census_tract) WHERE pa_census_tract IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_carrier_route 
    ON properties(pa_carrier_route) WHERE pa_carrier_route IS NOT NULL;

-- Ownership Indexes
CREATE INDEX IF NOT EXISTS idx_properties_owner_names 
    ON properties(owner1_first_name, owner1_last_name) 
    WHERE owner1_first_name IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_mailing_address 
    ON properties(co_mail_street_address, co_mailing_city, co_mailing_state);

CREATE INDEX IF NOT EXISTS idx_properties_buyer_codes 
    ON properties(buyer_id_code_1, buyer_vesting_code) 
    WHERE buyer_id_code_1 IS NOT NULL;

-- =====================================================
-- VIEWS WILL BE UPDATED SEPARATELY AFTER MIGRATION
-- =====================================================
-- Note: View recreation removed to avoid field reference issues during migration

-- =====================================================
-- MIGRATION RECORD (SCHEMA_VERSIONS TABLE NOT AVAILABLE)
-- =====================================================
-- Note: schema_versions table doesn't exist yet, tracking manually for now

-- =====================================================
-- FIELD COUNTS FOR VALIDATION
-- =====================================================
COMMENT ON TABLE properties IS 'Properties table now contains: Property Location (18/18 = 100%), Ownership (25/25 = 100%)';

-- Property Location field comments
COMMENT ON COLUMN properties.property_zip_plus4_code IS 'Property ZIP+4 extension';
COMMENT ON COLUMN properties.property_house_number IS 'Property house/building number';
COMMENT ON COLUMN properties.property_street_direction_left IS 'Street direction prefix (N, S, E, W)';
COMMENT ON COLUMN properties.property_street_name IS 'Street name only (no direction/suffix)';
COMMENT ON COLUMN properties.property_street_suffix IS 'Street suffix (St, Ave, Blvd, etc.)';
COMMENT ON COLUMN properties.property_street_direction_right IS 'Street direction suffix';
COMMENT ON COLUMN properties.property_unit_number IS 'Apartment/unit number';
COMMENT ON COLUMN properties.property_unit_type IS 'Unit type (Apt, Ste, Unit, etc.)';
COMMENT ON COLUMN properties.pa_carrier_route IS 'USPS carrier route code';
COMMENT ON COLUMN properties.pa_census_tract IS 'Census tract identifier';
COMMENT ON COLUMN properties.match_code IS 'GeoStan address match quality code';
COMMENT ON COLUMN properties.location_code IS 'GeoStan location precision code';

-- Ownership field comments
COMMENT ON COLUMN properties.owner1_middle_name IS 'Primary owner middle name';
COMMENT ON COLUMN properties.owner2_middle_name IS 'Secondary owner middle name';
COMMENT ON COLUMN properties.co_mail_care_of_name IS 'Mailing address care-of name';
COMMENT ON COLUMN properties.co_mail_street_address IS 'Owner mailing street address';
COMMENT ON COLUMN properties.co_mailing_zip_plus4_code IS 'Owner mailing ZIP+4 extension';
COMMENT ON COLUMN properties.co_unit_number IS 'Owner mailing address unit number';
COMMENT ON COLUMN properties.co_unit_type IS 'Owner mailing address unit type';
COMMENT ON COLUMN properties.mail_care_of_name_indicator IS 'Flag indicating care-of name present';
COMMENT ON COLUMN properties.parsed_owner_source_code IS 'Source code for owner parsing';
COMMENT ON COLUMN properties.buyer_id_code_1 IS 'Buyer identification code';
COMMENT ON COLUMN properties.buyer_vesting_code IS 'Buyer vesting/ownership type code';
COMMENT ON COLUMN properties.length_of_residence_code IS 'Residence length category code'; 