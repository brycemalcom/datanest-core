-- MIGRATION: 006_complete_building_characteristics
-- GOAL: Add all 73 "Building Characteristics" fields to the properties table.

ALTER TABLE datnest.properties
    -- Building Area & Size
    ADD COLUMN IF NOT EXISTS building_area_gross DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS building_area_living DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS building_area_total_calculated DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS effective_year_built INTEGER,
    ADD COLUMN IF NOT EXISTS number_of_stories DECIMAL(4, 1),
    ADD COLUMN IF NOT EXISTS total_number_of_rooms INTEGER,
    ADD COLUMN IF NOT EXISTS number_of_units INTEGER,
    ADD COLUMN IF NOT EXISTS number_of_partial_baths INTEGER,

    -- Construction & Features
    ADD COLUMN IF NOT EXISTS type_construction VARCHAR(50),
    ADD COLUMN IF NOT EXISTS building_style VARCHAR(50),
    ADD COLUMN IF NOT EXISTS exterior_walls VARCHAR(50),
    ADD COLUMN IF NOT EXISTS foundation VARCHAR(50),
    ADD COLUMN IF NOT EXISTS roof_cover VARCHAR(50),
    ADD COLUMN IF NOT EXISTS roof_type VARCHAR(50),
    ADD COLUMN IF NOT EXISTS interior_walls VARCHAR(50),
    ADD COLUMN IF NOT EXISTS floor_cover VARCHAR(50),

    -- Systems
    ADD COLUMN IF NOT EXISTS heating VARCHAR(50),
    ADD COLUMN IF NOT EXISTS heating_fuel_type VARCHAR(50),
    ADD COLUMN IF NOT EXISTS air_conditioning VARCHAR(50),
    ADD COLUMN IF NOT EXISTS water VARCHAR(50),
    ADD COLUMN IF NOT EXISTS sewer VARCHAR(50),

    -- Amenities
    ADD COLUMN IF NOT EXISTS garage_type VARCHAR(50),
    ADD COLUMN IF NOT EXISTS garage_cars INTEGER,
    ADD COLUMN IF NOT EXISTS pool VARCHAR(50),
    ADD COLUMN IF NOT EXISTS fireplace VARCHAR(50),
    ADD COLUMN IF NOT EXISTS basement VARCHAR(50),
    ADD COLUMN IF NOT EXISTS amenities VARCHAR(100),
    ADD COLUMN IF NOT EXISTS amenities_2 VARCHAR(100),
    ADD COLUMN IF NOT EXISTS elevator VARCHAR(50),

    -- Quality & Condition
    ADD COLUMN IF NOT EXISTS building_quality_code VARCHAR(10),
    ADD COLUMN IF NOT EXISTS building_condition_code VARCHAR(10),
    ADD COLUMN IF NOT EXISTS quality_and_condition_source VARCHAR(50); 