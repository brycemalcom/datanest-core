-- MIGRATION: 010_complete_building_characteristics_final
-- GOAL: Add the final 6 Building Characteristics database columns for 100% completion (73/73)

ALTER TABLE datnest.properties
    -- Final 6 Building Characteristics columns
    ADD COLUMN IF NOT EXISTS comments_summary_building_cards TEXT,
    ADD COLUMN IF NOT EXISTS interior_walls_alt VARCHAR(50),
    ADD COLUMN IF NOT EXISTS number_of_stories INTEGER,
    ADD COLUMN IF NOT EXISTS standardized_land_use_code_building VARCHAR(10),
    ADD COLUMN IF NOT EXISTS type_construction_alt VARCHAR(50),
    ADD COLUMN IF NOT EXISTS zoning_building VARCHAR(20);

-- Add performance indexes for building analysis
CREATE INDEX IF NOT EXISTS idx_properties_number_of_stories ON datnest.properties(number_of_stories) WHERE number_of_stories IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_land_use_code_building ON datnest.properties(standardized_land_use_code_building) WHERE standardized_land_use_code_building IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_zoning_building ON datnest.properties(zoning_building) WHERE zoning_building IS NOT NULL;

-- Add documentation comments for building intelligence
COMMENT ON COLUMN datnest.properties.comments_summary_building_cards IS 'Summary comments from building assessment cards';
COMMENT ON COLUMN datnest.properties.interior_walls_alt IS 'Alternative interior walls specification for building context';
COMMENT ON COLUMN datnest.properties.number_of_stories IS 'Number of stories/floors in the building';
COMMENT ON COLUMN datnest.properties.standardized_land_use_code_building IS 'Land use code in building context';
COMMENT ON COLUMN datnest.properties.type_construction_alt IS 'Alternative construction type specification';
COMMENT ON COLUMN datnest.properties.zoning_building IS 'Zoning classification in building context'; 