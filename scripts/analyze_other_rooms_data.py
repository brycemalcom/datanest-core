#!/usr/bin/env python3
"""
Analyze Other_Rooms field data to understand data quality issue
"""

import pandas as pd
import csv
import os

def analyze_other_rooms():
    """Analyze actual Other_Rooms data in TSV file"""
    
    print("🔍 ANALYZING OTHER_ROOMS DATA QUALITY")
    print("=" * 50)
    
    file_path = r'C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV'
    
    if not os.path.exists(file_path):
        print(f"❌ TSV file not found: {file_path}")
        return
    
    try:
        # Read just headers first
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            headers = next(reader)
        
        print(f"✅ TSV Headers loaded: {len(headers)} total fields")
        
        # Find Other_Rooms field
        if 'Other_Rooms' in headers:
            idx = headers.index('Other_Rooms')
            print(f"🔍 Other_Rooms found at column {idx}")
            
            # Sample data to understand values
            print("📊 Sampling Other_Rooms data...")
            df_sample = pd.read_csv(file_path, sep='\t', nrows=1000, usecols=['Other_Rooms'], dtype=str)
            
            print(f"📈 Total sample records: {len(df_sample)}")
            print(f"📊 Unique values in Other_Rooms:")
            
            value_counts = df_sample['Other_Rooms'].value_counts().head(20)
            for val, count in value_counts.items():
                print(f"   '{val}': {count} occurrences ({count/len(df_sample)*100:.1f}%)")
            
            # Check for Y/N patterns specifically
            yn_patterns = df_sample['Other_Rooms'].isin(['Y', 'N', 'y', 'n'])
            yn_count = yn_patterns.sum()
            
            print(f"\n🎯 Y/N Pattern Analysis:")
            print(f"   Y/N values: {yn_count} out of {len(df_sample)} ({yn_count/len(df_sample)*100:.1f}%)")
            
            if yn_count > 0:
                print(f"   ⚠️  CRITICAL: Converting Y/N to NULL would lose {yn_count} data points!")
                print(f"   ✅ SOLUTION: Preserve as VARCHAR(5) to maintain data integrity")
            else:
                print(f"   ℹ️  No Y/N values found in sample")
            
        else:
            print("❌ Other_Rooms field not found in TSV headers")
            print("📋 Available headers containing 'room':")
            room_headers = [h for h in headers if 'room' in h.lower()]
            for h in room_headers:
                print(f"   - {h}")
    
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_other_rooms() 