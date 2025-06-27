#!/usr/bin/env python3
"""
Find the exact decimal values in chunk 3 that are causing the failure
"""

import pandas as pd
import csv

def find_chunk3_decimals():
    tsv_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    print("🔍 SCANNING ALL OF CHUNK 3 FOR DECIMAL VALUES")
    print("=" * 50)
    
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
            print(f"\n📦 CHUNK 3 DEEP SCAN:")
            print(f"   Total rows: {len(chunk):,}")
            
            if 'LSale_Price' in chunk.columns:
                lsale_data = chunk['LSale_Price']
                
                # Check ALL values for decimals
                decimal_positions = []
                decimal_values = []
                
                for idx, val in enumerate(lsale_data):
                    if pd.notna(val) and val != '':
                        val_str = str(val).strip()
                        if '.' in val_str:
                            try:
                                float_val = float(val_str)
                                decimal_positions.append(idx)
                                decimal_values.append(val_str)
                                
                                # Show first 10 problematic values
                                if len(decimal_values) <= 10:
                                    print(f"   🚨 Row {idx}: '{val_str}'")
                            except:
                                pass  # Not a valid number
                
                print(f"\n📊 CHUNK 3 RESULTS:")
                print(f"   Total decimal values found: {len(decimal_values)}")
                
                if decimal_values:
                    print(f"   First 10 decimal values: {decimal_values[:10]}")
                    print(f"   Row positions: {decimal_positions[:10]}")
                    print(f"   \n💡 SOLUTION: These decimal values need to be:")
                    print(f"      Option 1: Rounded to integers (30.632601 → 31)")
                    print(f"      Option 2: Set to NULL (if suspected bad data)")
                    
                    # Show what they would become if rounded
                    print(f"   \n🔧 IF ROUNDED:")
                    for val in decimal_values[:5]:
                        try:
                            rounded = int(round(float(val)))
                            print(f"      {val} → {rounded}")
                        except:
                            print(f"      {val} → NULL (invalid)")
                else:
                    print(f"   ✅ No decimal values found - this is mysterious!")
            
            break  # Only check chunk 3
    
    print(f"\n🎯 FINAL ANSWER:")
    print(f"   The bulletproof loader SHOULD fix these by rounding decimals to integers")
    print(f"   This preserves data while making it database-compatible")

if __name__ == "__main__":
    find_chunk3_decimals() 