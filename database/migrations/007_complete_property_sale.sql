-- MIGRATION: 007_complete_property_sale
-- GOAL: Add all 47 "Property Sale" fields to the properties table for complete market analysis capabilities

ALTER TABLE datnest.properties
    -- Last Transfer Fields
    ADD COLUMN IF NOT EXISTS lsale_book_number VARCHAR(10),
    ADD COLUMN IF NOT EXISTS lsale_page_number VARCHAR(10),
    ADD COLUMN IF NOT EXISTS lsale_document_number VARCHAR(20),
    ADD COLUMN IF NOT EXISTS lsale_document_type_code VARCHAR(2),
    ADD COLUMN IF NOT EXISTS lsale_price BIGINT,
    ADD COLUMN IF NOT EXISTS lsale_price_code VARCHAR(1),
    ADD COLUMN IF NOT EXISTS lsale_recording_date VARCHAR(8),
    ADD COLUMN IF NOT EXISTS lsale_reo_flag VARCHAR(1),
    ADD COLUMN IF NOT EXISTS lsale_distressed_sale_flag VARCHAR(1),
    ADD COLUMN IF NOT EXISTS last_transfer_date VARCHAR(8),

    -- Last Valid Sale Fields
    ADD COLUMN IF NOT EXISTS lvalid_book_number VARCHAR(10),
    ADD COLUMN IF NOT EXISTS lvalid_page_number VARCHAR(10),
    ADD COLUMN IF NOT EXISTS lvalid_document_number VARCHAR(20),
    ADD COLUMN IF NOT EXISTS lvalid_document_type_code VARCHAR(2),
    ADD COLUMN IF NOT EXISTS lvalid_price BIGINT,
    ADD COLUMN IF NOT EXISTS lvalid_price_code VARCHAR(1),
    ADD COLUMN IF NOT EXISTS lvalid_recording_date VARCHAR(8),
    ADD COLUMN IF NOT EXISTS lvalid_reo_flag VARCHAR(1),
    ADD COLUMN IF NOT EXISTS lvalid_distressed_sale_flag VARCHAR(1),
    ADD COLUMN IF NOT EXISTS last_sale_date VARCHAR(8),

    -- Prior Transfer Fields
    ADD COLUMN IF NOT EXISTS psale_book_number VARCHAR(10),
    ADD COLUMN IF NOT EXISTS psale_page_number VARCHAR(10),
    ADD COLUMN IF NOT EXISTS psale_document_number VARCHAR(20),
    ADD COLUMN IF NOT EXISTS psale_document_type_code VARCHAR(2),
    ADD COLUMN IF NOT EXISTS psale_price BIGINT,
    ADD COLUMN IF NOT EXISTS psale_price_code VARCHAR(1),
    ADD COLUMN IF NOT EXISTS psale_recording_date VARCHAR(8),
    ADD COLUMN IF NOT EXISTS psale_reo_flag VARCHAR(1),
    ADD COLUMN IF NOT EXISTS psale_distressed_sale_flag VARCHAR(1),
    ADD COLUMN IF NOT EXISTS prior_transfer_date VARCHAR(8),

    -- Prior Valid Sale Fields  
    ADD COLUMN IF NOT EXISTS pvalid_book_number VARCHAR(10),
    ADD COLUMN IF NOT EXISTS pvalid_page_number VARCHAR(10),
    ADD COLUMN IF NOT EXISTS pvalid_document_number VARCHAR(20),
    ADD COLUMN IF NOT EXISTS pvalid_document_type_code VARCHAR(2),
    ADD COLUMN IF NOT EXISTS pvalid_price BIGINT,
    ADD COLUMN IF NOT EXISTS pvalid_price_code VARCHAR(1),
    ADD COLUMN IF NOT EXISTS pvalid_recording_date VARCHAR(8),
    ADD COLUMN IF NOT EXISTS pvalid_reo_flag VARCHAR(1),
    ADD COLUMN IF NOT EXISTS pvalid_distressed_sale_flag VARCHAR(1),
    ADD COLUMN IF NOT EXISTS prior_sale_date VARCHAR(8),

    -- Assessment Record Fields
    ADD COLUMN IF NOT EXISTS recorders_document_number_from_assessment VARCHAR(20),
    ADD COLUMN IF NOT EXISTS recorders_book_number_from_assessment VARCHAR(10),
    ADD COLUMN IF NOT EXISTS recorders_page_number_from_assessment VARCHAR(10),
    ADD COLUMN IF NOT EXISTS recording_date_from_assessment VARCHAR(8),
    ADD COLUMN IF NOT EXISTS document_type_from_assessment VARCHAR(25),
    ADD COLUMN IF NOT EXISTS sales_price_from_assessment BIGINT,
    ADD COLUMN IF NOT EXISTS sales_price_code_from_assessment VARCHAR(1);

-- Add indexes for performance on sales analysis queries
CREATE INDEX IF NOT EXISTS idx_properties_lsale_price ON datnest.properties(lsale_price) WHERE lsale_price IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_lvalid_price ON datnest.properties(lvalid_price) WHERE lvalid_price IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_last_sale_date ON datnest.properties(last_sale_date) WHERE last_sale_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_sales_price_assessment ON datnest.properties(sales_price_from_assessment) WHERE sales_price_from_assessment IS NOT NULL;

-- Add comments for documentation
COMMENT ON COLUMN datnest.properties.lsale_price IS 'Last Transfer Price - whole dollars only';
COMMENT ON COLUMN datnest.properties.lvalid_price IS 'Last Valid Sale Price - arms length transactions only';
COMMENT ON COLUMN datnest.properties.psale_price IS 'Prior Transfer Price - whole dollars only';
COMMENT ON COLUMN datnest.properties.pvalid_price IS 'Prior Valid Sale Price - arms length transactions only';
COMMENT ON COLUMN datnest.properties.sales_price_from_assessment IS 'Sales price from county assessment roll'; 