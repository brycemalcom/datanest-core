#!/usr/bin/env python3
"""
Find which integer field in chunk 3 has the problematic decimal values
"""

import pandas as pd
import csv

def find_all_decimal_integers():
    tsv_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    print("🔍 SCANNING ALL INTEGER FIELDS IN CHUNK 3")
    print("=" * 50)
    
    # Fields that get processed as integers
    integer_fields = ['Year_Built', 'Number_of_Bedrooms', 'ESTIMATED_VALUE', 'LSale_Price']
    
    # Read chunks and focus on chunk 3
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
            print(f"\n📦 CHUNK 3 INTEGER FIELDS SCAN:")
            print(f"   Total rows: {len(chunk):,}")
            print(f"   Checking fields: {integer_fields}")
            
            for field in integer_fields:
                if field in chunk.columns:
                    print(f"\n🔍 Checking {field}:")
                    field_data = chunk[field]
                    
                    # Check ALL values for decimals
                    decimal_count = 0
                    decimal_examples = []
                    
                    for idx, val in enumerate(field_data):
                        if pd.notna(val) and val != '':
                            val_str = str(val).strip()
                            if '.' in val_str:
                                try:
                                    float_val = float(val_str)
                                    decimal_count += 1
                                    if len(decimal_examples) < 10:
                                        decimal_examples.append((idx, val_str))
                                except:
                                    pass  # Not a valid number
                    
                    print(f"   Total decimal values: {decimal_count}")
                    if decimal_examples:
                        print(f"   🚨 FOUND THE CULPRIT! Examples:")
                        for idx, val in decimal_examples:
                            print(f"      Row {idx}: '{val}'")
                            # Check if this is our specific problematic value
                            if "30.632601" in val:
                                print(f"      ⭐ BINGO! Found the exact error value!")
                    else:
                        print(f"   ✅ No decimal values found")
                else:
                    print(f"\n❌ {field} not found in chunk columns")
            
            break  # Only check chunk 3
    
    print(f"\n🎯 CONCLUSION:")
    print(f"   Now we know which field is causing the 'invalid input syntax for type bigint' error!")

if __name__ == "__main__":
    find_all_decimal_integers() 