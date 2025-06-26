-- DatNest Core Platform - BATCH 4A: LAND CHARACTERISTICS COMPLETION
-- Migration: 005_complete_land_characteristics.sql
-- GOAL: 62.5% → 100% Land Characteristics + Production optimization

-- Set schema
SET search_path TO datnest, public;

-- =====================================================
-- ADD MISSING LAND CHARACTERISTICS FIELDS (100% COMPLETION)
-- =====================================================

-- Land Quality & Environment (Missing 2/4 fields)
ALTER TABLE properties ADD COLUMN view VARCHAR(100);                    -- View - Property view description/premium
ALTER TABLE properties ADD COLUMN view_code VARCHAR(10);                -- View_Code - Standardized view classification

-- Zoning & Land Use Intelligence (Missing 3/4 fields)  
ALTER TABLE properties ADD COLUMN land_use_code VARCHAR(10);             -- Land_Use_Code - Primary land use classification
ALTER TABLE properties ADD COLUMN land_use_general VARCHAR(50);          -- Land_Use_General - General land use category
ALTER TABLE properties ADD COLUMN neighborhood_code VARCHAR(20);         -- Neighborhood_Code - Area/district classification

-- Environmental Risk Assessment (New field)
ALTER TABLE properties ADD COLUMN flood_zone VARCHAR(10);                -- Flood_Zone - FEMA flood zone designation

-- =====================================================
-- LAND CHARACTERISTICS LOOKUP TABLES
-- =====================================================

