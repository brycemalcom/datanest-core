#!/usr/bin/env python3
"""
Diagnose column misalignment in chunk 3
Check if latitude coordinates are ending up in lsale_price column
"""

import pandas as pd
import csv

def diagnose_column_misalignment():
    tsv_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    print("🔍 DIAGNOSING COLUMN MISALIGNMENT IN CHUNK 3")
    print("=" * 60)
    
    # Read chunk 3 and examine the exact alignment
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
            print(f"\n📦 CHUNK 3 COLUMN ALIGNMENT CHECK:")
            print(f"   Total rows: {len(chunk):,}")
            print(f"   Total columns: {len(chunk.columns)}")
            
            # Check the key columns around line 7975
            target_lines = [7970, 7974, 7975, 7976, 7980]
            relevant_columns = ['LSale_Price', 'PA_Latitude', 'PA_Longitude']
            
            print(f"\n🔍 CHECKING LINES AROUND 7975:")
            
            for line_idx in target_lines:
                if line_idx < len(chunk):
                    print(f"\n   📍 LINE {line_idx}:")
                    for col in relevant_columns:
                        if col in chunk.columns:
                            value = chunk.iloc[line_idx][col]
                            print(f"      {col:15}: '{value}'")
                            
                            # Check if LSale_Price contains latitude-like values
                            if col == 'LSale_Price' and pd.notna(value) and value != '':
                                try:
                                    float_val = float(str(value))
                                    # Latitude range is roughly 25-50 for continental US
                                    if 25.0 <= float_val <= 50.0:
                                        print(f"      🚨 LATITUDE-LIKE VALUE IN SALE PRICE: {float_val}")
                                        print(f"         This is DEFINITELY a column misalignment!")
                                except:
                                    pass
            
            # Check a broader sample for pattern detection
            print(f"\n📊 BROADER PATTERN ANALYSIS:")
            lsale_column = chunk['LSale_Price'] if 'LSale_Price' in chunk.columns else None
            latitude_column = chunk['PA_Latitude'] if 'PA_Latitude' in chunk.columns else None
            
            if lsale_column is not None:
                # Look for latitude-like values in sale price column
                latitude_like_in_sale = []
                for idx, val in enumerate(lsale_column):
                    if pd.notna(val) and val != '':
                        try:
                            float_val = float(str(val))
                            if 25.0 <= float_val <= 50.0:  # Latitude range
                                latitude_like_in_sale.append((idx, float_val))
                                if len(latitude_like_in_sale) <= 5:  # Show first 5
                                    print(f"   🚨 Row {idx}: LSale_Price = {float_val} (latitude-like!)")
                        except:
                            pass
                
                print(f"\n📈 SUMMARY:")
                print(f"   Total latitude-like values in LSale_Price: {len(latitude_like_in_sale)}")
                
                if len(latitude_like_in_sale) > 0:
                    print(f"   🚨 CONFIRMED: Column misalignment detected!")
                    print(f"   💡 SOLUTION: Fix column mapping, not decimal formatting")
                else:
                    print(f"   ✅ No obvious misalignment detected")
            
            break
    
    print(f"\n🎯 CONCLUSION:")
    print(f"   If latitude-like values appear in LSale_Price, we have column shifting")
    print(f"   This requires fixing the CSV parsing/column mapping, not decimal conversion")

if __name__ == "__main__":
    diagnose_column_misalignment() 