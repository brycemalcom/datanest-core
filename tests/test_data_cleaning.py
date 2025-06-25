#!/usr/bin/env python3
"""
Test Data Cleaning for DataNest Loader
Validates that our data type fixes work properly
"""

import pandas as pd
import psycopg2
from simple_parallel_loader import SimpleParallelLoader

def test_data_cleaning():
    """Test our data cleaning with problematic data samples"""
    print("🧪 Testing Data Cleaning Fixes...")
    
    loader = SimpleParallelLoader()
    
    # Create test data with problematic values
    test_data = {
        'Quantarium_Internal_PID': ['123456', '789012'],
        'Assessors_Parcel_Number': ['ABC-123', 'DEF-456'],
        'FIPS_Code': ['1001', '1003'],
        'ESTIMATED_VALUE': ['', '150000'],  # Empty string issue
        'PRICE_RANGE_MAX': ['200000', ''],  # Empty string issue  
        'CONFIDENCE_SCORE': ['70', 'NULL'], # NULL string issue
        'QVM_asof_Date': [20250409, ''],    # Integer date issue
        'Property_State': ['AL', 'TX'],
        'PA_Latitude': ['33.5', ''],        # Empty coordinate
        'PA_Longitude': ['-86.8', 'null']   # null string
    }
    
    test_chunk = pd.DataFrame(test_data)
    print(f"📋 Original test data:")
    print(test_chunk)
    print()
    
    # Clean the data
    cleaned_chunk = loader.clean_chunk_data(test_chunk)
    print(f"🧹 Cleaned data:")
    print(cleaned_chunk)
    print()
    print(f"📊 Data types:")
    print(cleaned_chunk.dtypes)
    print()
    
    # Check specific fixes
    print("🔍 Validation Results:")
    
    # Check date conversion
    date_val = cleaned_chunk['qvm_asof_date'].iloc[0]
    if date_val == '2025-04-09':
        print("  ✅ Date conversion: 20250409 → 2025-04-09")
    else:
        print(f"  ❌ Date conversion failed: {date_val}")
    
    # Check empty numeric handling
    empty_estimate = cleaned_chunk['estimated_value'].iloc[0]
    if pd.isna(empty_estimate):
        print("  ✅ Empty numeric: '' → NaN")
    else:
        print(f"  ❌ Empty numeric failed: {empty_estimate}")
    
    # Check NULL string handling
    null_confidence = cleaned_chunk['confidence_score'].iloc[1]
    if pd.isna(null_confidence):
        print("  ✅ NULL string: 'NULL' → NaN")
    else:
        print(f"  ❌ NULL string failed: {null_confidence}")

def test_single_record_insert():
    """Test inserting a single cleaned record"""
    print("\n🔌 Testing Database Insert...")
    
    loader = SimpleParallelLoader()
    
    try:
        # Test connection
        conn = loader.get_connection()
        cursor = conn.cursor()
        
        # Get current count
        cursor.execute('SELECT COUNT(*) FROM datnest.properties;')
        count_before = cursor.fetchone()[0]
        
                 # Create a single test record
         test_data = {
             'quantarium_internal_pid': ['TEST123'],
             'apn': ['TEST-PARCEL'],
             'fips_code': ['9999'],
             'estimated_value': [125000.0],
             'confidence_score': [75.0],
             'qvm_asof_date': ['2025-04-09'],
             'property_state': ['AL'],  # Use proper 2-char state code
             'property_city_name': ['Test City'],
             'latitude': [33.5],
             'longitude': [-86.8]
         }
        
        test_record = pd.DataFrame(test_data)
        
        # Try to insert
        result = loader.insert_chunk_batch(test_record, "TEST")
        
        if result > 0:
            print(f"  ✅ Successfully inserted {result} test record")
            
            # Verify it's there
            cursor.execute('SELECT COUNT(*) FROM datnest.properties;')
            count_after = cursor.fetchone()[0]
            print(f"  📊 Record count: {count_before} → {count_after}")
            
            # Clean up test record
            cursor.execute("DELETE FROM datnest.properties WHERE quantarium_internal_pid = 'TEST123';")
            conn.commit()
            print("  🧹 Test record cleaned up")
        else:
            print("  ❌ Insert failed")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")

def main():
    """Run all tests"""
    test_data_cleaning()
    test_single_record_insert()
    print("\n🎉 Testing complete!")

if __name__ == "__main__":
    main() 