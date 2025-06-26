#!/usr/bin/env python3
"""
Evidence-Based Field Test Loader - Master Database Engineer
STRATEGY: Test new field mappings with small sample for efficiency
GOAL: Validate evidence-based corrections before full production load
"""

import csv
import psycopg2
import pandas as pd
import numpy as np
import tempfile
import os
import time
import sys
from decimal import Decimal

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
    from src.config import get_db_config
    CONN_PARAMS = get_db_config()
    print("✅ Database configuration loaded securely")
except Exception as e:
    print(f"❌ SECURITY ERROR: Failed to load secure database configuration: {e}")
    sys.exit(1)

def test_evidence_based_fields():
    """Test new evidence-based fields with small sample for efficiency"""
    file_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    sample_size = 5000  # Small sample for fast testing
    
    print("🧪 EVIDENCE-BASED FIELD TEST LOADER")
    print("🎯 STRATEGY: Validate 7 new fields with small sample")
    print("⚡ EFFICIENCY: 5K records vs 5M records (1000x faster)")
    print("=" * 70)
    print(f"📁 File: {os.path.basename(file_path)}")
    print(f"🔬 Sample Size: {sample_size:,} records")
    
    # EVIDENCE-BASED FIELD MAPPING - Using ACTUAL TSV column names from data_dictionary.txt
    field_mapping = {
        # EXISTING WORKING FIELDS (22 fields) - Keep for context
        'Quantarium_Internal_PID': 'quantarium_internal_pid',
        'Assessors_Parcel_Number': 'apn',
        'FIPS_Code': 'fips_code',
        'ESTIMATED_VALUE': 'estimated_value',
        'PRICE_RANGE_MAX': 'price_range_max',
        'PRICE_RANGE_MIN': 'price_range_min',
        'CONFIDENCE_SCORE': 'confidence_score',
        'QVM_asof_Date': 'qvm_asof_date',
        'QVM_Value_Range_Code': 'qvm_value_range_code',
        'Property_Full_Street_Address': 'property_full_street_address',
        'Property_City_Name': 'property_city_name',
        'Property_State': 'property_state',
        'Property_Zip_Code': 'property_zip_code',
        'PA_Latitude': 'latitude',
        'PA_Longitude': 'longitude',
        'Building_Area_1': 'building_area_total',
        'LotSize_Square_Feet': 'lot_size_square_feet',
        'Number_of_Bedrooms': 'number_of_bedrooms',
        'Number_of_Baths': 'number_of_bathrooms',
        'Year_Built': 'year_built',
        'Total_Assessed_Value': 'total_assessed_value',
        'Assessment_Year': 'assessment_year',
        
        # 🔥 NEW EVIDENCE-BASED FIELDS TO TEST (7 fields)
        'Standardized_Land_Use_Code': 'standardized_land_use_code',  # Property Classification
        'Style': 'style',                                            # Architectural Style
        'Zoning': 'zoning',                                          # Zoning Classification
        'Owner_Occupied': 'owner_occupied',                          # Owner Intelligence
        'Current_Owner_Name': 'current_owner_name',                  # Owner Information
        'Building_Quality': 'building_quality',                     # Building Quality
        'Building_Condition': 'building_condition',                 # Building Condition
    }
    
    print(f"🔥 Testing {len(field_mapping)} total fields")
    print(f"📊 Focus: 7 NEW evidence-based fields with VERIFIED TSV column names")
    print()
    
    try:
        start_time = time.time()
        
        # Read SAMPLE of data for testing
        print(f"📖 Reading {sample_size:,} sample records...")
        
        # Read sample efficiently
        df_sample = pd.read_csv(
            file_path,
            sep='\t',
            nrows=sample_size,
            dtype=str,
            encoding='utf-8',
            engine='python',
            quoting=csv.QUOTE_NONE,
            on_bad_lines='skip',
            na_values=['']
        )
        
        print(f"✅ Read {len(df_sample):,} records in {time.time() - start_time:.1f} seconds")
        print(f"📊 TSV has {len(df_sample.columns)} total columns available")
        
        # Map fields with validation
        clean_data = pd.DataFrame()
        mapped_fields = []
        missing_fields = []
        new_fields_found = []
        
        for tsv_col, db_col in field_mapping.items():
            if tsv_col in df_sample.columns:
                clean_data[db_col] = df_sample[tsv_col]
                mapped_fields.append(tsv_col)
                
                # Track new evidence-based fields
                if tsv_col in ['Standardized_Land_Use_Code', 'Style', 'Zoning', 
                              'Owner_Occupied', 'Current_Owner_Name', 
                              'Building_Quality', 'Building_Condition']:
                    new_fields_found.append(tsv_col)
            else:
                missing_fields.append(tsv_col)
        
        print(f"✅ Successfully mapped {len(mapped_fields)}/{len(field_mapping)} fields")
        print(f"🎯 NEW fields found: {len(new_fields_found)}/7")
        
        if new_fields_found:
            print(f"   🔥 EVIDENCE-BASED SUCCESS: {', '.join(new_fields_found)}")
        
        if missing_fields:
            print(f"⚠️  Missing fields: {missing_fields}")
        
        # Quick data quality analysis for NEW fields
        print(f"\n🔍 DATA QUALITY ANALYSIS (NEW FIELDS):")
        
        new_field_mapping = {
            'standardized_land_use_code': 'Standardized_Land_Use_Code',
            'style': 'Style', 
            'zoning': 'Zoning',
            'owner_occupied': 'Owner_Occupied',
            'current_owner_name': 'Current_Owner_Name',
            'building_quality': 'Building_Quality',
            'building_condition': 'Building_Condition'
        }
        
        for db_field, tsv_field in new_field_mapping.items():
            if db_field in clean_data.columns:
                non_null_count = clean_data[db_field].notna().sum()
                coverage = (non_null_count / len(clean_data)) * 100
                
                # Sample values
                sample_values = clean_data[db_field].dropna().head(3).tolist()
                sample_str = ', '.join([str(v)[:20] for v in sample_values]) if sample_values else "No data"
                
                status = "✅" if coverage > 10 else "⚠️" if coverage > 0 else "❌"
                print(f"  {status} {db_field}: {non_null_count:,}/{len(clean_data):,} ({coverage:.1f}%)")
                print(f"      Samples: {sample_str}")
        
        # TRUNCATE and insert sample data for testing
        print(f"\n🔄 Loading sample data to database...")
        
        # Handle data types (simplified for testing)
        # Required fields
        required_fields = ['quantarium_internal_pid', 'apn', 'fips_code']
        for field in required_fields:
            if field in clean_data.columns:
                clean_data[field] = clean_data[field].fillna('UNKNOWN')
        
        # Numeric fields  
        numeric_fields = ['estimated_value', 'price_range_max', 'price_range_min', 
                         'building_area_total', 'lot_size_square_feet', 'total_assessed_value']
        for field in numeric_fields:
            if field in clean_data.columns:
                clean_data[field] = pd.to_numeric(clean_data[field], errors='coerce')
        
        # Integer fields
        integer_fields = ['confidence_score', 'number_of_bedrooms', 'year_built', 'assessment_year']
        for field in integer_fields:
            if field in clean_data.columns:
                clean_data[field] = pd.to_numeric(clean_data[field], errors='coerce').round().astype('Int64')
        
        # String fields (including new ones)
        string_fields = ['property_full_street_address', 'property_city_name', 'property_state',
                        'standardized_land_use_code', 'style', 'zoning', 'owner_occupied',
                        'current_owner_name', 'building_quality', 'building_condition']
        for field in string_fields:
            if field in clean_data.columns:
                clean_data[field] = clean_data[field].fillna('')
        
        # Load to database
        conn = psycopg2.connect(**CONN_PARAMS)
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        
        # TRUNCATE for clean test
        cursor.execute("TRUNCATE TABLE properties RESTART IDENTITY CASCADE")
        
        # Create temp file for COPY
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as tmp_file:
            clean_data.to_csv(tmp_file, sep='\t', header=False, index=False, na_rep='\\N')
            tmp_file_path = tmp_file.name
        
        # COPY to database
        with open(tmp_file_path, 'r', encoding='utf-8') as f:
            cursor.copy_from(
                f,
                'properties',
                columns=tuple(clean_data.columns),
                sep='\t',
                null='\\N'
            )
        
        conn.commit()
        os.unlink(tmp_file_path)
        
        # VERIFICATION - Check new fields in database
        print(f"\n🎉 EVIDENCE-BASED FIELD TEST RESULTS:")
        
        cursor.execute("SELECT COUNT(*) FROM properties")
        total_loaded = cursor.fetchone()[0]
        print(f"📊 Sample records loaded: {total_loaded:,}")
        
        print(f"\n🔍 NEW FIELD VERIFICATION IN DATABASE:")
        
        for db_field, tsv_field in new_field_mapping.items():
            try:
                cursor.execute(f"SELECT COUNT(*) FROM properties WHERE {db_field} IS NOT NULL AND {db_field} != ''")
                count = cursor.fetchone()[0]
                coverage = (count / total_loaded) * 100 if total_loaded > 0 else 0
                
                # Get sample values
                cursor.execute(f"SELECT DISTINCT {db_field} FROM properties WHERE {db_field} IS NOT NULL AND {db_field} != '' LIMIT 3")
                samples = [row[0] for row in cursor.fetchall()]
                sample_str = ', '.join([str(s)[:15] for s in samples]) if samples else "No data"
                
                status = "✅" if count > 0 else "❌"
                print(f"  {status} {db_field}: {count:,} records ({coverage:.1f}%) - {sample_str}")
                
            except Exception as e:
                print(f"  ❌ {db_field}: Database error - {e}")
        
        cursor.close()
        conn.close()
        
        elapsed = time.time() - start_time
        print(f"\n⚡ TEST COMPLETED in {elapsed:.1f} seconds")
        print(f"🚀 EFFICIENCY: {sample_size:,} records tested vs 5M+ full load")
        print(f"📊 NEXT STEP: Full production load with validated field mapping")
        
        return True
        
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_evidence_based_fields() 