#!/usr/bin/env python3
"""
Production COPY Loader - Scale up the proven bulletproof approach
SECURITY: Uses secure configuration management - no hardcoded credentials
"""

import csv
import psycopg2
import pandas as pd
import tempfile
import os
import time
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# CRITICAL: Set CSV field size limit FIRST
try:
    csv.field_size_limit(2147483647)
    print(f"✅ CSV limit: {csv.field_size_limit():,} bytes")
except OverflowError:
    csv.field_size_limit(1000000000)
    print(f"✅ CSV limit: {csv.field_size_limit():,} bytes")

# SECURITY: Database connection loaded from secure sources only
# Never hardcode credentials - use environment variables or AWS Secrets Manager
try:
    from config import get_db_config
    CONN_PARAMS = get_db_config()
    print("✅ Database configuration loaded securely")
except Exception as e:
    print(f"❌ SECURITY ERROR: Failed to load secure database configuration: {e}")
    print("Please set environment variables: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME")
    print("Or configure AWS Secrets Manager with 'datnest-core/db/credentials'")
    sys.exit(1)

def load_full_file_with_copy():
    """Load entire first file using proven COPY approach"""
    file_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    print("🚀 Production COPY Loading - Full File")
    print(f"📁 File: {os.path.basename(file_path)} ({os.path.getsize(file_path)/1024**3:.2f} GB)")
    
    # Essential field mapping (proven to work)
    field_mapping = {
        'Quantarium_Internal_PID': 'quantarium_internal_pid',
        'Assessors_Parcel_Number': 'apn', 
        'FIPS_Code': 'fips_code',
        'ESTIMATED_VALUE': 'estimated_value',
        'PRICE_RANGE_MAX': 'price_range_max',
        'PRICE_RANGE_MIN': 'price_range_min',
        'CONFIDENCE_SCORE': 'confidence_score',
        'Property_Full_Street_Address': 'property_full_street_address',
        'Property_City_Name': 'property_city_name',
        'Property_State': 'property_state',
        'Property_Zip_Code': 'property_zip_code',
        'PA_Latitude': 'latitude',
        'PA_Longitude': 'longitude'
    }
    
    total_loaded = 0
    chunk_size = 50000  # Process 50K rows at a time
    
    try:
        # Truncate table for fresh start
        conn = psycopg2.connect(**CONN_PARAMS)
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        cursor.execute("TRUNCATE TABLE properties RESTART IDENTITY CASCADE")
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Table truncated for fresh production load")
        
        # Read file in chunks
        print(f"📖 Processing file in {chunk_size:,} row chunks...")
        
        chunk_reader = pd.read_csv(
            file_path,
            sep='\t',
            chunksize=chunk_size,
            dtype=str,
            encoding='utf-8',
            engine='python',
            quoting=csv.QUOTE_NONE,
            on_bad_lines='skip'
        )
        
        start_time = time.time()
        
        for chunk_num, chunk in enumerate(chunk_reader, 1):
            chunk_start = time.time()
            print(f"📦 Processing chunk {chunk_num}: {len(chunk):,} rows")
            
            # Map fields
            clean_data = pd.DataFrame()
            for tsv_col, db_col in field_mapping.items():
                if tsv_col in chunk.columns:
                    clean_data[db_col] = chunk[tsv_col]
            
            # Clean data (proven approach)
            clean_data['quantarium_internal_pid'] = clean_data['quantarium_internal_pid'].fillna('UNKNOWN')
            clean_data['apn'] = clean_data['apn'].fillna('UNKNOWN')
            clean_data['fips_code'] = clean_data['fips_code'].fillna('00000')
            
            # Handle numeric fields properly
            numeric_fields = ['estimated_value', 'price_range_max', 'price_range_min', 'latitude', 'longitude']
            for field in numeric_fields:
                if field in clean_data.columns:
                    clean_data[field] = clean_data[field].replace(['', ' ', 'NULL'], '\\N')
            
            # Handle integer fields  
            if 'confidence_score' in clean_data.columns:
                clean_data['confidence_score'] = clean_data['confidence_score'].replace(['', ' ', 'NULL'], '\\N')
            
            # Handle string fields
            string_fields = ['property_full_street_address', 'property_city_name', 'property_state', 'property_zip_code']
            for field in string_fields:
                if field in clean_data.columns:
                    clean_data[field] = clean_data[field].fillna('')
            
            # Create temp file and COPY
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as tmp_file:
                clean_data.to_csv(tmp_file, sep='\t', header=False, index=False, na_rep='\\N')
                tmp_file_path = tmp_file.name
            
            # COPY to database
            conn = psycopg2.connect(**CONN_PARAMS)
            cursor = conn.cursor()
            cursor.execute("SET search_path TO datnest, public")
            
            with open(tmp_file_path, 'r') as f:
                cursor.copy_from(
                    f,
                    'properties',
                    columns=tuple(clean_data.columns),
                    sep='\t',
                    null='\\N'
                )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Cleanup
            os.unlink(tmp_file_path)
            
            total_loaded += len(clean_data)
            chunk_elapsed = time.time() - chunk_start
            overall_elapsed = time.time() - start_time
            
            print(f"✅ Chunk {chunk_num}: {len(clean_data):,} records in {chunk_elapsed:.1f}s")
            print(f"📈 Total: {total_loaded:,} records, {total_loaded/overall_elapsed:.0f} rec/sec overall")
            
            # Progress checkpoint every 10 chunks
            if chunk_num % 10 == 0:
                elapsed_min = overall_elapsed / 60
                print(f"🕐 Checkpoint: {chunk_num} chunks, {elapsed_min:.1f} minutes elapsed")
        
        total_elapsed = time.time() - start_time
        print(f"\n🎉 FILE COMPLETE!")
        print(f"📊 Total records: {total_loaded:,}")
        print(f"⏱️  Total time: {total_elapsed/60:.1f} minutes")
        print(f"📈 Average rate: {total_loaded/total_elapsed:.0f} records/second")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏭 Production COPY Loader")
    print("=" * 50)
    load_full_file_with_copy() 