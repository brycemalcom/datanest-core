#!/usr/bin/env python3
"""
Test multiprocessing vs single-threaded processing
"""

import time
import logging
from simple_parallel_loader import SimpleParallelLoader, process_tsv_file_worker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(process)d - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_single_threaded():
    """Test single-threaded processing"""
    print("🧵 TESTING SINGLE-THREADED PROCESSING:")
    print("=" * 50)
    
    loader = SimpleParallelLoader()
    file_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    start_time = time.time()
    print(f"🚀 Starting single-threaded processing of file...")
    
    try:
        result = loader.process_single_file(file_path)
        elapsed = time.time() - start_time
        
        if result['success']:
            print(f"✅ SINGLE-THREADED SUCCESS: {result['total_inserted']} records in {elapsed:.2f} seconds")
            return True
        else:
            print(f"❌ SINGLE-THREADED FAILED: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ SINGLE-THREADED EXCEPTION after {elapsed:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_worker_function():
    """Test the worker function directly"""
    print("\n👷 TESTING WORKER FUNCTION DIRECTLY:")
    print("=" * 50)
    
    file_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    start_time = time.time()
    print(f"🚀 Starting direct worker function...")
    
    try:
        result = process_tsv_file_worker(file_path)
        elapsed = time.time() - start_time
        
        if result['success']:
            print(f"✅ WORKER FUNCTION SUCCESS: {result['total_inserted']} records in {elapsed:.2f} seconds")
            return True
        else:
            print(f"❌ WORKER FUNCTION FAILED: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ WORKER FUNCTION EXCEPTION after {elapsed:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 MULTIPROCESSING vs SINGLE-THREADED TEST")
    print("=" * 60)
    
    # Test 1: Single-threaded
    success_single = test_single_threaded()
    
    # Test 2: Worker function directly
    if success_single:
        test_worker_function()
    else:
        print("\n⚠️ Skipping worker test due to single-threaded failure")
    
    print("\n" + "=" * 60)
    print("�� Test complete!") 