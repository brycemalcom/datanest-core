#!/usr/bin/env python3
"""
Quick Test Loader - Debug where hangs occur
"""

import csv
import time
import pandas as pd
import os

# Set CSV limits first
try:
    csv.field_size_limit(2147483647)
    print(f"✅ CSV limit: {csv.field_size_limit():,} bytes")
except OverflowError:
    csv.field_size_limit(1000000000)
    print(f"✅ CSV limit: {csv.field_size_limit():,} bytes")

def test_file_reading():
    """Test just reading the first TSV file"""
    print("🔍 Testing file reading...")
    
    # Find first TSV file
    tsv_pattern = "Quantarium_OpenLien_*.TSV"
    tsv_files = [f for f in os.listdir('.') if f.startswith('Quantarium_OpenLien_') and f.endswith('.TSV')]
    
    if not tsv_files:
        print("❌ No TSV files found in current directory")
        return
    
    file_path = tsv_files[0]
    print(f"📁 Testing: {file_path}")
    
    try:
        print("⏱️ Starting chunk reader...")
        chunk_reader = pd.read_csv(
            file_path, 
            sep='\t', 
            chunksize=1000,  # Very small chunks
            dtype=str, 
            encoding='utf-8', 
            engine='python',
            quoting=csv.QUOTE_NONE, 
            on_bad_lines='skip',
            nrows=5000  # Only first 5000 rows
        )
        
        chunk_count = 0
        for chunk_num, chunk in enumerate(chunk_reader, 1):
            print(f"✅ Chunk {chunk_num}: {len(chunk)} rows")
            chunk_count += 1
            
            if chunk_count >= 3:  # Just test first 3 chunks
                print("🛑 Stopping after 3 chunks for testing")
                break
                    
        print("🎉 File reading test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Quick Test Loader")
    print("=" * 40)
    test_file_reading() 