#!/usr/bin/env python3
"""
Test script to isolate pd.read_csv() hanging issue
"""

import pandas as pd
import csv
import sys
import time

# Set maximum CSV field size limit
try:
    csv.field_size_limit(2147483647)  # 2GB
    print(f"✅ CSV field size limit: {csv.field_size_limit():,} bytes")
except OverflowError:
    csv.field_size_limit(1000000000)  # 1GB fallback
    print(f"✅ CSV field size limit: {csv.field_size_limit():,} bytes")

def test_file_structure():
    """Test the first few lines of the file"""
    print("\n🔍 TESTING FILE STRUCTURE:")
    print("=" * 50)
    
    file_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    try:
        with open(file_path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                line_preview = line[:100].replace('\t', ' | ')
                print(f"Line {i:2d}: {line_preview}")
                if i > 10:
                    break
        print("✅ File structure looks normal")
    except Exception as e:
        print(f"❌ Error reading file structure: {e}")

def test_pandas_read():
    """Test pd.read_csv() in isolation"""
    print("\n📥 TESTING PANDAS READ_CSV:")
    print("=" * 50)
    
    file_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    start_time = time.time()
    print("📥 Starting pd.read_csv()...")
    
    try:
        df = pd.read_csv(
            file_path,
            sep='\t',
            engine='python',
            quoting=csv.QUOTE_NONE,
            on_bad_lines='warn',
            encoding='utf-8',
            nrows=100  # Only read first 100 rows for testing
        )
        
        elapsed = time.time() - start_time
        print(f"✅ READ COMPLETE: {df.shape} in {elapsed:.2f} seconds")
        print(f"   Columns: {len(df.columns)}")
        print(f"   First few columns: {list(df.columns[:5])}")
        
        return True
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ READ FAILED after {elapsed:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pandas_chunked():
    """Test pd.read_csv() with chunking"""
    print("\n🔄 TESTING PANDAS CHUNKED READ:")
    print("=" * 50)
    
    file_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    start_time = time.time()
    print("📥 Starting chunked pd.read_csv()...")
    
    try:
        chunk_reader = pd.read_csv(
            file_path,
            sep='\t',
            chunksize=1000,  # Small chunks for testing
            engine='python',
            quoting=csv.QUOTE_NONE,
            on_bad_lines='warn',
            encoding='utf-8'
        )
        
        print("✅ Chunk reader created, reading first chunk...")
        
        first_chunk = next(chunk_reader)
        elapsed = time.time() - start_time
        
        print(f"✅ FIRST CHUNK READ: {first_chunk.shape} in {elapsed:.2f} seconds")
        print(f"   Columns: {len(first_chunk.columns)}")
        
        return True
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ CHUNKED READ FAILED after {elapsed:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 ISOLATION TEST: pd.read_csv() hanging issue")
    print("=" * 60)
    
    # Test 1: File structure
    test_file_structure()
    
    # Test 2: Simple pandas read
    success_simple = test_pandas_read()
    
    # Test 3: Chunked pandas read  
    if success_simple:
        test_pandas_chunked()
    else:
        print("\n⚠️ Skipping chunked test due to simple read failure")
    
    print("\n" + "=" * 60)
    print("�� Test complete!") 