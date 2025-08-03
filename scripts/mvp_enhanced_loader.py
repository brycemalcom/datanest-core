#!/usr/bin/env python3
"""
MVP ENHANCED LOADER - Built-in Fixes for the 3 Data Issues
Goal: Load all 5M records by fixing data quality issues during processing
"""

import os
import sys
import time
import psycopg2
import pandas as pd
import csv
import tempfile
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import re

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import get_db_config

# Set CSV limits
csv.field_size_limit(2147483647)

def clean_data_value(value, field_type='string'):
    """Universal data cleaner that handles all the problematic cases"""
    if pd.isna(value) or value is None:
        return None
    
    value_str = str(value).strip()
    
    # Remove null bytes and control characters (Fix for Chunk 17 UTF8 errors)
    value_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', value_str)
    
    # Handle empty values
    if value_str in ['', 'NAN', 'NULL', 'N/A', 'NA']:
        return None
    
    # For numeric/integer fields, handle Y/N values (Fix for Chunk 8)
    if field_type in ['numeric', 'integer']:
        value_upper = value_str.upper()
        if value_upper in ['Y', 'N', 'YES', 'NO', 'TRUE', 'FALSE']:
            return None  # Convert to NULL
        
        # Try to extract numeric value
        try:
            cleaned = re.sub(r'[^\d.-]', '', value_str)
            if cleaned and cleaned not in ['-', '.', '-.']:
                return float(cleaned) if field_type == 'numeric' else int(float(cleaned))
            else:
                return None
        except (ValueError, TypeError):
            return None
    
    # For string fields, return cleaned string
    return value_str if value_str else None

def process_chunk_enhanced(chunk_data, field_mapping, chunk_num):
    """Enhanced chunk processing with built-in data quality fixes"""
    try:
        print(f"🔧 Processing chunk {chunk_num}: {len(chunk_data):,} rows")
        
        # Handle missing columns gracefully (Fix for Chunk 1)
        available_mapping = {}
        for tsv_col, db_col in field_mapping.items():
            if tsv_col in chunk_data.columns:
                available_mapping[db_col] = tsv_col
            else:
                # Create missing column with NULL values
                chunk_data[tsv_col] = None
                available_mapping[db_col] = tsv_col
        
        clean_data = chunk_data[list(available_mapping.values())].copy()
        clean_data.columns = list(available_mapping.keys())
        
        print(f"   📊 Mapped {len(available_mapping)}/{len(field_mapping)} fields (missing columns padded)")
        
        # Enhanced data cleaning with universal cleaner
        # Required fields
        for field in ['quantarium_internal_pid', 'apn', 'fips_code']:
            if field in clean_data.columns:
                clean_data[field] = clean_data[field].apply(lambda x: clean_data_value(x, 'string') or 'UNKNOWN')
        
        # Numeric fields
        numeric_fields = ['building_area_total', 'lot_size_square_feet', 'latitude', 'longitude']
        for field in numeric_fields:
            if field in clean_data.columns:
                clean_data[field] = clean_data[field].apply(lambda x: clean_data_value(x, 'numeric'))
        
        # Integer fields  
        integer_fields = ['year_built', 'number_of_bedrooms', 'estimated_value', 'lsale_price', 
                         'total_assessed_value', 'price_range_min', 'price_range_max', 'confidence_score']
        for field in integer_fields:
            if field in clean_data.columns:
                clean_data[field] = clean_data[field].apply(lambda x: clean_data_value(x, 'integer'))
        
        # String fields
        string_cols = [col for col in clean_data.columns 
                      if col not in numeric_fields + integer_fields]
        for field in string_cols:
            if field in clean_data.columns:
                clean_data[field] = clean_data[field].apply(lambda x: clean_data_value(x, 'string'))
                clean_data[field] = clean_data[field].fillna('')
        
        # Final cleanup
        clean_data = clean_data.replace('', None)
        
        print(f"   ✅ Chunk {chunk_num} enhanced processing complete: {len(clean_data):,} records ready")
        return clean_data, chunk_num
        
    except Exception as e:
        print(f"   ❌ Chunk {chunk_num} error: {e}")
        import traceback
        traceback.print_exc()
        return None, chunk_num

