#!/usr/bin/env python3
"""
Quick investigation: What's different about chunk 3 vs successful chunks 1,2?
Focus on LSale_Price values
"""

import pandas as pd
import csv

def investigate_chunk_data():
    tsv_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    print("🔍 INVESTIGATING CHUNK DATA DIFFERENCES")
    print("=" * 50)
    
    # Read chunks and examine LSale_Price
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
        if chunk_num > 5:  # Only check first 5 chunks
            break
            
        print(f"\n📦 CHUNK {chunk_num}:")
        print(f"   Rows: {len(chunk):,}")
        
        if 'LSale_Price' in chunk.columns:
            lsale_data = chunk['LSale_Price']
            
            # Basic stats
            non_empty = lsale_data.dropna()
            non_empty = non_empty[non_empty != '']
            
            print(f"   Non-empty LSale_Price values: {len(non_empty)}")
            
            if len(non_empty) > 0:
                # Show sample values
                sample_values = non_empty.head(10).tolist()
                print(f"   Sample values: {sample_values}")
                
                # Check for decimal values (the problem!)
                decimal_values = []
                integer_values = []
                other_values = []
                
                for val in non_empty.head(100):  # Check first 100 non-empty
                    val_str = str(val).strip()
                    if '.' in val_str:
                        try:
                            float_val = float(val_str)
                            decimal_values.append(val_str)
                        except:
                            other_values.append(val_str)
                    elif val_str.isdigit():
                        integer_values.append(val_str)
                    else:
                        other_values.append(val_str)
                
                print(f"   🔢 Integer values: {len(integer_values)} (good)")
                print(f"   🚨 Decimal values: {len(decimal_values)} (PROBLEMATIC!)")
                print(f"   ❓ Other values: {len(other_values)}")
                
                # Show problematic decimal values
                if decimal_values:
                    print(f"   💥 Decimal examples: {decimal_values[:5]}")
                    print(f"   ⚠️  THIS IS THE CHUNK 3 PROBLEM!")
                else:
                    print(f"   ✅ No problematic decimal values found")
        else:
            print(f"   ❌ LSale_Price column not found!")
    
    print(f"\n🎯 CONCLUSION:")
    print(f"   Chunks 1,2 likely have clean integer LSale_Price values")
    print(f"   Chunk 3 has corrupted decimal LSale_Price values like '30.632601'")
    print(f"   Database expects BIGINT (integers) but gets decimal strings")

if __name__ == "__main__":
    investigate_chunk_data() 