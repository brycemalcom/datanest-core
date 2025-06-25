#!/usr/bin/env python3
"""
Read-Only Test - Just analyze TSV data, no database
"""

import csv
import pandas as pd
import time

# CRITICAL: Set CSV field size limit FIRST
try:
    csv.field_size_limit(2147483647)
    print(f"✅ CSV limit: {csv.field_size_limit():,} bytes")
except OverflowError:
    csv.field_size_limit(1000000000)
    print(f"✅ CSV limit: {csv.field_size_limit():,} bytes")

def analyze_first_chunk():
    """Just read and analyze first 1000 rows - no database"""
    file_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    print("🔍 Reading first 1000 rows only...")
    start_time = time.time()
    
    try:
        # Read just first 1000 rows
        chunk = pd.read_csv(
            file_path,
            sep='\t',
            nrows=1000,  # Just first 1000 rows
            dtype=str,
            encoding='utf-8',
            engine='python',
            quoting=csv.QUOTE_NONE,
            on_bad_lines='skip'
        )
        
        elapsed = time.time() - start_time
        print(f"✅ Read {len(chunk)} rows in {elapsed:.1f} seconds")
        print(f"📊 Columns: {len(chunk.columns)}")
        
        # Check key fields
        key_fields = ['Quantarium_Internal_PID', 'ESTIMATED_VALUE', 'Mtg01_loan_number']
        for field in key_fields:
            if field in chunk.columns:
                # Check for extremely long values
                max_len = chunk[field].str.len().max()
                avg_len = chunk[field].str.len().mean()
                print(f"   {field}: max={max_len}, avg={avg_len:.1f}")
                
                # Show examples of long values
                long_mask = chunk[field].str.len() > 100
                if long_mask.any():
                    long_count = long_mask.sum()
                    print(f"   ⚠️ {field}: {long_count} values >100 chars")
        
        print("🎉 Read-only test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_problematic_row():
    """Test reading around row 4460 specifically"""
    file_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    print("🔍 Testing rows around 4460 (the problematic area)...")
    
    try:
        # Read rows 4450-4470 to isolate the problem
        chunk = pd.read_csv(
            file_path,
            sep='\t',
            skiprows=4449,  # Skip to row 4450
            nrows=20,       # Read 20 rows (4450-4470)
            dtype=str,
            encoding='utf-8',
            engine='python',
            quoting=csv.QUOTE_NONE,
            on_bad_lines='skip'
        )
        
        print(f"✅ Read {len(chunk)} rows around the problematic area")
        
        # Check mortgage fields specifically
        mortgage_fields = ['Mtg01_loan_number', 'Mtg02_loan_number']
        for field in mortgage_fields:
            if field in chunk.columns:
                for idx, value in enumerate(chunk[field]):
                    length = len(str(value)) if value else 0
                    if length > 50:  # Suspiciously long
                        print(f"   ⚠️ Row {4450+idx}: {field} = {length} chars")
                        print(f"      Preview: {str(value)[:100]}...")
                        
        return True
        
    except Exception as e:
        print(f"❌ Error testing problematic row: {e}")
        return False

if __name__ == "__main__":
    print("📖 Read-Only TSV Test")
    print("=" * 40)
    
    # Test 1: Basic reading
    if analyze_first_chunk():
        print()
        # Test 2: Problematic row area
        test_problematic_row()
    else:
        print("❌ Basic reading failed") 