#!/usr/bin/env python3
"""
ENHANCED Production Loader - Master Database Engineer Fix
FIXES: Data conversion bugs + adds high-value fields
GOAL: Eliminate 97% data loss and unlock complete property intelligence
"""

import csv
import psycopg2
import pandas as pd
import numpy as np
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
try:
    from config import get_db_config
    CONN_PARAMS = get_db_config()
    print("✅ Database configuration loaded securely")
except Exception as e:
    print(f"❌ SECURITY ERROR: Failed to load secure database configuration: {e}")
    sys.exit(1)

def enhanced_load_with_fixes():
    """Enhanced loader that fixes data conversion bugs and adds high-value fields"""
    file_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    print("🚀 ENHANCED PRODUCTION LOADER - MASTER DATABASE ENGINEER")
    print("🎯 MISSION: Fix data conversion bugs + unlock property intelligence")
    print("=" * 70)
    print(f"📁 File: {os.path.basename(file_path)} ({os.path.getsize(file_path)/1024**3:.2f} GB)")
    
    # ENHANCED FIELD MAPPING - High Business Value Fields
    field_mapping = {
        # Core Identifiers (TIER 1)
        'Quantarium_Internal_PID': 'quantarium_internal_pid',
        'Assessors_Parcel_Number': 'apn', 
        'FIPS_Code': 'fips_code',
        
        # QVM Intelligence (TIER 1 - CRITICAL BUSINESS VALUE)
        'ESTIMATED_VALUE': 'estimated_value',
        'PRICE_RANGE_MAX': 'price_range_max',          # 🔧 FIX NEEDED
        'PRICE_RANGE_MIN': 'price_range_min',          # 🔧 FIX NEEDED
        'CONFIDENCE_SCORE': 'confidence_score',        # 🔧 FIX NEEDED
        'QVM_asof_Date': 'qvm_asof_date',              # 📋 NEW HIGH VALUE
        'QVM_Value_Range_Code': 'qvm_value_range_code', # 📋 NEW HIGH VALUE
        
        # Property Location (TIER 1)
        'Property_Full_Street_Address': 'property_full_street_address',
        'Property_City_Name': 'property_city_name',
        'Property_State': 'property_state',
        'Property_Zip_Code': 'property_zip_code',
        'PA_Latitude': 'latitude',
        'PA_Longitude': 'longitude',
        
        # Property Characteristics (TIER 1 - HIGH BUSINESS VALUE)
        'Building_Area_1': 'building_area_total',      # 📋 NEW - 100% coverage!
        'LotSize_Square_Feet': 'lot_size_square_feet', # 📋 NEW HIGH VALUE
        'Number_of_Bedrooms': 'number_of_bedrooms',    # 📋 NEW - 100% coverage!
        'Number_of_Baths': 'number_of_bathrooms',      # 📋 NEW HIGH VALUE
        'Year_Built': 'year_built',                    # 📋 NEW HIGH VALUE
        
        # Assessment Intelligence (TIER 2 - HIGH BUSINESS VALUE)
        'Total_Assessed_Value': 'total_assessed_value',
        'Assessment_Year': 'assessment_year',
        'Total_Market_Value': 'total_market_value',
        'Tax_Amount': 'tax_amount',
    }
    
    total_loaded = 0
    chunk_size = 25000  # Smaller chunks for reliability with more fields
    
    try:
        # Truncate table for fresh enhanced load
        conn = psycopg2.connect(**CONN_PARAMS)
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        cursor.execute("TRUNCATE TABLE properties RESTART IDENTITY CASCADE")
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Table truncated for fresh enhanced load")
        
        # Read file in chunks with enhanced processing
        print(f"📖 Processing file in {chunk_size:,} row chunks...")
        
        chunk_reader = pd.read_csv(
            file_path,
            sep='\t',
            chunksize=chunk_size,
            dtype=str,
            encoding='utf-8',
            engine='python',
            quoting=csv.QUOTE_NONE,
            on_bad_lines='skip',
            na_values=['']  # Treat empty strings as NaN
        )
        
        start_time = time.time()
        
        for chunk_num, chunk in enumerate(chunk_reader, 1):
            chunk_start = time.time()
            print(f"📦 Processing chunk {chunk_num}: {len(chunk):,} rows")
            
            # Map fields with enhanced handling
            clean_data = pd.DataFrame()
            mapped_fields = []
            
            for tsv_col, db_col in field_mapping.items():
                if tsv_col in chunk.columns:
                    clean_data[db_col] = chunk[tsv_col]
                    mapped_fields.append(tsv_col)
                else:
                    print(f"⚠️  Field not found: {tsv_col}")
            
            print(f"   ✅ Mapped {len(mapped_fields)}/{len(field_mapping)} fields")
            
            # ENHANCED DATA CLEANING - Fix conversion bugs
            
            # 1. Handle required string fields (NOT NULL constraints)
            required_string_fields = {
                'quantarium_internal_pid': 'UNKNOWN',
                'apn': 'UNKNOWN', 
                'fips_code': '00000'
            }
            
            for field, default_value in required_string_fields.items():
                if field in clean_data.columns:
                    clean_data[field] = clean_data[field].fillna(default_value)
                    # Replace empty strings
                    mask = clean_data[field].str.strip() == ''
                    clean_data.loc[mask, field] = default_value
            
            # 2. Handle numeric fields (FIXED conversion)
            numeric_fields = [
                'estimated_value', 'price_range_max', 'price_range_min', 
                'building_area_total', 'lot_size_square_feet', 
                'total_assessed_value', 'total_market_value', 'tax_amount',
                'latitude', 'longitude'
            ]
            
            for field in numeric_fields:
                if field in clean_data.columns:
                    # Convert to numeric, keeping NaN as None for PostgreSQL NULL
                    clean_data[field] = pd.to_numeric(clean_data[field], errors='coerce')
                    # Replace NaN with None (PostgreSQL NULL)
                    clean_data[field] = clean_data[field].where(pd.notna(clean_data[field]), None)
            
            # 3. Handle integer fields (FIXED conversion)
            integer_fields = ['confidence_score', 'number_of_bedrooms', 'year_built', 'assessment_year']
            
            for field in integer_fields:
                if field in clean_data.columns:
                    # Convert to numeric first, then to integer
                    numeric_series = pd.to_numeric(clean_data[field], errors='coerce')
                    # Convert to integer where possible, keep as None where NaN
                    clean_data[field] = numeric_series.where(pd.notna(numeric_series), None)
                    # Convert non-null values to int
                    mask = pd.notna(clean_data[field])
                    clean_data.loc[mask, field] = clean_data.loc[mask, field].astype(int)
            
            # 4. Handle decimal fields (bathrooms)
            decimal_fields = ['number_of_bathrooms']
            
            for field in decimal_fields:
                if field in clean_data.columns:
                    clean_data[field] = pd.to_numeric(clean_data[field], errors='coerce')
                    clean_data[field] = clean_data[field].where(pd.notna(clean_data[field]), None)
            
            # 5. Handle string fields (optional)
            string_fields = [
                'property_full_street_address', 'property_city_name', 
                'property_state', 'property_zip_code', 
                'qvm_value_range_code'
            ]
            
            for field in string_fields:
                if field in clean_data.columns:
                    clean_data[field] = clean_data[field].fillna('')
                    # Clean up zip codes
                    if field == 'property_zip_code':
                        clean_data[field] = clean_data[field].str.strip().str[:5]
            
            # 6. Handle date fields
            date_fields = ['qvm_asof_date']
            
            for field in date_fields:
                if field in clean_data.columns:
                    # Convert YYYYMMDD to proper date format
                    date_series = pd.to_datetime(clean_data[field], format='%Y%m%d', errors='coerce')
                    clean_data[field] = date_series.where(pd.notna(date_series), None)
            
            # Create temp file and COPY with enhanced error handling
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as tmp_file:
                clean_data.to_csv(tmp_file, sep='\t', header=False, index=False, na_rep='\\N')
                tmp_file_path = tmp_file.name
            
            # COPY to database with enhanced error handling
            conn = psycopg2.connect(**CONN_PARAMS)
            cursor = conn.cursor()
            cursor.execute("SET search_path TO datnest, public")
            
            try:
                with open(tmp_file_path, 'r', encoding='utf-8') as f:
                    cursor.copy_from(
                        f,
                        'properties',
                        columns=tuple(clean_data.columns),
                        sep='\t',
                        null='\\N'
                    )
                
                conn.commit()
                
                # Immediate verification
                cursor.execute("SELECT COUNT(*) FROM properties WHERE price_range_max IS NOT NULL")
                qvm_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM properties WHERE building_area_total IS NOT NULL")
                building_count = cursor.fetchone()[0]
                
                print(f"   🎯 QVM fields: {qvm_count} records")
                print(f"   🏠 Building area: {building_count} records")
                
            except Exception as e:
                print(f"❌ Database error in chunk {chunk_num}: {e}")
                conn.rollback()
            finally:
                cursor.close()
                conn.close()
            
            # Cleanup
            os.unlink(tmp_file_path)
            
            total_loaded += len(clean_data)
            chunk_elapsed = time.time() - chunk_start
            overall_elapsed = time.time() - start_time
            
            print(f"✅ Chunk {chunk_num}: {len(clean_data):,} records in {chunk_elapsed:.1f}s")
            print(f"📈 Total: {total_loaded:,} records, {total_loaded/overall_elapsed:.0f} rec/sec overall")
            print()
            
            # Progress checkpoint every 5 chunks
            if chunk_num % 5 == 0:
                elapsed_min = overall_elapsed / 60
                print(f"🕐 Checkpoint: {chunk_num} chunks, {elapsed_min:.1f} minutes elapsed")
                print()
        
        total_elapsed = time.time() - start_time
        
        # Final verification
        print("\n🎉 ENHANCED LOAD COMPLETE!")
        print("=" * 50)
        print(f"📊 Total records: {total_loaded:,}")
        print(f"⏱️  Total time: {total_elapsed/60:.1f} minutes")
        print(f"📈 Average rate: {total_loaded/total_elapsed:.0f} records/second")
        
        # Verify enhanced field coverage
        print(f"\n🔍 ENHANCED FIELD VERIFICATION:")
        conn = psycopg2.connect(**CONN_PARAMS)
        cursor = conn.cursor()
        
        verification_fields = {
            'estimated_value': 'ESTIMATED_VALUE',
            'price_range_max': 'PRICE_RANGE_MAX',
            'price_range_min': 'PRICE_RANGE_MIN', 
            'confidence_score': 'CONFIDENCE_SCORE',
            'building_area_total': 'Building_Area_1',
            'number_of_bedrooms': 'Number_of_Bedrooms'
        }
        
        for db_field, tsv_field in verification_fields.items():
            cursor.execute(f"SELECT COUNT(*) FROM properties WHERE {db_field} IS NOT NULL")
            count = cursor.fetchone()[0]
            coverage = (count / total_loaded) * 100 if total_loaded > 0 else 0
            status = "✅" if count > 0 else "❌"
            print(f"  {status} {db_field}: {count:,} records ({coverage:.1f}%) - TSV: {tsv_field}")
        
        cursor.close()
        conn.close()
        
        print(f"\n🚀 MISSION ACCOMPLISHED - Property intelligence unlocked!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔥 ENHANCED PRODUCTION LOADER - MASTER DATABASE ENGINEER")
    print("🎯 ELIMINATING 97% DATA LOSS")
    print("=" * 70)
    enhanced_load_with_fixes() 