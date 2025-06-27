-- DataNest Migration 012b: Add Missing MTG02 Purpose Field
-- Fix: Add mtg02_purpose_of_loan field that was mapped but not created
-- Engineer: Master Database Engineer
-- Date: June 27, 2025

SET search_path TO datnest, public;

-- Add missing MTG02 purpose field
ALTER TABLE properties ADD COLUMN IF NOT EXISTS mtg02_purpose_of_loan VARCHAR(100);

-- Add comment for field documentation
COMMENT ON COLUMN properties.mtg02_purpose_of_loan IS 'Second mortgage purpose/use of loan proceeds'; 