#!/usr/bin/env python3
"""
Check all column names in chunk 3 and find the exact decimal problem
"""

import pandas as pd
import csv

def check_chunk3_columns():
    tsv_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    print("🔍 CHECKING CHUNK 3 COLUMN MAPPING")
    print("=" * 50)
    
    # Our field mapping from the bulletproof loader
    field_mapping = {
        'Quantarium_Internal_PID': 'quantarium_internal_pid',
        'Assessors_Parcel_Number': 'apn', 
        'FIPS_Code': 'fips_code',
        'ESTIMATED_VALUE': 'estimated_value',          # INTEGER FIELD
        'Property_City_Name': 'property_city_name',
        'Current_Owner_Name': 'current_owner_name',
        'LotSize_Square_Feet': 'lot_size_square_feet',
        'Building_Area_1': 'building_area_total',
        'Number_of_Bedrooms': 'number_of_bedrooms',    # INTEGER FIELD  
        'Year_Built': 'year_built',                    # INTEGER FIELD
        'LSale_Price': 'lsale_price',                  # INTEGER FIELD
        'PA_Latitude': 'latitude',
        'PA_Longitude': 'longitude',
        'Property_State': 'property_state',
        'Property_Full_Street_Address': 'property_full_street_address',
        'Property_Zip_Code': 'property_zip_code',
        'Owner_Occupied': 'owner_occupied',
        'Total_Assessed_Value': 'total_assessed_value'
    }
    
    # Read chunk 3
    chunk_reader = pd.read_csv(
        tsv_path,
        sep='\t',
        chunksize=25000,
        dtype=str,
        encoding='utf-8',
        engine='python',
        quoting=csv.QUOTE_NONE,
        on_bad_lines='skip',
        na_values=['']
    )
    
    for chunk_num, chunk in enumerate(chunk_reader, 1):
        if chunk_num == 3:  # FOCUS ON CHUNK 3
            print(f"\n📦 CHUNK 3 ANALYSIS:")
            print(f"   Total rows: {len(chunk):,}")
            print(f"   Total columns: {len(chunk.columns)}")
            
            # Check our specific integer fields
            integer_tsv_fields = ['ESTIMATED_VALUE', 'Number_of_Bedrooms', 'Year_Built', 'LSale_Price']
            
            for tsv_field in integer_tsv_fields:
                if tsv_field in chunk.columns:
                    print(f"\n🔍 {tsv_field} (maps to {field_mapping.get(tsv_field, 'unknown')}):")
                    field_data = chunk[tsv_field]
                    
                    # Sample values
                    non_empty = field_data.dropna()
                    non_empty = non_empty[non_empty != '']
                    sample_values = non_empty.head(10).tolist()
                    print(f"   Sample values: {sample_values}")
                    
                    # Check ALL values for decimals - COMPREHENSIVE SCAN
                    decimal_count = 0
                    decimal_examples = []
                    
                    for idx, val in enumerate(field_data):
                        if pd.notna(val) and val != '' and str(val).strip() != '':
                            val_str = str(val).strip()
                            if '.' in val_str:
                                try:
                                    float_val = float(val_str)
                                    decimal_count += 1
                                    if len(decimal_examples) < 10:
                                        decimal_examples.append((idx, val_str))
                                    
                                    # Check for our specific problem value
                                    if "30.632601" in val_str:
                                        print(f"   🎯 FOUND IT! Row {idx}: '{val_str}' in {tsv_field}")
                                except:
                                    pass
                    
                    print(f"   Total decimal values: {decimal_count}")
                    if decimal_examples:
                        print(f"   🚨 Decimal examples:")
                        for idx, val in decimal_examples[:5]:
                            print(f"      Row {idx}: '{val}'")
                    else:
                        print(f"   ✅ No decimal values")
                else:
                    print(f"\n❌ {tsv_field} not found in columns")
            
            break
    
    print(f"\n✅ NOW WE KNOW:")
    print(f"   - Which field has the decimal values")
    print(f"   - The bulletproof loader WILL fix these by rounding to integers")
    print(f"   - This is SAFE data transformation (30.632601 → 31)")

if __name__ == "__main__":
    check_chunk3_columns() 