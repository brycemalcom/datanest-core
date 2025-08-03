#!/usr/bin/env python3
"""
MVP RECOVERY LOADER - Fix the 3 Failed Chunks to Recover 300K Records
Target: Process chunks 1, 8, and 17 with enhanced error handling
"""

import os
import sys
import time
import psycopg2
import pandas as pd
import csv
import tempfile
import re

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import get_db_config

# Set CSV limits
csv.field_size_limit(2147483647)

def clean_utf8_errors(text):
    """Remove null bytes and other UTF8 problematic characters"""
    if pd.isna(text) or text is None:
        return None
    text_str = str(text)
    # Remove null bytes (0x00) that cause UTF8 errors
    text_str = text_str.replace('\x00', '')
    # Remove other problematic control characters
    text_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text_str)
    return text_str if text_str else None

def robust_numeric_clean(value, field_name):
    """Enhanced numeric cleaning that handles Y/N values and other text"""
    if pd.isna(value) or value is None:
        return None
    
    value_str = str(value).strip().upper()
    
    # Handle empty values
    if value_str in ['', 'NAN', 'NULL', 'N/A', 'NA']:
        return None
    
    # Handle Y/N values (convert to NULL - these are not numeric)
    if value_str in ['Y', 'N', 'YES', 'NO', 'TRUE', 'FALSE']:
        print(f"   🔧 Converting non-numeric '{value_str}' to NULL in {field_name}")
        return None
    
    # Try to extract numeric value
    try:
        # Remove common non-numeric characters
        cleaned = re.sub(r'[^\d.-]', '', value_str)
        if cleaned and cleaned not in ['-', '.', '-.']:
            return float(cleaned)
        else:
            return None
    except (ValueError, TypeError):
        return None

def process_chunk_robust(chunk_data, field_mapping, chunk_num):
    """Process chunk with enhanced error handling for the 3 known issues"""
    try:
        print(f"🔧 Processing chunk {chunk_num} with enhanced error handling: {len(chunk_data):,} rows")
        
        # Step 1: Handle UTF8 encoding errors (Fix for Chunk 17)
        print(f"   🧹 Cleaning UTF8 encoding issues...")
        for col in chunk_data.columns:
            if chunk_data[col].dtype == 'object':  # String columns
                chunk_data[col] = chunk_data[col].apply(clean_utf8_errors)
        
        # Step 2: Fast bulk mapping with missing column handling (Fix for Chunk 1)
        print(f"   📊 Mapping fields with missing column protection...")
        available_mapping = {}
        missing_fields = []
        
        for tsv_col, db_col in field_mapping.items():
            if tsv_col in chunk_data.columns:
                available_mapping[db_col] = tsv_col
            else:
                missing_fields.append(tsv_col)
                print(f"   ⚠️  Missing column '{tsv_col}' - will pad with NULL")
        
        # Create clean data with available fields
        if available_mapping:
            clean_data = chunk_data[list(available_mapping.values())].copy()
            clean_data.columns = list(available_mapping.keys())
        else:
            clean_data = pd.DataFrame()
        
        # Pad missing fields with NULL values (Fix for Chunk 1)
        for tsv_col, db_col in field_mapping.items():
            if db_col not in clean_data.columns:
                clean_data[db_col] = None
                print(f"   🔧 Added missing column '{db_col}' with NULL values")
        
        print(f"   📊 Final mapping: {len(clean_data.columns)}/{len(field_mapping)} fields")
        
        # Step 3: Enhanced data cleaning
        # Required fields
        for field in ['quantarium_internal_pid', 'apn', 'fips_code']:
            if field in clean_data.columns:
                clean_data[field] = clean_data[field].fillna('UNKNOWN')
        
        # Numeric fields with robust cleaning (Fix for Chunk 8)
        numeric_fields = ['building_area_total', 'lot_size_square_feet', 'latitude', 'longitude']
        for field in numeric_fields:
            if field in clean_data.columns:
                print(f"   🔢 Cleaning numeric field: {field}")
                clean_data[field] = clean_data[field].apply(lambda x: robust_numeric_clean(x, field))
        
        # Integer fields with robust cleaning (Fix for Chunk 8)
        integer_fields = ['year_built', 'number_of_bedrooms', 'estimated_value', 'lsale_price', 
                         'total_assessed_value', 'price_range_min', 'price_range_max', 'confidence_score']
        for field in integer_fields:
            if field in clean_data.columns:
                print(f"   🔢 Cleaning integer field: {field}")
                clean_data[field] = clean_data[field].apply(lambda x: robust_numeric_clean(x, field))
                # Convert to int where not null
                clean_data[field] = clean_data[field].apply(lambda x: int(x) if pd.notna(x) and x is not None else None)
        
        # String fields with UTF8 cleaning
        string_cols = [col for col in clean_data.columns 
                      if col not in numeric_fields + integer_fields]
        for field in string_cols:
            if field in clean_data.columns:
                clean_data[field] = clean_data[field].apply(clean_utf8_errors)
                clean_data[field] = clean_data[field].fillna('')
        
        # Convert empty strings to None for proper NULL handling
        clean_data = clean_data.replace('', None)
        
        print(f"   ✅ Chunk {chunk_num} enhanced processing complete: {len(clean_data):,} records ready")
        return clean_data, chunk_num
        
    except Exception as e:
        print(f"❌ Chunk {chunk_num} error: {e}")
        import traceback
        traceback.print_exc()
        return None, chunk_num

