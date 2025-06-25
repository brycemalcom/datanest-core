#!/usr/bin/env python3
"""
Analyze All 449 TSV Columns - Ensure no data loss
"""

import csv
import pandas as pd

# CRITICAL: Set CSV field size limit FIRST
try:
    csv.field_size_limit(2147483647)
    print(f"✅ CSV limit: {csv.field_size_limit():,} bytes")
except OverflowError:
    csv.field_size_limit(1000000000)
    print(f"✅ CSV limit: {csv.field_size_limit():,} bytes")

def analyze_tsv_columns():
    """Analyze all columns in the TSV file"""
    file_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    print("🔍 Analyzing ALL TSV columns...")
    
    # Read just the header row to get all column names
    chunk = pd.read_csv(
        file_path,
        sep='\t',
        nrows=1,  # Just first row to get columns
        dtype=str,
        encoding='utf-8',
        engine='python',
        quoting=csv.QUOTE_NONE,
        on_bad_lines='skip'
    )
    
    tsv_columns = list(chunk.columns)
    print(f"📊 TSV file has {len(tsv_columns)} columns")
    
    # Database schema columns (from check_schema.py output)
    db_columns = [
        'id',  # Auto-generated
        'quantarium_internal_pid',
        'apn', 
        'fips_code',
        'estimated_value',
        'price_range_max',
        'price_range_min', 
        'confidence_score',
        'qvm_asof_date',
        'qvm_value_range_code',
        'property_full_street_address',
        'property_city_name',
        'property_state',
        'property_zip_code',
        'building_area_total',
        'lot_size_square_feet',  # Missing from current schema output?
        'number_of_bedrooms',
        'number_of_bathrooms',
        'year_built',
        'total_assessed_value',
        'assessment_year',
        'latitude',
        'longitude',
        'created_at',  # Auto-generated
        'updated_at',  # Auto-generated
        'data_source'  # Auto-generated
    ]
    
    print(f"📊 Database has {len(db_columns)} columns")
    
    # Show first 50 TSV columns
    print("\n📋 First 50 TSV columns:")
    for i, col in enumerate(tsv_columns[:50], 1):
        print(f"  {i:2d}. {col}")
    
    print(f"\n... and {len(tsv_columns) - 50} more columns")
    
    # Look for key QVM and property fields
    print("\n🔍 Key field analysis:")
    key_patterns = [
        'Quantarium', 'ESTIMATED', 'CONFIDENCE', 'PRICE_RANGE', 'QVM',
        'Property_', 'FIPS', 'APN', 'Owner', 'Building', 'Lot', 
        'Bedroom', 'Bath', 'Year_Built', 'Assessed'
    ]
    
    for pattern in key_patterns:
        matching = [col for col in tsv_columns if pattern.lower() in col.lower()]
        if matching:
            print(f"  {pattern}: {len(matching)} columns")
            for col in matching[:3]:  # Show first 3 matches
                print(f"    - {col}")
            if len(matching) > 3:
                print(f"    ... and {len(matching) - 3} more")
    
    return tsv_columns, db_columns

def check_current_mapping_coverage():
    """Check how much data we're currently capturing"""
    
    # Current mapping from production_copy_loader.py
    current_mapping = {
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
    
    print(f"\n⚠️  CURRENT MAPPING COVERAGE:")
    print(f"📊 Currently mapping: {len(current_mapping)} out of 449 TSV columns")
    print(f"📊 Data loss: {449 - len(current_mapping)} columns ({(449 - len(current_mapping))/449*100:.1f}%)")
    
    print("\n📋 Currently mapped fields:")
    for tsv_col, db_col in current_mapping.items():
        print(f"  {tsv_col} → {db_col}")

if __name__ == "__main__":
    print("🔍 Complete Column Analysis")
    print("=" * 60)
    
    tsv_cols, db_cols = analyze_tsv_columns()
    check_current_mapping_coverage()
    
    print(f"\n🚨 CRITICAL ISSUE:")
    print(f"   Database schema: {len(db_cols)} columns")
    print(f"   TSV file: {len(tsv_cols)} columns") 
    print(f"   Current mapping: Only 13 columns")
    print(f"\n❌ We are currently LOSING {449-13} columns of data!")
    print(f"\n✅ SOLUTION NEEDED: Expand database schema or create comprehensive mapping") 