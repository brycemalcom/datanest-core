-- MIGRATION: 008_complete_building_characteristics_remaining
-- GOAL: Add the remaining 37 Building Characteristics fields for 100% category completion

ALTER TABLE datnest.properties
    -- Additional Building Areas & Indicators
    ADD COLUMN IF NOT EXISTS building_area DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS building_area_1_indicator VARCHAR(10),
    ADD COLUMN IF NOT EXISTS building_area_2 DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS building_area_2_indicator VARCHAR(10),
    ADD COLUMN IF NOT EXISTS building_area_3 DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS building_area_3_indicator VARCHAR(10),
    ADD COLUMN IF NOT EXISTS building_area_4 DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS building_area_4_indicator VARCHAR(10),
    ADD COLUMN IF NOT EXISTS building_area_5 DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS building_area_5_indicator VARCHAR(10),
    ADD COLUMN IF NOT EXISTS building_area_6 DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS building_area_6_indicator VARCHAR(10),
    ADD COLUMN IF NOT EXISTS building_area_7 DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS building_area_7_indicator VARCHAR(10),
    
    -- Building Classification & Systems
    ADD COLUMN IF NOT EXISTS air_conditioning_type VARCHAR(50),
    ADD COLUMN IF NOT EXISTS building_class VARCHAR(20),
    ADD COLUMN IF NOT EXISTS floor_cover_alt VARCHAR(50),
    ADD COLUMN IF NOT EXISTS main_building_area_indicator VARCHAR(10),
    ADD COLUMN IF NOT EXISTS no_of_buildings INTEGER,
    ADD COLUMN IF NOT EXISTS no_of_stories DECIMAL(4, 1),
    ADD COLUMN IF NOT EXISTS n_of_plumbing_fixtures INTEGER,
    ADD COLUMN IF NOT EXISTS other_rooms INTEGER,
    
    -- Extra Features & Improvements
    ADD COLUMN IF NOT EXISTS extra_features_1_area DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS extra_features_1_indicator VARCHAR(10),
    ADD COLUMN IF NOT EXISTS extra_features_2_area DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS extra_features_2_indicator VARCHAR(10),
    ADD COLUMN IF NOT EXISTS extra_features_3_area DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS extra_features_3_indicator VARCHAR(10),
    ADD COLUMN IF NOT EXISTS extra_features_4_area DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS extra_features_4_indicator VARCHAR(10),
    
    -- Other Improvements & Areas
    ADD COLUMN IF NOT EXISTS other_impr_building_area_1 DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS other_impr_building_area_2 DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS other_impr_building_area_3 DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS other_impr_building_area_4 DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS other_impr_building_area_5 DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS other_impr_building_indicator_1 VARCHAR(10),
    ADD COLUMN IF NOT EXISTS other_impr_building_indicator_2 VARCHAR(10),
    ADD COLUMN IF NOT EXISTS other_impr_building_indicator_3 VARCHAR(10),
    ADD COLUMN IF NOT EXISTS other_impr_building_indicator_4 VARCHAR(10),
    ADD COLUMN IF NOT EXISTS other_impr_building_indicator_5 VARCHAR(10),
    
    -- Additional Classification
    ADD COLUMN IF NOT EXISTS standardized_land_use_code_building VARCHAR(20),
    ADD COLUMN IF NOT EXISTS zoning_building VARCHAR(50),
    ADD COLUMN IF NOT EXISTS comments_summary_building_cards TEXT;

-- Add performance indexes for common building queries
CREATE INDEX IF NOT EXISTS idx_properties_building_class ON datnest.properties(building_class) WHERE building_class IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_building_area ON datnest.properties(building_area) WHERE building_area IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_no_of_buildings ON datnest.properties(no_of_buildings) WHERE no_of_buildings IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_standardized_land_use_building ON datnest.properties(standardized_land_use_code_building) WHERE standardized_land_use_code_building IS NOT NULL;

-- Add documentation comments
COMMENT ON COLUMN datnest.properties.building_area IS 'Primary building area measurement';
COMMENT ON COLUMN datnest.properties.building_class IS 'Building classification code';
COMMENT ON COLUMN datnest.properties.no_of_buildings IS 'Number of buildings on the property';
COMMENT ON COLUMN datnest.properties.comments_summary_building_cards IS 'Summary comments from building assessment cards'; 