#!/usr/bin/env python3
"""
DIAGNOSE DATA QUALITY ISSUES
Goal: Identify root cause of column misalignment and UTF8 errors
"""

import os
import sys
import csv
import pandas as pd
import codecs

# Set CSV limits for large files
csv.field_size_limit(2147483647)

def diagnose_column_misalignment():
    """Diagnose column mapping and alignment issues"""
    
    print("🔍 DIAGNOSING COLUMN MISALIGNMENT ISSUES")
    print("🎯 Goal: Find why 'AL' is appearing in longitude field")
    print("=" * 60)
    
    tsv_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    try:
        # Read header to understand structure
        print("📋 STEP 1: HEADER ANALYSIS")
        df_header = pd.read_csv(tsv_path, sep='\t', nrows=0)
        
        print(f"   📊 Total columns: {len(df_header.columns)}")
        
        # Find state and coordinate columns
        state_cols = [i for i, col in enumerate(df_header.columns) if 'state' in col.lower()]
        coord_cols = [i for i, col in enumerate(df_header.columns) if 'latitude' in col.lower() or 'longitude' in col.lower()]
        
        print(f"   🗺️  State columns:")
        for i in state_cols:
            print(f"      Column {i}: {df_header.columns[i]}")
            
        print(f"   📍 Coordinate columns:")
        for i in coord_cols:
            print(f"      Column {i}: {df_header.columns[i]}")
        
        # Check our field mapping
        print(f"\n🔧 STEP 2: FIELD MAPPING ANALYSIS")
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
        
        print(f"   📊 Mapped fields: {len(field_mapping)}")
        
        # Check which mapped fields exist in TSV
        missing_fields = []
        existing_fields = []
        
        for tsv_field in field_mapping.keys():
            if tsv_field in df_header.columns:
                existing_fields.append(tsv_field)
                col_index = df_header.columns.get_loc(tsv_field)
                print(f"   ✅ {tsv_field} -> Column {col_index}")
            else:
                missing_fields.append(tsv_field)
                print(f"   ❌ {tsv_field} -> NOT FOUND")
        
        if missing_fields:
            print(f"\n⚠️  MISSING FIELDS: {len(missing_fields)}")
            for field in missing_fields:
                print(f"      {field}")
        
        # Sample data to check for column alignment issues
        print(f"\n🔍 STEP 3: SAMPLE DATA ANALYSIS")
        
        # Read specific rows where errors occurred
        error_row_ranges = [7975, 35812, 17044]  # From error messages
        
        for error_row in error_row_ranges:
            if error_row < 100000:  # Only check early rows for now
                try:
                    print(f"\n   📍 Analyzing row {error_row}:")
                    
                    # Read around the error row
                    df_sample = pd.read_csv(
                        tsv_path,
                        sep='\t',
                        skiprows=error_row,
                        nrows=3,
                        dtype=str,
                        encoding='utf-8',
                        engine='python',
                        quoting=csv.QUOTE_NONE,
                        on_bad_lines='skip',
                        header=None
                    )
                    
                    df_sample.columns = df_header.columns[:len(df_sample.columns)]
                    
                    # Check coordinate fields specifically
                    if 'PA_Latitude' in df_sample.columns and 'PA_Longitude' in df_sample.columns:
                        for idx, row in df_sample.iterrows():
                            lat_val = row.get('PA_Latitude', 'N/A')
                            lon_val = row.get('PA_Longitude', 'N/A')
                            state_val = row.get('Property_State', 'N/A')
                            
                            print(f"      Row {error_row + idx}:")
                            print(f"         Latitude: '{lat_val}'")
                            print(f"         Longitude: '{lon_val}'")
                            print(f"         State: '{state_val}'")
                            
                            # Check for obvious misalignment
                            if lat_val == 'AL' or lon_val == 'AL':
                                print(f"      🚨 COLUMN MISALIGNMENT DETECTED!")
                                print(f"         State value appearing in coordinate field")
                
                except Exception as e:
                    print(f"      ❌ Error reading row {error_row}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in column diagnosis: {e}")
        return False

