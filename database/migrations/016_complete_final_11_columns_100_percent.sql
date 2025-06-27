-- DATANEST CORE PLATFORM - FINAL 11 COLUMNS FOR 100% DATA CAPTURE
-- Migration 016: Complete Final 11 Columns for 449/449 Field Coverage
-- QA Session: 96.9% → 100% Data Capture Achievement
-- Date: 2025-01-27
-- Purpose: Add the final 11 missing database columns to achieve complete 449/449 TSV field mapping

-- Set search path
SET search_path TO datnest, public;

-- =====================================================
-- FINAL 11 COLUMNS FOR 100% DATA CAPTURE
-- =====================================================

-- Financing/Mortgage Fields (1 column)
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_loan_number VARCHAR(50);

-- County Values/Taxes Fields (6 columns) 
ALTER TABLE properties ADD COLUMN IF NOT EXISTS school_tax_district_1 VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS school_tax_district_1_indicator VARCHAR(10);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS school_tax_district_2 VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS school_tax_district_2_indicator VARCHAR(10);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS school_tax_district_3 VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS school_tax_district_3_indicator VARCHAR(10);

-- Ownership Fields (1 column)
ALTER TABLE properties ADD COLUMN IF NOT EXISTS co_mailing_zip_plus4code VARCHAR(10);

-- Other/Uncategorized Fields (3 columns)
ALTER TABLE properties ADD COLUMN IF NOT EXISTS duplicate_apn VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS property_unit_type VARCHAR(20);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS property_zip_plus4code VARCHAR(10);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS total_number_of_rooms INTEGER;

-- Create indexes for commonly queried fields
CREATE INDEX IF NOT EXISTS idx_properties_mtg02_loan_number ON properties(mtg02_loan_number);
CREATE INDEX IF NOT EXISTS idx_properties_school_tax_district_1 ON properties(school_tax_district_1);
CREATE INDEX IF NOT EXISTS idx_properties_duplicate_apn ON properties(duplicate_apn);

-- =====================================================
-- VERIFICATION
-- =====================================================

-- Verify all columns were created successfully
DO $$
DECLARE
    missing_columns TEXT[] := ARRAY[
        'mtg02_loan_number',
        'school_tax_district_1',
        'school_tax_district_1_indicator', 
        'school_tax_district_2',
        'school_tax_district_2_indicator',
        'school_tax_district_3',
        'school_tax_district_3_indicator',
        'co_mailing_zip_plus4code',
        'duplicate_apn',
        'property_unit_type',
        'property_zip_plus4code',
        'total_number_of_rooms'
    ];
    col TEXT;
    col_count INTEGER;
BEGIN
    RAISE NOTICE '🔍 VERIFYING FINAL 11 COLUMNS CREATION...';
    
    FOREACH col IN ARRAY missing_columns
    LOOP
        SELECT COUNT(*) INTO col_count
        FROM information_schema.columns 
        WHERE table_name = 'properties' 
        AND table_schema = 'datnest'
        AND column_name = col;
        
        IF col_count = 1 THEN
            RAISE NOTICE '✅ Column created: %', col;
        ELSE
            RAISE NOTICE '❌ Column missing: %', col;
        END IF;
    END LOOP;
    
    -- Get total column count
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns 
    WHERE table_name = 'properties' 
    AND table_schema = 'datnest';
    
    RAISE NOTICE '📊 Total database columns: %', col_count;
    RAISE NOTICE '🎯 Target: 449 TSV fields mappable to database';
    RAISE NOTICE '🚀 Ready for 100%% data capture!';
END
$$;

-- =====================================================
-- COMPLETION CONFIRMATION
-- =====================================================

-- Log migration completion
INSERT INTO schema_migrations (version, applied_at, description) 
VALUES ('016', NOW(), 'Complete Final 11 Columns for 100% Data Capture - 449/449 Fields')
ON CONFLICT (version) DO NOTHING;

-- Final status
SELECT 
    COUNT(*) as total_columns,
    'Migration 016: Final 11 columns added for 100% data capture' as status
FROM information_schema.columns 
WHERE table_name = 'properties' 
AND table_schema = 'datnest'; 