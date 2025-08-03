#!/usr/bin/env python3
"""
MVP TURBO LOADER - Ultra High Performance for Client Valuation Business
Goal: Load 5M records in 20 minutes (4,167 records/second) with core 20 fields
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
    """Process a single chunk in parallel with optimized MVP field handling"""
    try:
        print(f"🔧 Worker processing chunk {chunk_num}: {len(chunk_data):,} rows")
        
        # Fast bulk mapping - no fragmentation
        available_mapping = {db_col: tsv_col for tsv_col, db_col in field_mapping.items() 
                            if tsv_col in chunk_data.columns}
        
        clean_data = chunk_data[list(available_mapping.values())].copy()
        clean_data.columns = list(available_mapping.keys())
        
        print(f"   📊 Mapped {len(available_mapping)}/{len(field_mapping)} MVP fields")
        
        # Fast data cleaning using vectorized operations
        # Required fields
        for field in ['quantarium_internal_pid', 'apn', 'fips_code']:
            if field in clean_data.columns:
                clean_data[field] = clean_data[field].fillna('UNKNOWN')
        
        # Numeric fields - vectorized (coordinates and areas)
        numeric_fields = ['building_area_total', 'lot_size_square_feet', 'latitude', 'longitude']
        for field in numeric_fields:
            if field in clean_data.columns:
                clean_data[field] = pd.to_numeric(clean_data[field].replace('', pd.NA), errors='coerce')
                clean_data[field] = clean_data[field].where(pd.notna(clean_data[field]), None)
        
        # Integer fields - vectorized (valuations and property data)
        integer_fields = ['year_built', 'number_of_bedrooms', 'estimated_value', 'lsale_price', 
                         'total_assessed_value', 'price_range_min', 'price_range_max', 'confidence_score']
        for field in integer_fields:
            if field in clean_data.columns:
                clean_data[field] = pd.to_numeric(clean_data[field].replace('', pd.NA), errors='coerce').round()
                clean_data[field] = clean_data[field].apply(lambda x: int(x) if pd.notna(x) else None)
        
        # String fields - vectorized (all remaining fields)
        string_cols = [col for col in clean_data.columns 
                      if col not in numeric_fields + integer_fields]
        for field in string_cols:
            if field in clean_data.columns:
                clean_data[field] = clean_data[field].fillna('')
        
        # Convert empty strings to None for proper NULL handling
        clean_data = clean_data.replace('', None)
        
        print(f"   ✅ Chunk {chunk_num} processed: {len(clean_data):,} records ready")
        return clean_data, chunk_num
        
    except Exception as e:
        print(f"❌ Chunk {chunk_num} error: {e}")
        import traceback
        traceback.print_exc()
        return None, chunk_num

def mvp_turbo_load(tsv_file_path, max_workers=None, chunk_size=75000):
    """Ultra high-performance MVP loader for client valuation business"""
    
    # Auto-detect optimal workers if not specified
    if max_workers is None:
        max_workers = max(1, int(mp.cpu_count() * 0.8))  # Use 80% of cores for max performance
    
    print("🚀 MVP TURBO LOADER - CLIENT VALUATION BUSINESS")
    print(f"🎯 Target: 5M records in 20 minutes (4,167 rec/sec)")
    print(f"⚙️  Workers: {max_workers}")
    print(f"📦 Chunk size: {chunk_size:,}")
    print("=" * 70)
    
    # MVP Field mapping for client valuation use case (20 core fields)
    field_mapping = {
        # Identifiers & Tracking (3 fields)
        'Quantarium_Internal_PID': 'quantarium_internal_pid',
        'Assessors_Parcel_Number': 'apn', 
        'FIPS_Code': 'fips_code',
        
        # Address Matching for Client Spreadsheets (5 fields)
        'Property_Full_Street_Address': 'property_full_street_address',
        'Property_City_Name': 'property_city_name',
        'Property_State': 'property_state',
        'Property_Zip_Code': 'property_zip_code',
        'PA_Latitude': 'latitude',
        'PA_Longitude': 'longitude',
        
        # Valuation Fields - Core Business Value (4 fields)
        'ESTIMATED_VALUE': 'estimated_value',
        'PRICE_RANGE_MIN': 'price_range_min',
        'PRICE_RANGE_MAX': 'price_range_max',
        'CONFIDENCE_SCORE': 'confidence_score',
        
        # Bonus Property Data (8 fields)
        'Current_Owner_Name': 'current_owner_name',
        'LotSize_Square_Feet': 'lot_size_square_feet',
        'Building_Area_1': 'building_area_total',
        'Number_of_Bedrooms': 'number_of_bedrooms',
        'Year_Built': 'year_built',
        'LSale_Price': 'lsale_price',
        'Total_Assessed_Value': 'total_assessed_value',
        'Owner_Occupied': 'owner_occupied'
    }
    
    print(f"🔥 MVP Fields: {len(field_mapping)} core fields for immediate business value")
    print("🎯 Valuation Fields: QID + Address + Quantarium Value + Low + High + Confidence")
    print("📈 Client Workflow: Upload Address Spreadsheet → Get Property Valuations")
    print()
    
    start_time = time.time()
    
    try:
        # Clear database for fresh start
        print("🗃️  Clearing database for fresh MVP load...")
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        cursor.execute("TRUNCATE TABLE properties RESTART IDENTITY CASCADE")
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database cleared - ready for MVP turbo load")
        
        # Read file in optimized chunks
        print(f"📖 Reading TSV file in {chunk_size:,} record chunks...")
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
        
        # Process chunks in parallel with optimized worker management
        print(f"🚀 Starting parallel processing with {max_workers} workers...")
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for chunk_num, chunk in enumerate(chunk_reader, 1):
                chunk_count = chunk_num
                future = executor.submit(process_chunk, chunk, field_mapping, chunk_num)
                futures.append(future)
                
                # Process completed chunks in batches for better throughput
                if len(futures) >= max_workers * 2:  # Process in larger batches
                    for future in as_completed(futures):
                        clean_data, chunk_id = future.result()
                        if clean_data is not None:
                            # Bulk database insert
                            inserted = bulk_insert_data(clean_data, chunk_id)
                            total_loaded += inserted
                        else:
                            failed_chunks += 1
                            print(f"⚠️  Chunk {chunk_id} failed processing")
                    futures = []
                    
                    # Progress update every batch
                    elapsed = time.time() - start_time
                    rate = total_loaded / elapsed if elapsed > 0 else 0
                    print(f"📈 Progress: {total_loaded:,} records in {elapsed:.1f}s ({rate:,.0f} rec/sec)")
            
            # Process remaining chunks
            print("🏁 Processing final chunks...")
            for future in as_completed(futures):
                clean_data, chunk_id = future.result()
                if clean_data is not None:
                    inserted = bulk_insert_data(clean_data, chunk_id)
                    total_loaded += inserted
                else:
                    failed_chunks += 1
                    print(f"⚠️  Chunk {chunk_id} failed processing")
        
        elapsed = time.time() - start_time
        rate = total_loaded / elapsed if elapsed > 0 else 0
        target_rate = 4167  # Target: 4,167 rec/sec
        
        print(f"\n🎉 MVP TURBO LOAD COMPLETE!")
        print(f"📊 Records loaded: {total_loaded:,}")
        print(f"📦 Chunks processed: {chunk_count} ({failed_chunks} failed)")
        print(f"⏱️  Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print(f"🚀 Performance: {rate:,.0f} records/second")
        print(f"🎯 Target rate: {target_rate:,} rec/sec ({'✅ ACHIEVED' if rate >= target_rate else '⚠️ BELOW TARGET'})")
        
        # Validate MVP data coverage
        print(f"\n🔍 MVP DATA VALIDATION:")
        validate_mvp_data(total_loaded)
        
        success = total_loaded > 0 and failed_chunks < chunk_count * 0.1  # Allow 10% failure rate
        return success
        
    except Exception as e:
        print(f"❌ MVP turbo load failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def bulk_insert_data(clean_data, chunk_id):
    """Optimized bulk database insert with enhanced error handling"""
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

def validate_mvp_data(total_records):
    """Validate MVP data coverage for client valuation business"""
    try:
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        
        # Core validation queries
        validations = {
            'Total Records': 'SELECT COUNT(*) FROM properties',
            'QID Coverage': 'SELECT COUNT(*) FROM properties WHERE quantarium_internal_pid IS NOT NULL',
            'Address Data': 'SELECT COUNT(*) FROM properties WHERE property_full_street_address IS NOT NULL',
            'City Data': 'SELECT COUNT(*) FROM properties WHERE property_city_name IS NOT NULL',
            'State Data': 'SELECT COUNT(*) FROM properties WHERE property_state IS NOT NULL',
            'Coordinates': 'SELECT COUNT(*) FROM properties WHERE latitude IS NOT NULL AND longitude IS NOT NULL',
            'Quantarium Values': 'SELECT COUNT(*) FROM properties WHERE estimated_value IS NOT NULL',
            'Value Ranges': 'SELECT COUNT(*) FROM properties WHERE price_range_min IS NOT NULL AND price_range_max IS NOT NULL',
            'Confidence Scores': 'SELECT COUNT(*) FROM properties WHERE confidence_score IS NOT NULL'
        }
        
        for desc, query in validations.items():
            cursor.execute(query)
            count = cursor.fetchone()[0]
            coverage = (count / total_records) * 100 if total_records > 0 else 0
            print(f"   {desc}: {count:,} ({coverage:.1f}%)")
        
        # Sample data preview
        print(f"\n📋 SAMPLE MVP DATA:")
        cursor.execute("""
            SELECT quantarium_internal_pid, property_city_name, property_state,
                   estimated_value, price_range_min, price_range_max, confidence_score
            FROM properties 
            WHERE estimated_value IS NOT NULL 
            LIMIT 3
        """)
        
        for row in cursor.fetchall():
            print(f"   🏠 QID: {row[0]} | 📍 {row[1]}, {row[2]}")
            print(f"      💰 Value: ${row[3] or 0:,} | Range: ${row[4] or 0:,} - ${row[5] or 0:,} | Confidence: {row[6] or 0}")
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ MVP VALIDATION COMPLETE - Ready for client valuation service!")
        
    except Exception as e:
        print(f"❌ Validation error: {e}")

if __name__ == "__main__":
    # TSV file path
    tsv_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    if not os.path.exists(tsv_path):
        print(f"❌ TSV file not found: {tsv_path}")
        print("📁 Please check the file path and try again")
        exit(1)
    
    # Optimize for maximum performance
    max_workers = max(1, int(mp.cpu_count() * 0.8))  # Use 80% of CPU cores
    chunk_size = 100000  # Large chunks for maximum throughput
    
    print(f"🖥️  Detected {mp.cpu_count()} CPU cores")
    print(f"⚙️  Using {max_workers} workers")
    print(f"📦 Chunk size: {chunk_size:,} records")
    print(f"📁 Source file: {os.path.basename(tsv_path)}")
    print(f"📏 File size: {os.path.getsize(tsv_path)/1024**3:.1f} GB")
    
    success = mvp_turbo_load(tsv_path, max_workers=max_workers, chunk_size=chunk_size)
    
    if success:
        print(f"\n🎉 SUCCESS! MVP turbo loader ready for client valuation business!")
        print(f"📊 Next: Test client workflow - upload address spreadsheet → get QID + valuations")
    else:
        print(f"\n❌ FAILED! Check logs above for error details")
    
    exit(0 if success else 1)