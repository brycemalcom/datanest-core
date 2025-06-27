#!/usr/bin/env python3
"""
TURBO ALABAMA LOADER - High Performance Multiprocessing
Goal: Load 5M records in under 1 hour using parallel processing
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
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import get_db_config

# Set CSV limits
csv.field_size_limit(2147483647)

def process_chunk(chunk_data, field_mapping, chunk_num):
    """Process a single chunk in parallel"""
    try:
        print(f"🔧 Worker processing chunk {chunk_num}: {len(chunk_data):,} rows")
        
        # Fast bulk mapping - no fragmentation
        available_mapping = {db_col: tsv_col for tsv_col, db_col in field_mapping.items() 
                            if tsv_col in chunk_data.columns}
        
        clean_data = chunk_data[list(available_mapping.values())].copy()
        clean_data.columns = list(available_mapping.keys())
        
        # Fast data cleaning using vectorized operations
        # Required fields
        for field in ['quantarium_internal_pid', 'apn', 'fips_code']:
            if field in clean_data.columns:
                clean_data[field] = clean_data[field].fillna('UNKNOWN')
        
        # Numeric fields - vectorized
        numeric_fields = ['building_area_total', 'lot_size_square_feet', 'latitude', 'longitude']
        for field in numeric_fields:
            if field in clean_data.columns:
                clean_data[field] = pd.to_numeric(clean_data[field].replace('', pd.NA), errors='coerce')
        
        # Integer fields - vectorized
        integer_fields = ['year_built', 'number_of_bedrooms', 'estimated_value', 'lsale_price']
        for field in integer_fields:
            if field in clean_data.columns:
                clean_data[field] = pd.to_numeric(clean_data[field].replace('', pd.NA), errors='coerce').round()
                clean_data[field] = clean_data[field].apply(lambda x: int(x) if pd.notna(x) else None)
        
        # String fields - vectorized
        string_cols = [col for col in clean_data.columns 
                      if col not in numeric_fields + integer_fields]
        for field in string_cols:
            if field in clean_data.columns:
                clean_data[field] = clean_data[field].fillna('')
        
        # Convert to records for bulk insert
        clean_data = clean_data.replace('', None)
        return clean_data, chunk_num
        
    except Exception as e:
        print(f"❌ Chunk {chunk_num} error: {e}")
        return None, chunk_num

def turbo_load_alabama(tsv_file_path, max_workers=4, chunk_size=50000):
    """High-performance multiprocessing loader"""
    
    print("🚀 TURBO ALABAMA LOADER - MULTIPROCESSING MODE")
    print(f"⚙️  Workers: {max_workers}")
    print(f"📦 Chunk size: {chunk_size:,}")
    print("=" * 60)
    
    # Field mapping - CORRECTED from working loader
    field_mapping = {
        'Quantarium_Internal_PID': 'quantarium_internal_pid',
        'Assessors_Parcel_Number': 'apn', 
        'FIPS_Code': 'fips_code',
        'ESTIMATED_VALUE': 'estimated_value',
        'Property_City_Name': 'property_city_name',
        'Current_Owner_Name': 'current_owner_name',
        'LotSize_Square_Feet': 'lot_size_square_feet',
        'Building_Area_1': 'building_area_total',
        'Number_of_Bedrooms': 'number_of_bedrooms',
        'Year_Built': 'year_built',
        'LSale_Price': 'lsale_price',
        'PA_Latitude': 'latitude',
        'PA_Longitude': 'longitude',
        'Property_State': 'property_state',
        'Property_Full_Street_Address': 'property_full_street_address',
        'Property_Zip_Code': 'property_zip_code',
        'Owner_Occupied': 'owner_occupied',
        'Total_Assessed_Value': 'total_assessed_value'
    }
    
    start_time = time.time()
    
    try:
        # Clear database
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE datnest.properties RESTART IDENTITY CASCADE")
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database cleared")
        
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
        
        # Process chunks in parallel
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for chunk_num, chunk in enumerate(chunk_reader, 1):
                future = executor.submit(process_chunk, chunk, field_mapping, chunk_num)
                futures.append(future)
                
                # Process completed chunks
                if len(futures) >= max_workers:
                    for future in as_completed(futures):
                        clean_data, chunk_id = future.result()
                        if clean_data is not None:
                            # Bulk database insert
                            total_loaded += bulk_insert_data(clean_data)
                    futures = []
            
            # Process remaining chunks
            for future in as_completed(futures):
                clean_data, chunk_id = future.result()
                if clean_data is not None:
                    total_loaded += bulk_insert_data(clean_data)
        
        elapsed = time.time() - start_time
        rate = total_loaded / elapsed if elapsed > 0 else 0
        
        print(f"\n🎉 TURBO LOAD COMPLETE!")
        print(f"📊 Records: {total_loaded:,}")
        print(f"⏱️  Time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print(f"🚀 Rate: {rate:,.0f} records/second")
        
        return True
        
    except Exception as e:
        print(f"❌ Turbo load failed: {e}")
        return False

def bulk_insert_data(clean_data):
    """Fast bulk database insert with better error handling"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', 
                                       newline='', encoding='utf-8') as tmp_file:
            clean_data.to_csv(tmp_file, sep='\t', header=False, index=False, 
                            na_rep='\\N', float_format='%.0f')
            tmp_file_path = tmp_file.name
        
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        
        print(f"💾 Inserting {len(clean_data)} records with columns: {list(clean_data.columns)}")
        
        with open(tmp_file_path, 'r', encoding='utf-8') as f:
            cursor.copy_from(f, 'properties', columns=tuple(clean_data.columns), 
                           sep='\t', null='\\N')
        conn.commit()
        cursor.close()
        conn.close()
        
        os.unlink(tmp_file_path)
        print(f"✅ Successfully inserted {len(clean_data)} records")
        return len(clean_data)
        
    except Exception as e:
        print(f"❌ Bulk insert error: {e}")
        print(f"🔍 Attempted columns: {list(clean_data.columns) if 'clean_data' in locals() else 'N/A'}")
        try:
            os.unlink(tmp_file_path)
        except:
            pass
        return 0

if __name__ == "__main__":
    tsv_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    # Detect optimal workers (use 70% of CPU cores)
    max_workers = max(1, int(mp.cpu_count() * 0.7))
    
    print(f"🖥️  Detected {mp.cpu_count()} CPU cores")
    print(f"⚙️  Using {max_workers} workers")
    
    success = turbo_load_alabama(tsv_path, max_workers=max_workers, chunk_size=50000)
    exit(0 if success else 1) 