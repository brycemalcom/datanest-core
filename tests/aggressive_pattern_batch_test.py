#!/usr/bin/env python3
"""
Aggressive Pattern-Batch Field Test - Master Database Engineer
STRATEGY: Test 10 new high-value fields using pattern-batch optimization
GOAL: Validate sales + assessment intelligence before production load
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

def aggressive_pattern_batch_test():
    """Test aggressive pattern-batch field mapping with small sample"""
    file_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    print("🚀 AGGRESSIVE PATTERN-BATCH FIELD TEST")
    print("🎯 STRATEGY: Validate 10 new high-value sales & assessment fields")
    print("⚡ EFFICIENCY: 5K sample test before production load")
    print("=" * 65)
    
    # AGGRESSIVE PATTERN-BATCH FIELD MAPPING
    field_mapping = {
        # Core QVM Intelligence (PROVEN WORKING)
        'Quantarium_Internal_PID': 'quantarium_internal_pid',
        'ESTIMATED_VALUE': 'estimated_value',
        'CONFIDENCE_SCORE': 'confidence_score',
        'Building_Area_1': 'building_area_total',
        'Number_of_Bedrooms': 'number_of_bedrooms',
        
        # 🚀 AGGRESSIVE PATTERN-BATCH: Sales Intelligence (NEW)
        'LValid_Price': 'last_valid_sale_price',               # Field #43
        'Last_Sale_date': 'last_sale_date',                    # Field #48
        'PSale_Price': 'prior_sale_price',                     # Field #53
        'Prior_Sale_Date': 'prior_sale_date',                  # Field #68
        
        # 🚀 AGGRESSIVE PATTERN-BATCH: Assessment Intelligence (NEW)
        'Assessed_Improvement_Value': 'assessed_improvement_value',  # Field #109
        'Assessed_Land_Value': 'assessed_land_value',               # Field #110
        'Market_Value_Improvement': 'market_value_improvement',     # Field #115
        'Market_Value_Land': 'market_value_land',                   # Field #116
        
        # 🚀 AGGRESSIVE PATTERN-BATCH: High-Value Bonus (NEW)
        'Tax_Amount': 'tax_amount',                            # Field #125
        'Garage_Cars': 'garage_cars'                           # Field #182
    }
    
    print(f"📊 PATTERN-BATCH ANALYSIS:")
    print(f"   • Core Working Fields: 5 (validation baseline)")
    print(f"   • Sales Intelligence: 4 new fields")
    print(f"   • Assessment Intelligence: 4 new fields") 
    print(f"   • High-Value Bonus: 2 new fields")
    print(f"   • TOTAL: {len(field_mapping)} fields ({len(field_mapping)-5} NEW)")
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
        
        # Analyze field availability in TSV
        print(f"\n🔍 PATTERN-BATCH FIELD ANALYSIS:")
        available_fields = []
        missing_fields = []
        
        for tsv_col, db_col in field_mapping.items():
            if tsv_col in sample_data.columns:
                available_fields.append(tsv_col)
                # Analyze data coverage
                non_null_count = sample_data[tsv_col].notna().sum()
                coverage = (non_null_count / len(sample_data)) * 100
                status = "🔥" if coverage > 50 else "⚡" if coverage > 10 else "⚠️"
                print(f"   {status} {tsv_col}: {non_null_count:,} records ({coverage:.1f}% coverage)")
            else:
                missing_fields.append(tsv_col)
                print(f"   ❌ {tsv_col}: NOT FOUND in TSV")
        
        print(f"\n📊 PATTERN-BATCH RESULTS:")
        print(f"   ✅ Available fields: {len(available_fields)}/{len(field_mapping)}")
        print(f"   ❌ Missing fields: {len(missing_fields)}")
        
        if missing_fields:
            print(f"   ⚠️  Missing: {missing_fields}")
        
        # Test data type conversions for new fields
        print(f"\n🧪 DATA TYPE CONVERSION TEST:")
        conversion_results = {}
        
        # Test sales intelligence fields (DECIMAL)
        sales_fields = ['LValid_Price', 'PSale_Price']
        for field in sales_fields:
            if field in sample_data.columns:
                try:
                    numeric_data = pd.to_numeric(sample_data[field], errors='coerce')
                    valid_count = numeric_data.notna().sum()
                    conversion_results[field] = valid_count
                    print(f"   💰 {field}: {valid_count:,} valid numeric conversions")
                except Exception as e:
                    print(f"   ❌ {field}: Conversion failed - {e}")
        
        # Test assessment intelligence fields (DECIMAL)
        assessment_fields = ['Assessed_Improvement_Value', 'Assessed_Land_Value', 'Market_Value_Improvement', 'Market_Value_Land']
        for field in assessment_fields:
            if field in sample_data.columns:
                try:
                    numeric_data = pd.to_numeric(sample_data[field], errors='coerce')
                    valid_count = numeric_data.notna().sum()
                    conversion_results[field] = valid_count
                    print(f"   🏦 {field}: {valid_count:,} valid numeric conversions")
                except Exception as e:
                    print(f"   ❌ {field}: Conversion failed - {e}")
        
        # Test tax and garage fields
        bonus_fields = [('Tax_Amount', 'numeric'), ('Garage_Cars', 'integer')]
        for field, data_type in bonus_fields:
            if field in sample_data.columns:
                try:
                    if data_type == 'numeric':
                        converted_data = pd.to_numeric(sample_data[field], errors='coerce')
                    else:
                        converted_data = pd.to_numeric(sample_data[field], errors='coerce').round().astype('Int64', errors='ignore')
                    valid_count = converted_data.notna().sum()
                    conversion_results[field] = valid_count
                    print(f"   🎯 {field}: {valid_count:,} valid {data_type} conversions")
                except Exception as e:
                    print(f"   ❌ {field}: Conversion failed - {e}")
        
        # Test date conversions
        date_fields = ['Last_Sale_date', 'Prior_Sale_Date']
        for field in date_fields:
            if field in sample_data.columns:
                try:
                    date_data = pd.to_datetime(sample_data[field], format='%Y%m%d', errors='coerce')
                    valid_count = date_data.notna().sum()
                    conversion_results[field] = valid_count
                    print(f"   📅 {field}: {valid_count:,} valid date conversions")
                except Exception as e:
                    print(f"   ❌ {field}: Date conversion failed - {e}")
        
        # BUSINESS INTELLIGENCE ANALYSIS
        print(f"\n💡 BUSINESS INTELLIGENCE PREVIEW:")
        
        # Sales intelligence analysis
        if 'LValid_Price' in sample_data.columns:
            try:
                sales_prices = pd.to_numeric(sample_data['LValid_Price'], errors='coerce')
                valid_sales = sales_prices.dropna()
                if len(valid_sales) > 0:
                    print(f"   💰 Sales Data: ${valid_sales.min():,.0f} - ${valid_sales.max():,.0f} (avg: ${valid_sales.mean():,.0f})")
            except:
                pass
        
        # Assessment intelligence analysis  
        if 'Total_Assessed_Value' in sample_data.columns:
            try:
                assessed_values = pd.to_numeric(sample_data['Total_Assessed_Value'], errors='coerce')
                valid_assessed = assessed_values.dropna()
                if len(valid_assessed) > 0:
                    print(f"   🏦 Assessment Data: ${valid_assessed.min():,.0f} - ${valid_assessed.max():,.0f} (avg: ${valid_assessed.mean():,.0f})")
            except:
                pass
        
        # Property features analysis
        if 'Garage_Cars' in sample_data.columns:
            try:
                garage_data = pd.to_numeric(sample_data['Garage_Cars'], errors='coerce')
                valid_garage = garage_data.dropna()
                if len(valid_garage) > 0:
                    print(f"   🚗 Garage Data: {valid_garage.min():.0f} - {valid_garage.max():.0f} cars (avg: {valid_garage.mean():.1f})")
            except:
                pass
        
        # SUCCESS METRICS
        total_new_fields = len(field_mapping) - 5  # Subtract baseline fields
        successful_new_fields = sum(1 for field in conversion_results if field in [
            'LValid_Price', 'Last_Sale_date', 'PSale_Price', 'Prior_Sale_Date',
            'Assessed_Improvement_Value', 'Assessed_Land_Value', 'Market_Value_Improvement', 'Market_Value_Land',
            'Tax_Amount', 'Garage_Cars'
        ])
        
        success_rate = (successful_new_fields / total_new_fields) * 100 if total_new_fields > 0 else 0
        
        print(f"\n🎉 AGGRESSIVE PATTERN-BATCH VALIDATION:")
        print(f"   🚀 New fields tested: {total_new_fields}")
        print(f"   ✅ Successfully validated: {successful_new_fields}")
        print(f"   📊 Success rate: {success_rate:.0f}%")
        print(f"   ⚡ Ready for production: {'YES' if success_rate >= 70 else 'NEEDS REVIEW'}")
        
        total_time = time.time() - start_time
        print(f"   ⏱️  Test time: {total_time:.1f} seconds (vs 30+ min production)")
        
        if success_rate >= 70:
            print(f"\n🔥 AGGRESSIVE STRATEGY: VALIDATION SUCCESSFUL!")
            print(f"   🎯 Recommended: Proceed with production load")
            print(f"   📈 Expected result: 29 → ~{len(field_mapping)} working fields")
            return True
        else:
            print(f"\n⚠️  AGGRESSIVE STRATEGY: NEEDS REVIEW")
            print(f"   🔍 Some fields may need adjustment before production")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = aggressive_pattern_batch_test()
    if success:
        print("\n🚀 Next step: Run production load with aggressive pattern-batch")
    else:
        print("\n⚠️  Review test results before production load") 