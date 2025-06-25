#!/usr/bin/env python3
"""
DataNest Status Check
Comprehensive status of files, extraction, and database
"""

import os
import glob
from pathlib import Path

def check_file_status():
    """Check status of ZIP and TSV files"""
    print("🚀 DataNest Core Platform - Status Check")
    print("=" * 50)
    
    # Paths
    zip_path = "C:\\DataNest-TSV-Files\\downloaded-zip"
    tsv_path = "C:\\DataNest-TSV-Files\\extracted-tsv"
    completed_path = "C:\\DataNest-TSV-Files\\completed"
    
    # Check ZIP files
    zip_files = glob.glob(os.path.join(zip_path, "*.zip"))
    print(f"📁 ZIP Files: {len(zip_files)} found")
    
    total_zip_size = 0
    for file in zip_files:
        size_gb = os.path.getsize(file) / (1024**3)
        total_zip_size += size_gb
    
    print(f"   Total compressed size: {total_zip_size:.1f} GB")
    
    # Check TSV files
    tsv_files = glob.glob(os.path.join(tsv_path, "*.TSV"))
    print(f"📄 TSV Files: {len(tsv_files)} extracted")
    
    total_tsv_size = 0
    for file in tsv_files:
        size_gb = os.path.getsize(file) / (1024**3)
        total_tsv_size += size_gb
        file_name = os.path.basename(file)
        print(f"   ✅ {file_name}: {size_gb:.1f} GB")
    
    print(f"   Total extracted size: {total_tsv_size:.1f} GB")
    
    # Calculate progress
    total_files_expected = 32
    extraction_progress = (len(tsv_files) / total_files_expected) * 100
    print(f"   📊 Extraction progress: {extraction_progress:.1f}% ({len(tsv_files)}/{total_files_expected})")
    
    # Estimate remaining
    if len(tsv_files) > 0:
        avg_tsv_size = total_tsv_size / len(tsv_files)
        remaining_files = total_files_expected - len(tsv_files)
        estimated_remaining_size = remaining_files * avg_tsv_size
        print(f"   🔮 Estimated remaining: {remaining_files} files, {estimated_remaining_size:.1f} GB")
        print(f"   🎯 Total when complete: ~{total_tsv_size + estimated_remaining_size:.1f} GB")
    
    # Check completed files
    completed_files = glob.glob(os.path.join(completed_path, "*.TSV"))
    if completed_files:
        print(f"✅ Completed Files: {len(completed_files)} processed")
    
    # Disk space check
    import shutil
    total, used, free = shutil.disk_usage("C:\\")
    free_gb = free / (1024**3)
    print(f"💾 Disk Space: {free_gb:.0f} GB free")
    
    space_needed = 195 - total_tsv_size  # ~195GB total expected
    if free_gb > space_needed * 1.2:  # 20% buffer
        print(f"   ✅ Sufficient space ({space_needed:.0f} GB needed)")
    else:
        print(f"   ⚠️  May need more space ({space_needed:.0f} GB needed)")

def check_infrastructure():
    """Check AWS infrastructure status"""
    print("\n🏗️ Infrastructure Status")
    print("-" * 30)
    
    try:
        import subprocess
        result = subprocess.run(['aws', 'rds', 'describe-db-instances', 
                               '--db-instance-identifier', 'datnest-core-postgres',
                               '--query', 'DBInstances[0].[DBInstanceStatus,DBInstanceClass]',
                               '--output', 'text'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            status, instance_class = result.stdout.strip().split('\t')
            print(f"   📊 RDS Status: {status}")
            print(f"   🖥️  Instance Class: {instance_class}")
            
            if instance_class == "db.r5.4xlarge":
                print("   ✅ Scaled for high-performance loading")
            else:
                print("   ⚠️  May need scaling for optimal performance")
        else:
            print("   ❌ Could not check RDS status")
    except Exception as e:
        print(f"   ❌ Infrastructure check failed: {e}")

def check_database_connection():
    """Check database connectivity"""
    print("\n🔗 Database Connection")
    print("-" * 25)
    
    try:
        import psycopg2
        import sys
        import os
        
        # Add src to path for secure config
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from config import get_db_config
        
        # SECURITY: Load database config securely
        db_config = get_db_config()
        conn = psycopg2.connect(
            **db_config,
            connect_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM datnest.properties;')
        count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM datnest.properties WHERE estimated_value IS NOT NULL;')
        qvm_count = cursor.fetchone()[0]
        coverage = (qvm_count / count * 100) if count > 0 else 0
        
        print(f"   ✅ Database connected successfully")
        print(f"   📊 Current records: {count:,}")
        print(f"   💰 QVM Coverage: {qvm_count:,} records ({coverage:.1f}%)")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        print("   🔧 Need to establish SSH tunnel or check connectivity")
        return False

def check_loading_readiness():
    """Check if we're ready for parallel loading"""
    print("\n🚀 Loading Readiness")
    print("-" * 20)
    
    tsv_files = glob.glob("C:\\DataNest-TSV-Files\\extracted-tsv\\*.TSV")
    
    if len(tsv_files) >= 3:
        print(f"   ✅ Ready for parallel loading with {len(tsv_files)} files")
        print("   🎯 Can start with current files while extraction continues")
        
        # Calculate estimated processing time
        estimated_records_per_file = 5000000  # 5M records per file average
        total_estimated_records = len(tsv_files) * estimated_records_per_file
        
        # At 10,000 records/second with parallel processing
        estimated_minutes = (total_estimated_records / 10000) / 60
        
        print(f"   📈 Estimated records: {total_estimated_records:,}")
        print(f"   ⏱️  Estimated loading time: {estimated_minutes:.0f} minutes")
        
        return True
    else:
        print(f"   ⏳ Need more files extracted ({len(tsv_files)} ready)")
        return False

def main():
    """Main status check"""
    check_file_status()
    check_infrastructure()
    db_ready = check_database_connection()
    loading_ready = check_loading_readiness()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    if loading_ready and db_ready:
        print("🎉 READY TO START PARALLEL LOADING!")
        print("   Run: python parallel_loader.py")
    elif loading_ready:
        print("⚠️  Files ready, but need database connection")
        print("   1. Establish SSH tunnel")
        print("   2. Run: python parallel_loader.py")
    else:
        print("⏳ Still preparing...")
        print("   1. Continue file extraction")
        print("   2. Establish database connection")
        print("   3. Start parallel loading")

if __name__ == "__main__":
    main() 