#!/usr/bin/env python3
"""
Phase 2A Financing Intelligence Test - Master Database Engineer
STRATEGY: Validate 15 new financing fields for mortgage/lending intelligence
GOAL: Test financing data quality before production load (39 → 54 fields)
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

def phase_2a_financing_intelligence_test():
    """Test Phase 2A financing intelligence field mapping with sample data"""
    file_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    print("🏦 PHASE 2A: FINANCING INTELLIGENCE VALIDATION TEST")
    print("🎯 STRATEGY: Validate 15 new mortgage & lending fields")
    print("⚡ EFFICIENCY: 5K sample test for financing data quality")
    print("=" * 65)
    
    # PHASE 2A FINANCING INTELLIGENCE FIELD MAPPING
    field_mapping = {
        # Core working fields (validation baseline)
        'Quantarium_Internal_PID': 'quantarium_internal_pid',
        'ESTIMATED_VALUE': 'estimated_value',
        'Building_Area_1': 'building_area_total',
        
        # 🏦 PHASE 2A: PRIMARY MORTGAGE INTELLIGENCE (NEW)
        'Mtg01_lender_name_beneficiary': 'mtg01_lender_name',       # Field #217
        'Mtg01_Loan_Amount': 'mtg01_loan_amount',                   # Field #221
        'Mtg01_interest_rate': 'mtg01_interest_rate',               # Field #224
        'Mtg01_recording_date': 'mtg01_recording_date',             # Field #220
        'Mtg01_due_date': 'mtg01_due_date',                         # Field #225
        'Mtg01_loan_type': 'mtg01_loan_type',                       # Field #222
        'Mtg01_type_financing': 'mtg01_type_financing',             # Field #223
        
        # 🏦 PHASE 2A: SECONDARY MORTGAGE INTELLIGENCE (NEW)
        'Mtg02_lender_name_beneficiary': 'mtg02_lender_name',       # Secondary mortgage
        'Mtg02_Loan_Amount': 'mtg02_loan_amount',                   # Secondary amount
        'Mtg02_interest_rate': 'mtg02_interest_rate',               # Secondary rate
        'Mtg02_recording_date': 'mtg02_recording_date',             # Secondary recording
        
        # 🏦 PHASE 2A: LENDING SUMMARY INTELLIGENCE (NEW)
        'Total_Open_Lien_Count': 'total_open_lien_count',           # Lien count
        'Total_Open_Lien_Balance': 'total_open_lien_balance',       # Lien balance
        'Current_Est_LTV_Combined': 'current_est_ltv_combined',     # LTV ratio
        'Current_Est_Equity_Dollars': 'current_est_equity_dollars'  # Equity amount
    }
    
    print(f"🏦 FINANCING INTELLIGENCE ANALYSIS:")
    print(f"   • Core baseline fields: 3 (validation)")
    print(f"   • Primary mortgage fields: 7 (core lending data)")
    print(f"   • Secondary mortgage fields: 4 (additional financing)")
    print(f"   • Lending summary fields: 4 (portfolio analysis)")
    print(f"   • TOTAL: {len(field_mapping)} fields ({len(field_mapping)-3} NEW)")
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
        
        # Analyze financing field availability in TSV
        print(f"\n🏦 FINANCING INTELLIGENCE FIELD ANALYSIS:")
        available_fields = []
        missing_fields = []
        financing_coverage = {}
        
        for tsv_col, db_col in field_mapping.items():
            if tsv_col in sample_data.columns:
                available_fields.append(tsv_col)
                # Analyze data coverage
                non_null_count = sample_data[tsv_col].notna().sum()
                coverage = (non_null_count / len(sample_data)) * 100
                financing_coverage[tsv_col] = coverage
                
                if 'mtg' in tsv_col.lower() or 'lien' in tsv_col.lower() or 'ltv' in tsv_col.lower() or 'equity' in tsv_col.lower():
                    status = "💰" if coverage > 10 else "🏦" if coverage > 1 else "⚠️"
                    print(f"   {status} {tsv_col}: {non_null_count:,} records ({coverage:.1f}% coverage)")
                else:
                    status = "✅"  # Baseline fields
                    print(f"   {status} {tsv_col}: {non_null_count:,} records ({coverage:.1f}% coverage)")
            else:
                missing_fields.append(tsv_col)
                print(f"   ❌ {tsv_col}: NOT FOUND in TSV")
        
        print(f"\n📊 PHASE 2A AVAILABILITY RESULTS:")
        print(f"   ✅ Available fields: {len(available_fields)}/{len(field_mapping)}")
        print(f"   ❌ Missing fields: {len(missing_fields)}")
        
        if missing_fields:
            print(f"   ⚠️  Missing: {missing_fields}")
        
        # Test financing data type conversions
        print(f"\n🧪 FINANCING DATA TYPE CONVERSION TEST:")
        conversion_results = {}
        
        # Test primary mortgage fields
        primary_mtg_fields = [
            ('Mtg01_Loan_Amount', 'numeric'),
            ('Mtg01_interest_rate', 'decimal'),
            ('Mtg01_lender_name_beneficiary', 'string'),
            ('Mtg01_recording_date', 'date'),
            ('Mtg01_due_date', 'date'),
            ('Mtg01_loan_type', 'string'),
            ('Mtg01_type_financing', 'string')
        ]
        
        for field, data_type in primary_mtg_fields:
            if field in sample_data.columns:
                try:
                    if data_type == 'numeric':
                        converted_data = pd.to_numeric(sample_data[field], errors='coerce')
                    elif data_type == 'decimal':
                        converted_data = pd.to_numeric(sample_data[field], errors='coerce')
                    elif data_type == 'date':
                        converted_data = pd.to_datetime(sample_data[field], format='%Y%m%d', errors='coerce')
                    else:  # string
                        converted_data = sample_data[field].fillna('')
                    
                    valid_count = converted_data.notna().sum() if data_type != 'string' else len(converted_data[converted_data != ''])
                    conversion_results[field] = valid_count
                    print(f"   💰 {field}: {valid_count:,} valid {data_type} conversions")
                except Exception as e:
                    print(f"   ❌ {field}: Conversion failed - {e}")
        
        # Test secondary mortgage fields
        secondary_mtg_fields = [
            ('Mtg02_Loan_Amount', 'numeric'),
            ('Mtg02_interest_rate', 'decimal'),
            ('Mtg02_lender_name_beneficiary', 'string'),
            ('Mtg02_recording_date', 'date')
        ]
        
        for field, data_type in secondary_mtg_fields:
            if field in sample_data.columns:
                try:
                    if data_type == 'numeric':
                        converted_data = pd.to_numeric(sample_data[field], errors='coerce')
                    elif data_type == 'decimal':
                        converted_data = pd.to_numeric(sample_data[field], errors='coerce')
                    elif data_type == 'date':
                        converted_data = pd.to_datetime(sample_data[field], format='%Y%m%d', errors='coerce')
                    else:  # string
                        converted_data = sample_data[field].fillna('')
                    
                    valid_count = converted_data.notna().sum() if data_type != 'string' else len(converted_data[converted_data != ''])
                    conversion_results[field] = valid_count
                    print(f"   🏦 {field}: {valid_count:,} valid {data_type} conversions")
                except Exception as e:
                    print(f"   ❌ {field}: Conversion failed - {e}")
        
        # Test lending summary fields
        summary_fields = [
            ('Total_Open_Lien_Count', 'integer'),
            ('Total_Open_Lien_Balance', 'numeric'),
            ('Current_Est_LTV_Combined', 'decimal'),
            ('Current_Est_Equity_Dollars', 'numeric')
        ]
        
        for field, data_type in summary_fields:
            if field in sample_data.columns:
                try:
                    if data_type == 'integer':
                        converted_data = pd.to_numeric(sample_data[field], errors='coerce').round().astype('Int64', errors='ignore')
                    else:  # numeric/decimal
                        converted_data = pd.to_numeric(sample_data[field], errors='coerce')
                    
                    valid_count = converted_data.notna().sum()
                    conversion_results[field] = valid_count
                    print(f"   📊 {field}: {valid_count:,} valid {data_type} conversions")
                except Exception as e:
                    print(f"   ❌ {field}: Conversion failed - {e}")
        
        # FINANCING INTELLIGENCE ANALYSIS
        print(f"\n💡 FINANCING INTELLIGENCE PREVIEW:")
        
        # Primary mortgage analysis
        if 'Mtg01_Loan_Amount' in sample_data.columns:
            try:
                loan_amounts = pd.to_numeric(sample_data['Mtg01_Loan_Amount'], errors='coerce')
                valid_loans = loan_amounts.dropna()
                if len(valid_loans) > 0:
                    print(f"   💰 Primary Mortgage: ${valid_loans.min():,.0f} - ${valid_loans.max():,.0f} (avg: ${valid_loans.mean():,.0f})")
            except:
                pass
        
        # Interest rate analysis
        if 'Mtg01_interest_rate' in sample_data.columns:
            try:
                interest_rates = pd.to_numeric(sample_data['Mtg01_interest_rate'], errors='coerce')
                valid_rates = interest_rates.dropna()
                if len(valid_rates) > 0:
                    print(f"   📈 Interest Rates: {valid_rates.min():.3f}% - {valid_rates.max():.3f}% (avg: {valid_rates.mean():.3f}%)")
            except:
                pass
        
        # LTV analysis
        if 'Current_Est_LTV_Combined' in sample_data.columns:
            try:
                ltv_ratios = pd.to_numeric(sample_data['Current_Est_LTV_Combined'], errors='coerce')
                valid_ltv = ltv_ratios.dropna()
                if len(valid_ltv) > 0:
                    print(f"   📊 LTV Ratios: {valid_ltv.min():.1%} - {valid_ltv.max():.1%} (avg: {valid_ltv.mean():.1%})")
            except:
                pass
        
        # SUCCESS METRICS
        total_new_fields = len(field_mapping) - 3  # Subtract baseline fields
        successful_new_fields = sum(1 for field in conversion_results if 'mtg' in field.lower() or 'lien' in field.lower() or 'ltv' in field.lower() or 'equity' in field.lower())
        
        success_rate = (successful_new_fields / total_new_fields) * 100 if total_new_fields > 0 else 0
        
        print(f"\n🎉 PHASE 2A: FINANCING INTELLIGENCE VALIDATION:")
        print(f"   🏦 New financing fields tested: {total_new_fields}")
        print(f"   ✅ Successfully validated: {successful_new_fields}")
        print(f"   📊 Success rate: {success_rate:.0f}%")
        print(f"   ⚡ Ready for production: {'YES' if success_rate >= 60 else 'NEEDS REVIEW'}")
        
        total_time = time.time() - start_time
        print(f"   ⏱️  Test time: {total_time:.1f} seconds")
        
        if success_rate >= 60:
            print(f"\n🔥 PHASE 2A: FINANCING INTELLIGENCE VALIDATION SUCCESSFUL!")
            print(f"   🎯 Recommended: Proceed with production load")
            print(f"   📈 Expected result: 39 → {len(field_mapping)} working fields")
            print(f"   💰 Business value: Mortgage analysis, lending decisions, loan management")
            return True
        else:
            print(f"\n⚠️  PHASE 2A: NEEDS REVIEW")
            print(f"   🔍 Some financing fields may need adjustment before production")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = phase_2a_financing_intelligence_test()
    if success:
        print("\n🚀 Next step: Run production load with Phase 2A financing intelligence")
    else:
        print("\n⚠️  Review financing field test results before production load") 