def diagnose_encoding_issues():
    """Diagnose UTF8 and encoding problems"""
    
    print(f"\n" + "=" * 60)
    print("🔍 DIAGNOSING ENCODING ISSUES")
    print("🎯 Goal: Find UTF8 problems and null characters")
    print("=" * 60)
    
    tsv_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    try:
        # Check file encoding
        print("📋 STEP 1: FILE ENCODING DETECTION")
        
        # Read first few bytes to check encoding
        with open(tsv_path, 'rb') as f:
            raw_bytes = f.read(1000)
            
        try:
            decoded_utf8 = raw_bytes.decode('utf-8')
            print("   ✅ UTF-8 decoding successful for sample")
        except UnicodeDecodeError as e:
            print(f"   ❌ UTF-8 decoding failed: {e}")
        
        # Check for null characters
        if b'\x00' in raw_bytes:
            print("   ⚠️  NULL characters found in file!")
            null_positions = [i for i, byte in enumerate(raw_bytes) if byte == 0]
            print(f"      Null positions in first 1000 bytes: {null_positions[:5]}")
        else:
            print("   ✅ No null characters in sample")
        
        # Check for specific encoding issues around error row
        print(f"\n📋 STEP 2: ERROR ROW ENCODING CHECK")
        
        # The error mentioned line 17044 with null character
        try:
            with open(tsv_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= 17040 and i <= 17050:  # Around error line
                        lines.append((i, line))
                    if i > 17050:
                        break
                
                for line_num, line_content in lines:
                    if '\x00' in line_content:
                        print(f"   🚨 NULL character found in line {line_num}")
                        # Show context around null character
                        null_pos = line_content.find('\x00')
                        start = max(0, null_pos - 20)
                        end = min(len(line_content), null_pos + 20)
                        context = line_content[start:end].replace('\x00', '<NULL>')
                        print(f"      Context: '{context}'")
                    
                    if len(line_content.split('\t')) != 449:  # Expected column count
                        col_count = len(line_content.split('\t'))
                        print(f"   ⚠️  Line {line_num}: {col_count} columns (expected 449)")
        
        except Exception as e:
            print(f"   ❌ Error reading specific lines: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in encoding diagnosis: {e}")
        return False

def generate_fix_recommendations():
    """Generate specific recommendations to fix the issues"""
    
    print(f"\n" + "=" * 60)
    print("🔧 FIX RECOMMENDATIONS")
    print("=" * 60)
    
    print("📋 IMMEDIATE FIXES NEEDED:")
    print("   1. 🔧 Enhanced data cleaning for null characters")
    print("   2. 📊 Column validation before database insert")
    print("   3. 🔍 UTF-8 encoding handling with error recovery")
    print("   4. ⚠️  Row-by-row error logging for debugging")
    print("   5. 🎯 Field-by-field validation with type checking")
    
    print(f"\n🚀 ENHANCED LOADER REQUIREMENTS:")
    print("   ✅ Strip null characters (\\x00) from all fields")
    print("   ✅ Validate data types before database insert")
    print("   ✅ Log specific rows that fail validation")
    print("   ✅ Handle UTF-8 encoding errors gracefully")
    print("   ✅ Verify column count matches expected 449")
    print("   ✅ Skip malformed rows instead of failing entire chunks")
    
    print(f"\n🎯 SUCCESS CRITERIA:")
    print("   📊 Load all 5,000,000 records from TSV")
    print("   🔍 Zero records lost to data quality issues")
    print("   ✅ All coordinate fields contain valid numeric data")
    print("   🗺️  All state fields contain valid 2-character codes")

if __name__ == "__main__":
    print("🚀 STARTING DATA QUALITY DIAGNOSIS")
    
    success1 = diagnose_column_misalignment()
    success2 = diagnose_encoding_issues()
    generate_fix_recommendations()
    
    overall_success = success1 and success2
    print(f"\n🎯 DIAGNOSIS: {'COMPLETE' if overall_success else 'FAILED'}")
    exit(0 if overall_success else 1) 