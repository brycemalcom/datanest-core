#!/usr/bin/env python3
"""
Comprehensive CSV field limit diagnosis and testing
"""

import csv
import pandas as pd
import multiprocessing
import os

def test_current_limits():
    """Test what limits are currently in effect"""
    print("🔍 Current CSV Field Limit Diagnosis")
    print("=" * 50)
    
    # Test 1: Check current limit
    current_limit = csv.field_size_limit()
    print(f"Current CSV field limit: {current_limit:,} bytes ({current_limit/1024/1024:.1f} MB)")
    
    # Test 2: Try to set 10MB and verify
    try:
        csv.field_size_limit(10_000_000)
        new_limit = csv.field_size_limit()
        print(f"After setting 10MB: {new_limit:,} bytes ({new_limit/1024/1024:.1f} MB)")
        success = new_limit == 10_000_000
        print(f"Setting successful: {'✅' if success else '❌'}")
    except Exception as e:
        print(f"❌ Failed to set limit: {e}")
    
    # Test 3: Try reading a problematic file
    try:
        print(f"\n📋 Testing file reading with current limit...")
        sample_file = "C:\\DataNest-TSV-Files\\extracted-tsv\\Quantarium_OpenLien_20250414_00001.TSV"
        
        # Just try to read the header to see if it works
        sample_data = pd.read_csv(sample_file, sep='\t', nrows=1, dtype=str, engine='python')
        print(f"✅ Successfully read header with {len(sample_data.columns)} columns")
        
        # Try reading more rows
        sample_data = pd.read_csv(sample_file, sep='\t', nrows=100, dtype=str, engine='python')
        print(f"✅ Successfully read 100 rows")
        
    except Exception as e:
        print(f"❌ Failed to read file: {e}")

def worker_test_limit():
    """Test limit in a worker process"""
    # Set limit in worker
    import csv
    csv.field_size_limit(10_000_000)
    
    current_limit = csv.field_size_limit()
    print(f"Worker process limit: {current_limit:,} bytes ({current_limit/1024/1024:.1f} MB)")
    
    # Try to read file in worker
    try:
        import pandas as pd
        sample_file = "C:\\DataNest-TSV-Files\\extracted-tsv\\Quantarium_OpenLien_20250414_00001.TSV"
        sample_data = pd.read_csv(sample_file, sep='\t', nrows=50, dtype=str, engine='python')
        return f"✅ Worker: Read {len(sample_data)} rows successfully"
    except Exception as e:
        return f"❌ Worker failed: {e}"

def test_multiprocessing_limits():
    """Test if limits work in multiprocessing"""
    print(f"\n🔄 Testing Multiprocessing CSV Limits")
    print("=" * 50)
    
    with multiprocessing.Pool(1) as pool:
        result = pool.apply(worker_test_limit)
        print(result)

if __name__ == "__main__":
    test_current_limits()
    test_multiprocessing_limits() 