-- View Classification Lookup
CREATE TABLE IF NOT EXISTS view_classifications (
    view_code VARCHAR(10) PRIMARY KEY,
    view_description VARCHAR(100) NOT NULL,
    view_category VARCHAR(50),
    premium_indicator BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Populate view classifications
INSERT INTO view_classifications (view_code, view_description, view_category, premium_indicator) VALUES
('NONE', 'No View', 'Standard', FALSE),
('CITY', 'City View', 'Urban', TRUE),
('WATER', 'Water View', 'Premium', TRUE),
('OCEAN', 'Ocean View', 'Premium', TRUE),
('LAKE', 'Lake View', 'Premium', TRUE),
('RIVER', 'River View', 'Premium', TRUE),
('MOUNT', 'Mountain View', 'Premium', TRUE),
('GOLF', 'Golf Course View', 'Premium', TRUE),
('PARK', 'Park View', 'Enhanced', TRUE),
('GARDEN', 'Garden View', 'Enhanced', FALSE),
('STREET', 'Street View', 'Standard', FALSE),
('COURT', 'Courtyard View', 'Standard', FALSE)
ON CONFLICT (view_code) DO NOTHING;

-- Neighborhood Classification Lookup
CREATE TABLE IF NOT EXISTS neighborhood_classifications (
    neighborhood_code VARCHAR(20) PRIMARY KEY,
    neighborhood_name VARCHAR(100),
    neighborhood_type VARCHAR(50),
    desirability_score INTEGER CHECK (desirability_score >= 1 AND desirability_score <= 10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Land Use Code Lookup (Enhanced)
CREATE TABLE IF NOT EXISTS land_use_classifications (
    land_use_code VARCHAR(10) PRIMARY KEY,
    land_use_description VARCHAR(100) NOT NULL,
    land_use_category VARCHAR(50),
    development_potential VARCHAR(50),
    investment_grade VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Populate basic land use classifications
INSERT INTO land_use_classifications (land_use_code, land_use_description, land_use_category, development_potential, investment_grade) VALUES
('RES', 'Residential', 'Residential', 'Limited', 'Stable'),
('COM', 'Commercial', 'Commercial', 'High', 'Growth'),
('IND', 'Industrial', 'Industrial', 'Medium', 'Income'),
('AGR', 'Agricultural', 'Agricultural', 'Variable', 'Cyclical'),
('VAC', 'Vacant', 'Vacant', 'High', 'Speculative'),
('MIX', 'Mixed Use', 'Mixed', 'High', 'Growth'),
('INS', 'Institutional', 'Institutional', 'Low', 'Stable'),
('REC', 'Recreational', 'Recreation', 'Limited', 'Lifestyle')
ON CONFLICT (land_use_code) DO NOTHING;

-- =====================================================
-- PRODUCTION-READY INDEX OPTIMIZATIONS
-- =====================================================

-- Land Intelligence Indexes for Property Search & Analytics
CREATE INDEX IF NOT EXISTS idx_properties_land_size_search 
    ON properties(lot_size_square_feet) WHERE lot_size_square_feet IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_acreage_search 
    ON properties(lot_size_acres) WHERE lot_size_acres IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_view_premium 
    ON properties(view_code) WHERE view_code IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_zoning_analysis 
    ON properties(zoning, land_use_code) WHERE zoning IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_neighborhood_analysis 
    ON properties(neighborhood_code) WHERE neighborhood_code IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_environmental_risk 
    ON properties(flood_zone) WHERE flood_zone IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_land_quality 
    ON properties(topography, site_influence) WHERE topography IS NOT NULL;

-- Business Intelligence Composite Indexes
CREATE INDEX IF NOT EXISTS idx_properties_development_potential 
    ON properties(land_use_code, zoning, lot_size_acres) 
    WHERE land_use_code IS NOT NULL AND zoning IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_properties_premium_features 
    ON properties(view_code, lot_size_square_feet, topography) 
    WHERE view_code IS NOT NULL;

-- =====================================================
-- DATA QUALITY CONSTRAINTS (DEFERRED - EXISTING DATA ISSUES)
-- =====================================================

-- Note: Data quality constraints deferred due to existing data with invalid values
-- These can be added later after data cleaning

-- Foreign key constraints for data integrity
ALTER TABLE properties ADD CONSTRAINT fk_properties_view_code 
    FOREIGN KEY (view_code) REFERENCES view_classifications(view_code);

-- =====================================================
-- PRODUCTION-READY VIEWS FOR LAND INTELLIGENCE
-- =====================================================

-- Complete Land Intelligence View
CREATE OR REPLACE VIEW vw_land_intelligence AS
SELECT 
    p.id,
    p.quantarium_internal_pid,
    p.apn,
    
    -- Property Address (for context)
    p.property_full_street_address,
    p.property_city_name,
    p.property_state,
    p.property_zip_code,
    
    -- COMPLETE LOT SIZE & DIMENSIONS (100%)
    p.lot_size_square_feet,
    p.lot_size_acres,
    p.lot_size_depth_feet,
    p.lot_size_frontage_feet,
    p.lot_size_or_area,
    p.lot_size_area_unit,
    p.original_lot_size_or_area,
    
    -- COMPLETE LAND QUALITY & ENVIRONMENT (100%)
    p.topography,
    p.site_influence,
    p.view,                          -- NEW
    p.view_code,                     -- NEW
    vc.view_description,
    vc.view_category,
    vc.premium_indicator,
    
    -- COMPLETE ZONING & LAND USE (100%)
    p.zoning,
    p.land_use_code,                 -- NEW
    p.land_use_general,              -- NEW
    p.neighborhood_code,             -- NEW
    luc.land_use_description,
    luc.development_potential,
    luc.investment_grade,
    
    -- ENVIRONMENTAL RISK ASSESSMENT (100%)
    p.flood_zone,                    -- NEW
    
    -- QVM Value (for context)
    p.estimated_value,
    
    -- System
    p.created_at,
    p.updated_at
    
FROM properties p
LEFT JOIN view_classifications vc ON p.view_code = vc.view_code
LEFT JOIN land_use_classifications luc ON p.land_use_code = luc.land_use_code
WHERE p.lot_size_square_feet IS NOT NULL 
   OR p.lot_size_acres IS NOT NULL
   OR p.zoning IS NOT NULL;

-- Land Development Analysis View
CREATE OR REPLACE VIEW vw_land_development_analysis AS
SELECT 
    p.id,
    p.quantarium_internal_pid,
    p.apn,
    p.property_full_street_address,
    p.property_city_name,
    p.property_state,
    
    -- Development Metrics
    p.lot_size_acres,
    p.lot_size_square_feet,
    p.zoning,
    p.land_use_code,
    p.topography,
    p.flood_zone,
    
    -- Development Potential Scoring
    CASE 
        WHEN p.lot_size_acres >= 1.0 THEN 'Large Lot'
        WHEN p.lot_size_acres >= 0.5 THEN 'Medium Lot'
        WHEN p.lot_size_acres >= 0.25 THEN 'Standard Lot'
        ELSE 'Small Lot'
    END AS lot_size_category,
    
    CASE 
        WHEN p.flood_zone IN ('A', 'AE', 'AO', 'AH') THEN 'High Risk'
        WHEN p.flood_zone IN ('X', 'C') THEN 'Low Risk'
        WHEN p.flood_zone = 'B' THEN 'Medium Risk'
        ELSE 'Unknown Risk'
    END AS flood_risk_level,
    
    -- Premium Indicators
    vc.premium_indicator AS has_premium_view,
    luc.development_potential,
    
    -- QVM Context
    p.estimated_value,
    
    -- Calculated Fields
    ROUND(p.estimated_value / NULLIF(p.lot_size_square_feet, 0), 2) AS price_per_sq_ft
    
FROM properties p
LEFT JOIN view_classifications vc ON p.view_code = vc.view_code
LEFT JOIN land_use_classifications luc ON p.land_use_code = luc.land_use_code
WHERE p.lot_size_square_feet IS NOT NULL 
  AND p.estimated_value IS NOT NULL;

-- Land Premium Analysis View  
CREATE OR REPLACE VIEW vw_land_premium_analysis AS
SELECT 
    p.id,
    p.quantarium_internal_pid,
    p.apn,
    
    -- Location Context
    p.property_city_name,
    p.property_state,
    p.neighborhood_code,
    
    -- Premium Features
    p.view,
    p.view_code,
    vc.premium_indicator AS premium_view,
    p.lot_size_acres,
    p.topography,
    
    -- Market Analysis
    p.estimated_value,
    p.lot_size_square_feet,
    
    -- Premium Scoring
    (CASE WHEN vc.premium_indicator THEN 1 ELSE 0 END +
     CASE WHEN p.lot_size_acres > 1.0 THEN 1 ELSE 0 END +
     CASE WHEN p.topography IN ('Level', 'Gently Sloping') THEN 1 ELSE 0 END) AS premium_score
    
FROM properties p
LEFT JOIN view_classifications vc ON p.view_code = vc.view_code
WHERE p.estimated_value IS NOT NULL
  AND (vc.premium_indicator = TRUE 
       OR p.lot_size_acres > 0.5 
       OR p.view IS NOT NULL);

-- =====================================================
-- FIELD COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON COLUMN properties.view IS 'Property view description - impacts premium value';
COMMENT ON COLUMN properties.view_code IS 'Standardized view classification code';
COMMENT ON COLUMN properties.land_use_code IS 'Primary land use classification code';
COMMENT ON COLUMN properties.land_use_general IS 'General land use category';
COMMENT ON COLUMN properties.neighborhood_code IS 'Neighborhood/district classification';
COMMENT ON COLUMN properties.flood_zone IS 'FEMA flood zone designation for risk assessment';

-- =====================================================
-- COMPLETION VALIDATION
-- =====================================================

-- Verify 100% Land Characteristics completion
DO $$
DECLARE
    land_field_count INTEGER;
    expected_land_fields INTEGER := 16;
BEGIN
    SELECT COUNT(*) INTO land_field_count
    FROM information_schema.columns 
    WHERE table_name = 'properties' 
    AND table_schema = 'datnest'
    AND (
        column_name LIKE '%lot%' OR 
        column_name LIKE '%land%' OR 
        column_name LIKE '%acre%' OR
        column_name LIKE '%frontage%' OR
        column_name LIKE '%depth%' OR
        column_name LIKE '%square_feet%' OR
        column_name LIKE '%topography%' OR
        column_name LIKE '%site%' OR
        column_name LIKE '%view%' OR
        column_name LIKE '%zoning%' OR
        column_name = 'flood_zone' OR
        column_name = 'neighborhood_code'
    );
    
    IF land_field_count >= expected_land_fields THEN
        RAISE NOTICE '✅ LAND CHARACTERISTICS COMPLETION: % fields (100%% or better)', land_field_count;
    ELSE
        RAISE NOTICE '⚠️  LAND CHARACTERISTICS COMPLETION: % fields (%.1f%%)', land_field_count, (land_field_count::float / expected_land_fields * 100);
    END IF;
END $$; 