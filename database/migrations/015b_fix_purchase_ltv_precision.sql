-- DataNest Migration 015b: Fix Purchase LTV Precision Issue
-- Phase 2E: Quick fix for purchase_ltv precision overflow
-- Engineer: Master Database Engineer
-- Date: June 27, 2025
-- Issue: purchase_ltv field precision too restrictive for data values

SET search_path TO datnest, public;

-- Fix purchase_ltv precision to accommodate larger values
ALTER TABLE properties ALTER COLUMN purchase_ltv TYPE DECIMAL(10,2);

-- Update comment
COMMENT ON COLUMN properties.purchase_ltv IS 'Purchase loan-to-value ratio (decimal 10,2 for proper range support)';

-- Migration complete
SELECT 'Migration 015b: Fixed purchase_ltv precision issue' AS status; 