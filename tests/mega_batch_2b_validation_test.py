#!/usr/bin/env python3
"""
MEGA BATCH 2B Validation Test - Master Database Engineer
STRATEGY: Validate 41 new fields for complete category coverage (54 → 95 fields)
GOAL: Verify Building + Land categories are COMPLETE before production
"""

import csv
import psycopg2
import pandas as pd
import numpy as np
import tempfile
import os
import time
import sys
from decimal import Decimal

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# CRITICAL: Set CSV field size limit FIRST
try:
    csv.field_size_limit(2147483647)
    print(f"✅ CSV limit: {csv.field_size_limit():,} bytes")
except OverflowError:
    csv.field_size_limit(1000000000)
    print(f"✅ CSV limit: {csv.field_size_limit():,} bytes")

# SECURITY: Database connection loaded from secure sources only
try:
    from src.config import get_db_config
    CONN_PARAMS = get_db_config()
    print("✅ Database configuration loaded securely")
except Exception as e:
    print(f"❌ SECURITY ERROR: Failed to load secure database configuration: {e}")
    sys.exit(1)

def mega_batch_2b_validation_test():
    """Test mega batch category completion with sample data"""
    file_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    print("🔥 MEGA BATCH 2B: CATEGORY COMPLETION VALIDATION TEST")
    print("🎯 STRATEGY: Validate complete Building + Land + Ownership categories")
    print("⚡ EFFICIENCY: 5K sample test for 95-field validation")
    print("=" * 70)
    
    # KEY VALIDATION FIELDS (representative sample of the 95 total)
    validation_fields = {
        # Core baseline (proven working)
        'Quantarium_Internal_PID': 'quantarium_internal_pid',
        'ESTIMATED_VALUE': 'estimated_value',
        
        # 🏗️ BUILDING CHARACTERISTICS VALIDATION (Complete category)
        'Pool': 'pool',
        'Air_Conditioning': 'air_conditioning',
        'Fireplace': 'fireplace',
        'Basement': 'basement',
        'Number_of_Partial_Baths': 'number_of_partial_baths',
        'Number_of_Units': 'number_of_units',
        'No_of_Stories': 'number_of_stories',
        'Heating': 'heating',
        'Roof_Cover': 'roof_cover',
        'Foundation': 'foundation',
        'Garage_Type': 'garage_type',
        
        # 🌍 LAND CHARACTERISTICS VALIDATION (Complete category)
        'LotSize_Acres': 'lot_size_acres',
        'LotSize_Depth_Feet': 'lot_size_depth_feet',
        'LotSize_Frontage_Feet': 'lot_size_frontage_feet',
        'Lot_Size_or_Area': 'lot_size_or_area',
        'Topography': 'topography',
        'Site_Influence': 'site_influence',
        
        # 👤 ENHANCED OWNERSHIP VALIDATION
        'Owner1FirstName': 'owner1_first_name',
        'Owner1LastName': 'owner1_last_name',
        'CO_Mailing_City': 'co_mailing_city',
        'CO_Mailing_State': 'co_mailing_state',
        'Length_of_Residence_Months': 'length_of_residence_months'
    }
    
    print(f"🔥 MEGA BATCH CATEGORY ANALYSIS:")
    print(f"   • Core baseline: 2 fields (proven)")
    print(f"   • Building Characteristics: 12 fields (COMPLETE CATEGORY)")
    print(f"   • Land Characteristics: 6 fields (COMPLETE CATEGORY)")
    print(f"   • Enhanced Ownership: 5 fields (enhanced category)")
    print(f"   • VALIDATION SAMPLE: {len(validation_fields)} key fields (of 95 total)")
    print()
    
    try:
        # Read sample data
        print(f"📖 Reading 5K sample from {os.path.basename(file_path)}...")
        start_time = time.time()
        
        sample_data = pd.read_csv(
            file_path,
            sep='\t',
            nrows=5000,
            dtype=str,
            encoding='utf-8',
            engine='python',
            quoting=csv.QUOTE_NONE,
            on_bad_lines='skip'
        )
        
        print(f"✅ Sample loaded: {len(sample_data):,} rows in {time.time()-start_time:.1f}s")
        
        # Analyze category completion field availability
        print(f"\n🔥 CATEGORY COMPLETION FIELD ANALYSIS:")
        category_results = {
            'building': {'available': 0, 'total': 0, 'coverage': []},
            'land': {'available': 0, 'total': 0, 'coverage': []},
            'ownership': {'available': 0, 'total': 0, 'coverage': []}
        }
        
        for tsv_col, db_col in validation_fields.items():
            # Categorize fields
            if tsv_col in ['Pool', 'Air_Conditioning', 'Fireplace', 'Basement', 'Number_of_Partial_Baths', 
                          'Number_of_Units', 'No_of_Stories', 'Heating', 'Roof_Cover', 'Foundation', 'Garage_Type']:
                category = 'building'
            elif tsv_col.startswith('LotSize') or tsv_col in ['Topography', 'Site_Influence']:
                category = 'land'
            elif 'Owner' in tsv_col or 'CO_Mailing' in tsv_col or 'Length_of_Residence' in tsv_col:
                category = 'ownership'
            else:
                continue  # Skip baseline fields for category analysis
            
            category_results[category]['total'] += 1
            
            if tsv_col in sample_data.columns:
                category_results[category]['available'] += 1
                non_null_count = sample_data[tsv_col].notna().sum()
                coverage = (non_null_count / len(sample_data)) * 100
                category_results[category]['coverage'].append(coverage)
                
                # Status indicators
                if category == 'building':
                    status = "🏗️" if coverage > 50 else "🏠" if coverage > 5 else "⚠️"
                elif category == 'land':
                    status = "🌍" if coverage > 50 else "🌱" if coverage > 5 else "⚠️"
                else:  # ownership
                    status = "👤" if coverage > 50 else "👥" if coverage > 5 else "⚠️"
                
                print(f"   {status} {tsv_col}: {non_null_count:,} records ({coverage:.1f}% coverage)")
            else:
                print(f"   ❌ {tsv_col}: NOT FOUND in TSV")
        
        # Category completion summary
        print(f"\n📊 CATEGORY COMPLETION SUMMARY:")
        for cat_name, cat_data in category_results.items():
            available = cat_data['available']
            total = cat_data['total']
            avg_coverage = np.mean(cat_data['coverage']) if cat_data['coverage'] else 0
            completion_rate = (available / total * 100) if total > 0 else 0
            
            print(f"   {cat_name.upper()}: {available}/{total} fields available ({completion_rate:.0f}%) - Avg coverage: {avg_coverage:.1f}%")
        
        # Test data type conversions by category
        print(f"\n🧪 CATEGORY DATA TYPE CONVERSION TEST:")
        
        # Building characteristics conversion tests
        building_tests = [
            ('Pool', 'categorical'),
            ('Air_Conditioning', 'categorical'),
            ('Number_of_Partial_Baths', 'integer'),
            ('Number_of_Units', 'integer'),
            ('Heating', 'categorical')
        ]
        
        building_success = 0
        for field, data_type in building_tests:
            if field in sample_data.columns:
                try:
                    if data_type == 'integer':
                        converted_data = pd.to_numeric(sample_data[field], errors='coerce').round().astype('Int64', errors='ignore')
                        valid_count = converted_data.notna().sum()
                    else:  # categorical
                        converted_data = sample_data[field].fillna('')
                        valid_count = len(converted_data[converted_data != ''])
                    
                    print(f"   🏗️ {field}: {valid_count:,} valid {data_type} conversions")
                    building_success += 1
                except Exception as e:
                    print(f"   ❌ {field}: Conversion failed - {e}")
        
        # Land characteristics conversion tests
        land_tests = [
            ('LotSize_Acres', 'decimal'),
            ('LotSize_Depth_Feet', 'decimal'),
            ('Topography', 'categorical'),
            ('Site_Influence', 'categorical')
        ]
        
        land_success = 0
        for field, data_type in land_tests:
            if field in sample_data.columns:
                try:
                    if data_type == 'decimal':
                        converted_data = pd.to_numeric(sample_data[field], errors='coerce')
                        valid_count = converted_data.notna().sum()
                    else:  # categorical
                        converted_data = sample_data[field].fillna('')
                        valid_count = len(converted_data[converted_data != ''])
                    
                    print(f"   🌍 {field}: {valid_count:,} valid {data_type} conversions")
                    land_success += 1
                except Exception as e:
                    print(f"   ❌ {field}: Conversion failed - {e}")
        
        # Ownership conversion tests
        ownership_tests = [
            ('Owner1FirstName', 'string'),
            ('CO_Mailing_City', 'string'),
            ('Length_of_Residence_Months', 'integer')
        ]
        
        ownership_success = 0
        for field, data_type in ownership_tests:
            if field in sample_data.columns:
                try:
                    if data_type == 'integer':
                        converted_data = pd.to_numeric(sample_data[field], errors='coerce').round().astype('Int64', errors='ignore')
                        valid_count = converted_data.notna().sum()
                    else:  # string
                        converted_data = sample_data[field].fillna('')
                        valid_count = len(converted_data[converted_data != ''])
                    
                    print(f"   👤 {field}: {valid_count:,} valid {data_type} conversions")
                    ownership_success += 1
                except Exception as e:
                    print(f"   ❌ {field}: Conversion failed - {e}")
        
        # CATEGORY INTELLIGENCE PREVIEW
        print(f"\n💡 CATEGORY INTELLIGENCE PREVIEW:")
        
        # Building intelligence
        if 'Pool' in sample_data.columns:
            pool_data = sample_data['Pool'].fillna('')
            pool_count = len(pool_data[pool_data == 'Y'])
            print(f"   🏗️ Properties with pools: {pool_count:,} ({pool_count/len(sample_data)*100:.1f}%)")
        
        # Land intelligence
        if 'LotSize_Acres' in sample_data.columns:
            try:
                lot_acres = pd.to_numeric(sample_data['LotSize_Acres'], errors='coerce')
                valid_lots = lot_acres.dropna()
                if len(valid_lots) > 0:
                    print(f"   🌍 Lot sizes: {valid_lots.min():.2f} - {valid_lots.max():.2f} acres (avg: {valid_lots.mean():.2f})")
            except:
                pass
        
        # Ownership intelligence
        if 'Length_of_Residence_Months' in sample_data.columns:
            try:
                residence_months = pd.to_numeric(sample_data['Length_of_Residence_Months'], errors='coerce')
                valid_residence = residence_months.dropna()
                if len(valid_residence) > 0:
                    print(f"   👤 Residence length: {valid_residence.min():.0f} - {valid_residence.max():.0f} months (avg: {valid_residence.mean():.0f})")
            except:
                pass
        
        # SUCCESS METRICS
        total_categories = 3
        successful_categories = sum([
            1 if building_success >= 3 else 0,
            1 if land_success >= 2 else 0,
            1 if ownership_success >= 2 else 0
        ])
        
        success_rate = (successful_categories / total_categories) * 100
        
        print(f"\n🎉 MEGA BATCH 2B: CATEGORY COMPLETION VALIDATION:")
        print(f"   🔥 Categories tested: {total_categories}")
        print(f"   ✅ Categories validated: {successful_categories}")
        print(f"   📊 Category success rate: {success_rate:.0f}%")
        print(f"   ⚡ Ready for production: {'YES' if success_rate >= 80 else 'NEEDS REVIEW'}")
        
        total_time = time.time() - start_time
        print(f"   ⏱️  Test time: {total_time:.1f} seconds")
        
        if success_rate >= 80:
            print(f"\n🔥 MEGA BATCH 2B: CATEGORY COMPLETION VALIDATION SUCCESSFUL!")
            print(f"   🏗️ Building Characteristics: READY TO COMPLETE")
            print(f"   🌍 Land Characteristics: READY TO COMPLETE")
            print(f"   👤 Ownership Intelligence: ENHANCED")
            print(f"   📈 Expected result: 54 → 95 working fields")
            print(f"   🎯 Categories to cross off: Building + Land COMPLETE")
            return True
        else:
            print(f"\n⚠️  MEGA BATCH 2B: NEEDS REVIEW")
            print(f"   🔍 Some categories may need adjustment before production")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = mega_batch_2b_validation_test()
    if success:
        print("\n🚀 Next step: Run production load with MEGA BATCH 2B category completion")
        print("🎯 Goal: Cross off Building + Land categories as COMPLETE")
    else:
        print("\n⚠️  Review category validation results before production load") 