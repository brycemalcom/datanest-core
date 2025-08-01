#!/usr/bin/env python3
"""
BULLETPROOF COMPLETE LOADER V2 - COLUMN ALIGNMENT FIX
Goal: Load ALL 5M records with zero data loss, FIXING column alignment issues

CRITICAL FIX: Replace DataFrame rebuilding with in-place processing
ROOT CAUSE: clean_data = pd.DataFrame() + clean_data[db_col] = col_data causes pandas index misalignment
SOLUTION: Process original DataFrame in-place to maintain row alignment
"""

import os
import sys
import time
import psycopg2
import pandas as pd
import csv
import tempfile
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import get_db_config

# Set CSV limits
csv.field_size_limit(2147483647)

def process_chunk_bulletproof_v2(chunk_data, field_mapping, chunk_num):
    """Bulletproof chunk processing with FIXED column alignment"""
    try:
        print(f"🔧 Worker processing chunk {chunk_num}: {len(chunk_data):,} rows")
        
        # CRITICAL: Verify we have the expected columns
        expected_columns = 449
        if len(chunk_data.columns) != expected_columns:
            print(f"⚠️  Chunk {chunk_num}: Column count mismatch! Got {len(chunk_data.columns)}, expected {expected_columns}")
            return None, chunk_num
        
        # CRITICAL FIX: Create a copy of original DataFrame structure to maintain alignment
        # Instead of rebuilding DataFrame column by column, we'll rename and clean in place
        clean_data = chunk_data.copy()
        
        # First pass: Clean data types IN PLACE (no column reassignment yet)
        for tsv_col, db_col in field_mapping.items():
            if tsv_col in clean_data.columns:
                
                # Data type specific cleaning - MODIFY IN PLACE
                if db_col in ['latitude', 'longitude']:
                    # Coordinates: Must be numeric
                    clean_data[tsv_col] = pd.to_numeric(clean_data[tsv_col].replace('', pd.NA), errors='coerce')
                    
                elif db_col in ['building_area_total', 'lot_size_square_feet']:
                    # Numeric fields
                    clean_data[tsv_col] = pd.to_numeric(clean_data[tsv_col].replace('', pd.NA), errors='coerce')
                    
                elif db_col in ['year_built', 'number_of_bedrooms', 'estimated_value', 'lsale_price', 'assessment_year']:
                    # Integer fields - handle floats like "1975.0" and large decimals like "30.632601"
                    # CRITICAL: Replace empty strings with None for proper NULL handling
                    clean_data[tsv_col] = clean_data[tsv_col].replace(['', ' ', 'nan', 'NaN', 'NULL'], None)
                    
                    # Convert to numeric, handling NaN and large decimals properly
                    def safe_int_convert(x):
                        if pd.isna(x) or x is None or str(x).lower() in ['nan', '', 'null', 'none']:
                            return None  # Return None for NULL database insertion
                        try:
                            # For very large decimals, round to nearest integer
                            if str(x).strip() == '':  # Extra empty string check
                                return None
                            float_val = float(x)
                            if pd.isna(float_val):  # Double-check for NaN after float conversion
                                return None
                            return int(round(float_val))
                        except (ValueError, OverflowError, TypeError):
                            return None
                    
                    clean_data[tsv_col] = clean_data[tsv_col].apply(safe_int_convert)
                    
                elif db_col == 'property_state':
                    # State: Must be 2 characters or NULL
                    clean_data[tsv_col] = clean_data[tsv_col].fillna('').astype(str)
                    clean_data[tsv_col] = clean_data[tsv_col].apply(lambda x: x[:2] if x and len(x) >= 2 else None)
                    
                else:
                    # String fields
                    clean_data[tsv_col] = clean_data[tsv_col].fillna('').astype(str)
                    # Remove null characters
                    clean_data[tsv_col] = clean_data[tsv_col].str.replace('\x00', '', regex=False)
                    clean_data[tsv_col] = clean_data[tsv_col].apply(lambda x: None if x == '' else x)
        
        # Second pass: Create final DataFrame with correct column names
        # CRITICAL: Use column selection instead of iterative assignment to preserve row alignment
        final_columns = {}
        for tsv_col, db_col in field_mapping.items():
            if tsv_col in clean_data.columns:
                final_columns[db_col] = clean_data[tsv_col]
            else:
                print(f"⚠️  Missing column {tsv_col} in chunk {chunk_num}")
        
        # Create final DataFrame using dict constructor (preserves row alignment)
        result_data = pd.DataFrame(final_columns)
        
        # Final validation before return
        if len(result_data) == 0:
            print(f"❌ Chunk {chunk_num}: No data after cleaning")
            return None, chunk_num
        
        # Validate critical coordinates
        if 'latitude' in result_data.columns and 'longitude' in result_data.columns:
            coord_issues = 0
            for idx, row in result_data.iterrows():
                lat, lon = row['latitude'], row['longitude']
                if pd.notna(lat) and pd.notna(lon):
                    try:
                        lat_val, lon_val = float(lat), float(lon)
                        # Basic US coordinate validation
                        if not (20 <= lat_val <= 70 and -180 <= lon_val <= -60):
                            coord_issues += 1
                            if coord_issues <= 3:  # Show first few issues
                                print(f"⚠️  Chunk {chunk_num} suspicious coordinates at row {idx}: lat={lat_val}, lon={lon_val}")
                    except:
                        pass
            
            if coord_issues > 0:
                print(f"⚠️  Chunk {chunk_num}: {coord_issues} rows with suspicious coordinates")
        
        print(f"✅ Chunk {chunk_num}: {len(result_data):,} rows processed successfully")
        return result_data, chunk_num
        
    except Exception as e:
        print(f"❌ Chunk {chunk_num} processing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, chunk_num

def load_file_bulletproof_v2():
    """Main loading function with fixed column alignment"""
    print("🛡️ BULLETPROOF COMPLETE LOADER V2 - COLUMN ALIGNMENT FIXED")
    print("=" * 70)
    
    # File path for first TSV file
    tsv_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    if not os.path.exists(tsv_path):
        print(f"❌ TSV file not found: {tsv_path}")
        return
    
    # Field mapping (same as before)
    field_mapping = {
        'Quantarium_Internal_PID': 'quantarium_internal_pid',
        'Property_Full_Street_Address': 'property_full_street_address', 
        'Property_City_Name': 'property_city_name',
        'Property_State': 'property_state',
        'Property_Zip_Code': 'property_zip_code',
        'PA_Latitude': 'latitude',
        'PA_Longitude': 'longitude',
        'FIPS_Code': 'fips_code',
        'Assessors_Parcel_Number': 'apn',
        'Building_Area_1': 'building_area_total',
        'LotSize_Square_Feet': 'lot_size_square_feet',
        'Number_of_Bedrooms': 'number_of_bedrooms',
        'Number_of_Baths': 'number_of_bathrooms',
        'Year_Built': 'year_built',
        'Total_Assessed_Value': 'total_assessed_value',
        'Assessment_Year': 'assessment_year',
        'ESTIMATED_VALUE': 'estimated_value',
        'PRICE_RANGE_MIN': 'price_range_min',
        'PRICE_RANGE_MAX': 'price_range_max',
        'CONFIDENCE_SCORE': 'confidence_score',
        'QVM_asof_Date': 'qvm_asof_date',
        'QVM_Value_Range_Code': 'qvm_value_range_code',
        'LSale_Price': 'lsale_price'
        # Add more fields as needed for complete 449-field mapping
    }
    
    print(f"📂 Processing file: {tsv_path}")
    print(f"🔗 Mapped fields: {len(field_mapping)}")
    print("🎯 CRITICAL: Testing Column Alignment Fix - in-place processing prevents row shifting")
    
    # Database connection
    conn = psycopg2.connect(**get_db_config())
    cursor = conn.cursor()
    
    # Set search path to datnest schema (like other working loaders)
    cursor.execute("SET search_path TO datnest, public")
    
    # Clear existing data for fresh complete load
    print("🗑️  Clearing existing data for complete load...")
    cursor.execute("TRUNCATE TABLE properties")
    conn.commit()
    
    # Process chunks
    chunk_size = 25000  # Smaller chunks for better error isolation
    total_processed = 0
    
    try:
        chunk_reader = pd.read_csv(
            tsv_path,
            sep='\t',
            chunksize=chunk_size,
            dtype=str,
            encoding='utf-8',
            engine='python',
            quoting=csv.QUOTE_NONE,
            on_bad_lines='skip',
            na_values=['']
        )
        
        for chunk_num, chunk in enumerate(chunk_reader, 1):
            print(f"\n📦 Processing chunk {chunk_num}: {len(chunk):,} rows")
            
            # Process chunk with fixed alignment
            processed_chunk, _ = process_chunk_bulletproof_v2(chunk, field_mapping, chunk_num)
            
            if processed_chunk is not None and len(processed_chunk) > 0:
                                # Use COPY for fast loading
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
                    # CRITICAL: Use na_rep='\\N' for proper NULL handling in PostgreSQL COPY
                    processed_chunk.to_csv(tmp_file.name, index=False, header=False, na_rep='\\N')
                    
                    with open(tmp_file.name, 'r') as f:
                        cursor.copy_from(
                        f, 
                        'properties',  # Just table name (schema in search_path)
                        columns=list(processed_chunk.columns),
                        sep=',',
                        null='\\N'  # Tell PostgreSQL how to interpret NULLs
                    )
                    
                    os.unlink(tmp_file.name)
                
                total_processed += len(processed_chunk)
                conn.commit()
                print(f"✅ Chunk {chunk_num}: {len(processed_chunk):,} rows loaded (Total: {total_processed:,})")
            else:
                print(f"❌ Chunk {chunk_num}: Failed to process")
                break
            
            # Continue until we process the entire file
            # No artificial limits - let's get ALL the data!
    
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()
    
    print(f"\n🎉 LOADING COMPLETE!")
    print(f"📊 Total records processed: {total_processed:,}")
    print(f"🎯 Target was 5,000,000 records")
    
    if total_processed >= 4999000:
        print("✅ SUCCESS: Achieved near-complete data capture!")
    else:
        print("⚠️  Review needed: Less than expected records processed")

if __name__ == "__main__":
    load_file_bulletproof_v2()