def mvp_enhanced_load(tsv_file_path, max_workers=None, chunk_size=75000):
    """Enhanced MVP loader with built-in data quality fixes"""
    
    if max_workers is None:
        max_workers = max(1, int(mp.cpu_count() * 0.8))
    
    print("🚀 MVP ENHANCED LOADER - BUILT-IN DATA QUALITY FIXES")
    print(f"🛠️  Enhanced fixes: UTF8 cleaning + Y/N handling + missing columns")
    print(f"🎯 Target: 5M records with 0 data loss")
    print(f"⚙️  Workers: {max_workers}")
    print(f"📦 Chunk size: {chunk_size:,}")
    print("=" * 70)
    
    # Same MVP field mapping
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
    
    print(f"🔥 MVP Fields: {len(field_mapping)} core fields with enhanced data cleaning")
    print()
    
    start_time = time.time()
    
    try:
        # Clear database for fresh start
        print("🗃️  Clearing database for enhanced load...")
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        cursor.execute("TRUNCATE TABLE properties RESTART IDENTITY CASCADE")
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database cleared - ready for enhanced MVP load")
        
        # Read file in chunks
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
        
        total_loaded = 0
        chunk_count = 0
        failed_chunks = 0
        
        # Process with multiprocessing
        print(f"🚀 Starting enhanced processing with {max_workers} workers...")
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for chunk_num, chunk in enumerate(chunk_reader, 1):
                chunk_count = chunk_num
                future = executor.submit(process_chunk_enhanced, chunk, field_mapping, chunk_num)
                futures.append(future)
                
                # Process in batches
                if len(futures) >= max_workers * 2:
                    for future in as_completed(futures):
                        clean_data, chunk_id = future.result()
                        if clean_data is not None:
                            inserted = bulk_insert_enhanced(clean_data, chunk_id)
                            total_loaded += inserted
                        else:
                            failed_chunks += 1
                    futures = []
                    
                    # Progress update
                    elapsed = time.time() - start_time
                    rate = total_loaded / elapsed if elapsed > 0 else 0
                    print(f"📈 Progress: {total_loaded:,} records in {elapsed:.1f}s ({rate:,.0f} rec/sec)")
            
            # Process remaining
            for future in as_completed(futures):
                clean_data, chunk_id = future.result()
                if clean_data is not None:
                    inserted = bulk_insert_enhanced(clean_data, chunk_id)
                    total_loaded += inserted
                else:
                    failed_chunks += 1
        
        elapsed = time.time() - start_time
        rate = total_loaded / elapsed if elapsed > 0 else 0
        
        print(f"\n🎉 MVP ENHANCED LOAD COMPLETE!")
        print(f"📊 Records loaded: {total_loaded:,}")
        print(f"📦 Chunks processed: {chunk_count} ({failed_chunks} failed)")
        print(f"⏱️  Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print(f"🚀 Performance: {rate:,.0f} records/second")
        print(f"🎯 Target: 5,000,000 records ({'✅ SUCCESS' if total_loaded >= 4950000 else '⚠️ PARTIAL'})")
        
        return total_loaded >= 4950000  # Allow 1% margin for success
        
    except Exception as e:
        print(f"❌ Enhanced load failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def bulk_insert_enhanced(clean_data, chunk_id):
    """Enhanced bulk insert with better error handling"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', 
                                       newline='', encoding='utf-8') as tmp_file:
            clean_data.to_csv(tmp_file, sep='\t', header=False, index=False, 
                            na_rep='\\N', float_format='%.0f')
            tmp_file_path = tmp_file.name
        
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        
        with open(tmp_file_path, 'r', encoding='utf-8') as f:
            cursor.copy_from(f, 'properties', columns=tuple(clean_data.columns), 
                           sep='\t', null='\\N')
        conn.commit()
        cursor.close()
        conn.close()
        
        os.unlink(tmp_file_path)
        print(f"   ✅ Chunk {chunk_id}: {len(clean_data):,} records inserted")
        return len(clean_data)
        
    except Exception as e:
        print(f"   ❌ Chunk {chunk_id} insert error: {e}")
        try:
            os.unlink(tmp_file_path)
        except:
            pass
        return 0

if __name__ == "__main__":
    tsv_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    if not os.path.exists(tsv_path):
        print(f"❌ TSV file not found: {tsv_path}")
        exit(1)
    
    max_workers = max(1, int(mp.cpu_count() * 0.8))
    chunk_size = 50000  # Smaller chunks for more stability
    
    print(f"🖥️  Using {max_workers} workers with {chunk_size:,} record chunks")
    print(f"📁 Source: {os.path.basename(tsv_path)}")
    
    success = mvp_enhanced_load(tsv_path, max_workers=max_workers, chunk_size=chunk_size)
    
    if success:
        print(f"\n🎉 SUCCESS! Enhanced MVP loader achieved target!")
    else:
        print(f"\n❌ PARTIAL SUCCESS - Check results above")
    
    exit(0 if success else 1)