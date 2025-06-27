#!/usr/bin/env python3
"""
COMPREHENSIVE FIELD AUDIT - QA Session
Identify exact gaps between Database Schema, TSV Headers, and Loader Mapping

Mission: Close the 54-field gap (395 → 449) for 100% data capture
"""

import os
import sys
import csv

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from config import get_db_config

def comprehensive_field_audit():
    """Three-way audit: Database vs TSV vs Loader"""
    
    print("🔍 COMPREHENSIVE FIELD AUDIT - QA SESSION")
    print("🎯 Goal: Identify 54 missing fields for 100% data capture (395 → 449)")
    print("=" * 70)
    
    # =====================================================
    # STEP 1: ANALYZE TSV HEADERS (TRUTH SOURCE)
    # =====================================================
    
    print("📂 STEP 1: TSV HEADERS ANALYSIS (Truth Source)")
    
    tsv_file = r'C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV'
    
    if not os.path.exists(tsv_file):
        print(f"❌ TSV file not found: {tsv_file}")
        return False
    
    try:
        # Read TSV headers
        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            tsv_headers = next(reader)
        
        print(f"✅ TSV Headers loaded: {len(tsv_headers)} fields")
        print(f"📊 Target field count: 449 (should match TSV headers minus 1)")
        
        # Verify the count matches our target
        if len(tsv_headers) == 450:  # 449 + 1 header row
            print(f"✅ TSV field count verified: {len(tsv_headers)} headers confirmed")
        else:
            print(f"⚠️  TSV field count mismatch: Expected ~450, got {len(tsv_headers)}")
        
    except Exception as e:
        print(f"❌ TSV analysis failed: {e}")
        return False
    
    # =====================================================
    # STEP 2: ANALYZE DATABASE SCHEMA
    # =====================================================
    
    print(f"\n🗄️  STEP 2: DATABASE SCHEMA ANALYSIS")
    
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        
        # Get all columns in properties table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'properties' 
            AND table_schema = 'datnest'
            ORDER BY ordinal_position;
        """)
        
        db_columns = [row[0] for row in cursor.fetchall()]
        
        print(f"✅ Database columns loaded: {len(db_columns)} fields")
        print(f"📊 Database capacity: {len(db_columns)} columns operational")
        
    except Exception as e:
        print(f"❌ Database analysis failed: {e}")
        return False
    
    # =====================================================
    # STEP 3: ANALYZE CURRENT LOADER MAPPING
    # =====================================================
    
    print(f"\n🔧 STEP 3: CURRENT LOADER MAPPING ANALYSIS")
    
    # Import the current loader to get field mapping
    try:
        # Read current loader file to extract field mapping
        loader_file = 'src/loaders/enhanced_production_loader_batch4a.py'
        
        with open(loader_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract field mapping (simplified approach)
        # Count TSV field references in the loader
        mapped_tsv_fields = set()
        
        for header in tsv_headers:
            if f"'{header}'" in content:
                mapped_tsv_fields.add(header)
        
        print(f"✅ Loader mapping analyzed: {len(mapped_tsv_fields)} TSV fields mapped")
        print(f"📊 Current coverage: {len(mapped_tsv_fields)}/{len(tsv_headers)} = {len(mapped_tsv_fields)/len(tsv_headers)*100:.1f}%")
        
    except Exception as e:
        print(f"❌ Loader analysis failed: {e}")
        return False
    
    # =====================================================
    # STEP 4: THREE-WAY GAP ANALYSIS
    # =====================================================
    
    print(f"\n🎯 STEP 4: THREE-WAY GAP ANALYSIS")
    
    # Find unmapped TSV fields
    unmapped_tsv_fields = set(tsv_headers) - mapped_tsv_fields
    
    print(f"📊 GAP ANALYSIS RESULTS:")
    print(f"   🗄️  Database columns: {len(db_columns)}")
    print(f"   📂 TSV headers: {len(tsv_headers)}")
    print(f"   🔧 Loader mapped: {len(mapped_tsv_fields)}")
    print(f"   ❌ UNMAPPED FIELDS: {len(unmapped_tsv_fields)}")
    
    # Show missing field categories
    if unmapped_tsv_fields:
        print(f"\n📋 UNMAPPED TSV FIELDS ({len(unmapped_tsv_fields)} fields):")
        
        # Group by category prefixes
        categories = {}
        for field in sorted(unmapped_tsv_fields):
            # Determine category based on field name patterns
            if field.startswith('Mtg'):
                category = 'Financing/Mortgage'
            elif 'Building' in field or 'Construction' in field:
                category = 'Building Characteristics'
            elif 'Sale' in field or 'Transfer' in field or 'Price' in field:
                category = 'Property Sale'
            elif 'Owner' in field or 'CO_' in field:
                category = 'Ownership'
            elif 'Legal' in field:
                category = 'Property Legal'
            elif 'Tax' in field or 'Assessment' in field or 'Value' in field:
                category = 'County Values/Taxes'
            elif 'Property_' in field and ('Address' in field or 'Street' in field or 'City' in field):
                category = 'Property Location'
            elif 'Lot' in field or 'Land' in field or 'Zoning' in field:
                category = 'Land Characteristics'
            elif 'Foreclosure' in field:
                category = 'Foreclosure'
            else:
                category = 'Other/Uncategorized'
            
            if category not in categories:
                categories[category] = []
            categories[category].append(field)
        
        for category, fields in sorted(categories.items()):
            print(f"\n   📂 {category} ({len(fields)} fields):")
            for field in sorted(fields)[:5]:  # Show first 5 fields
                print(f"      - {field}")
            if len(fields) > 5:
                print(f"      ... and {len(fields)-5} more")
    
    # =====================================================
    # STEP 5: DATABASE CAPACITY CHECK
    # =====================================================
    
    print(f"\n💾 STEP 5: DATABASE CAPACITY CHECK")
    
    # Check if database has capacity for missing fields
    db_mapped_fields = set()
    for header in tsv_headers:
        # Convert TSV header to likely database column name
        db_field = header.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').replace('&', 'and').replace('/', '_')
        if db_field in [col.lower() for col in db_columns]:
            db_mapped_fields.add(header)
    
    missing_db_columns = len(unmapped_tsv_fields) - (len(db_columns) - len(db_mapped_fields))
    
    print(f"📊 Database capacity analysis:")
    print(f"   🗄️  Current columns: {len(db_columns)}")
    print(f"   🔧 TSV fields that can map: {len(db_mapped_fields)}")
    print(f"   ❌ Missing DB columns needed: {max(0, missing_db_columns)}")
    
    if missing_db_columns <= 0:
        print(f"   ✅ Database has sufficient capacity!")
    else:
        print(f"   ⚠️  Need {missing_db_columns} additional database columns")
    
    # =====================================================
    # STEP 6: COMPLETION STRATEGY
    # =====================================================
    
    print(f"\n🚀 STEP 6: COMPLETION STRATEGY")
    
    gap_size = len(unmapped_tsv_fields)
    
    print(f"📊 COMPLETION ROADMAP:")
    print(f"   🎯 Target: 449 total fields")
    print(f"   ✅ Current: {len(mapped_tsv_fields)} fields mapped")
    print(f"   ❌ Gap: {gap_size} fields missing")
    print(f"   📈 Progress: {len(mapped_tsv_fields)/len(tsv_headers)*100:.1f}% complete")
    
    # Priority recommendations
    if categories:
        priority_categories = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)
        
        print(f"\n📋 PRIORITY COMPLETION ORDER:")
        for i, (category, fields) in enumerate(priority_categories[:5], 1):
            print(f"   {i}. {category}: {len(fields)} fields")
    
    # =====================================================
    # STEP 7: ACTION ITEMS
    # =====================================================
    
    print(f"\n✅ STEP 7: ACTION ITEMS FOR 100% DATA CAPTURE")
    
    print(f"🎯 IMMEDIATE ACTIONS:")
    print(f"   1. Fix other_rooms Y/N → NULL issue ✅ COMPLETED")
    print(f"   2. Map {gap_size} remaining TSV fields to database columns")
    print(f"   3. Update loader field mapping for new fields")
    print(f"   4. Test with sample data before production load")
    print(f"   5. Validate 449/449 field completion")
    
    print(f"\n🚀 SUCCESS CRITERIA:")
    print(f"   ✅ All 449 TSV fields mapped and loading")
    print(f"   ✅ Zero data quality issues (no Y/N → NULL)")
    print(f"   ✅ Production performance maintained")
    print(f"   ✅ All 12 categories meet expected field counts")
    
    cursor.close()
    conn.close()
    
    return gap_size < 60  # Success if gap is manageable

if __name__ == "__main__":
    success = comprehensive_field_audit()
    
    if success:
        print(f"\n🎉 AUDIT COMPLETE - Clear path to 100% data capture!")
    else:
        print(f"\n⚠️  Additional analysis needed for completion strategy") 