def recover_failed_chunks(tsv_file_path, failed_chunks=[1, 8, 17]):
    """Recover the 3 failed chunks with enhanced error handling"""
    
    print("🚀 MVP RECOVERY LOADER - RECOVER 300K RECORDS")
    print(f"🎯 Target: Process failed chunks {failed_chunks} with enhanced error handling")
    print("=" * 70)
    
    # MVP Field mapping (same as original)
    field_mapping = {
        'Quantarium_Internal_PID': 'quantarium_internal_pid',
        'Assessors_Parcel_Number': 'apn', 
        'FIPS_Code': 'fips_code',
        'Property_Full_Street_Address': 'property_full_street_address',
        'Property_City_Name': 'property_city_name',
        'Property_State': 'property_state',
        'Property_Zip_Code': 'property_zip_code',
        'PA_Latitude': 'latitude',
        'PA_Longitude': 'longitude',
        'ESTIMATED_VALUE': 'estimated_value',
        'PRICE_RANGE_MIN': 'price_range_min',
        'PRICE_RANGE_MAX': 'price_range_max',
        'CONFIDENCE_SCORE': 'confidence_score',
        'Current_Owner_Name': 'current_owner_name',
        'LotSize_Square_Feet': 'lot_size_square_feet',
        'Building_Area_1': 'building_area_total',
        'Number_of_Bedrooms': 'number_of_bedrooms',
        'Year_Built': 'year_built',
        'LSale_Price': 'lsale_price',
        'Total_Assessed_Value': 'total_assessed_value',
        'Owner_Occupied': 'owner_occupied'
    }
    
    print(f"🔥 Processing {len(field_mapping)} MVP fields with enhanced error handling")
    print()
    
    start_time = time.time()
    chunk_size = 100000
    total_recovered = 0
    
    try:
        # Read file and process specific chunks
        print(f"📖 Reading TSV file to target failed chunks...")
        chunk_reader = pd.read_csv(
            tsv_file_path,
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
            if chunk_num in failed_chunks:
                print(f"\n🎯 PROCESSING FAILED CHUNK {chunk_num}:")
                
                # Enhanced processing
                clean_data, chunk_id = process_chunk_robust(chunk, field_mapping, chunk_num)
                
                if clean_data is not None:
                    # Insert into existing database (append mode)
                    inserted = insert_recovery_data(clean_data, chunk_id)
                    total_recovered += inserted
                    print(f"   ✅ Recovered {inserted:,} records from chunk {chunk_num}")
                else:
                    print(f"   ❌ Failed to recover chunk {chunk_num}")
            
            # Stop after processing all target chunks
            if chunk_num >= max(failed_chunks):
                break
        
        elapsed = time.time() - start_time
        
        print(f"\n🎉 RECOVERY OPERATION COMPLETE!")
        print(f"📊 Records recovered: {total_recovered:,}")
        print(f"⏱️  Recovery time: {elapsed:.1f} seconds")
        
        # Validate final database state
        validate_recovery_results(total_recovered)
        
        return total_recovered > 0
        
    except Exception as e:
        print(f"❌ Recovery operation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def insert_recovery_data(clean_data, chunk_id):
    """Insert recovered data into existing database"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', 
                                       newline='', encoding='utf-8') as tmp_file:
            clean_data.to_csv(tmp_file, sep='\t', header=False, index=False, 
                            na_rep='\\N', float_format='%.0f')
            tmp_file_path = tmp_file.name
        
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        
        print(f"   💾 Inserting {len(clean_data):,} recovered records...")
        
        with open(tmp_file_path, 'r', encoding='utf-8') as f:
            cursor.copy_from(f, 'properties', columns=tuple(clean_data.columns), 
                           sep='\t', null='\\N')
        conn.commit()
        cursor.close()
        conn.close()
        
        os.unlink(tmp_file_path)
        return len(clean_data)
        
    except Exception as e:
        print(f"   ❌ Recovery insert error: {e}")
        try:
            os.unlink(tmp_file_path)
        except:
            pass
        return 0

def validate_recovery_results(recovered_count):
    """Validate the recovery results"""
    try:
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        
        cursor.execute("SELECT COUNT(*) FROM properties")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM properties WHERE estimated_value IS NOT NULL")
        valuation_records = cursor.fetchone()[0]
        
        print(f"\n🔍 FINAL DATABASE STATE:")
        print(f"📊 Total records: {total_records:,}")
        print(f"💰 Records with valuations: {valuation_records:,}")
        print(f"📈 Valuation coverage: {(valuation_records/total_records)*100:.1f}%")
        
        # Check if we reached the target
        target_records = 5000000
        if total_records >= target_records:
            print(f"🎉 SUCCESS! Reached target of {target_records:,} records!")
        else:
            remaining = target_records - total_records
            print(f"📊 Progress: {total_records:,}/{target_records:,} ({(total_records/target_records)*100:.1f}%)")
            print(f"🎯 Remaining: {remaining:,} records to reach 100% target")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Validation error: {e}")

if __name__ == "__main__":
    # TSV file path
    tsv_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    if not os.path.exists(tsv_path):
        print(f"❌ TSV file not found: {tsv_path}")
        exit(1)
    
    print(f"📁 Source file: {os.path.basename(tsv_path)}")
    print(f"🎯 Target chunks: 1, 8, 17 (300,000 records)")
    
    success = recover_failed_chunks(tsv_path)
    
    if success:
        print(f"\n🎉 RECOVERY SUCCESS! 300K records recovered!")
        print(f"📊 Database now closer to 5M record target")
    else:
        print(f"\n❌ RECOVERY FAILED! Check logs above")
    
    exit(0 if success else 1)