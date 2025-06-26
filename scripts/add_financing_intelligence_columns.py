#!/usr/bin/env python3
"""
Add Financing Intelligence Database Columns - Phase 2A
STRATEGY: Mortgage & lending data for loan management platform capabilities
GOAL: Add 12-15 high-value financing fields for comprehensive loan intelligence
"""

import psycopg2
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import get_db_config

def add_financing_intelligence_columns():
    """Add missing columns for financing/mortgage intelligence fields"""
    
    print("🏦 PHASE 2A: FINANCING INTELLIGENCE DATABASE EXPANSION")
    print("=" * 65)
    
    # Define the columns we need - FINANCING INTELLIGENCE CATEGORY
    columns_to_add = [
        # PRIMARY MORTGAGE (MTG01) - Core lending intelligence
        ("mtg01_lender_name", "VARCHAR(40)", "Primary mortgage lender name"),
        ("mtg01_loan_amount", "DECIMAL(12,2)", "Primary mortgage loan amount"),
        ("mtg01_interest_rate", "DECIMAL(7,5)", "Primary mortgage interest rate"),
        ("mtg01_recording_date", "DATE", "Primary mortgage recording date"),
        ("mtg01_due_date", "DATE", "Primary mortgage due date"),
        ("mtg01_loan_type", "VARCHAR(1)", "Primary mortgage loan type code"),
        ("mtg01_type_financing", "VARCHAR(4)", "Primary mortgage financing type"),
        
        # SECONDARY MORTGAGE (MTG02) - Enhanced lending intelligence  
        ("mtg02_lender_name", "VARCHAR(40)", "Secondary mortgage lender name"),
        ("mtg02_loan_amount", "DECIMAL(12,2)", "Secondary mortgage loan amount"),
        ("mtg02_interest_rate", "DECIMAL(7,5)", "Secondary mortgage interest rate"),
        ("mtg02_recording_date", "DATE", "Secondary mortgage recording date"),
        
        # LENDING SUMMARY INTELLIGENCE (High business value)
        ("total_open_lien_count", "INTEGER", "Total number of open liens"),
        ("total_open_lien_balance", "DECIMAL(15,2)", "Total open lien balance"),
        ("current_est_ltv_combined", "DECIMAL(7,4)", "Current estimated LTV ratio"),
        ("current_est_equity_dollars", "DECIMAL(15,2)", "Current estimated equity amount"),
    ]
    
    try:
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        
        print("💰 FINANCING INTELLIGENCE ANALYSIS:")
        print(f"   • Primary Mortgage Fields: 7 (core lending data)")
        print(f"   • Secondary Mortgage Fields: 4 (additional financing)")
        print(f"   • Lending Summary Fields: 4 (portfolio analysis)")
        print(f"   • TOTAL TARGET: {len(columns_to_add)} new financing fields")
        print()
        
        success_count = 0
        for column_name, data_type, description in columns_to_add:
            try:
                sql = f"ALTER TABLE properties ADD COLUMN IF NOT EXISTS {column_name} {data_type};"
                cursor.execute(sql)
                conn.commit()
                print(f"✅ Added: {column_name} ({data_type}) - {description}")
                success_count += 1
            except Exception as e:
                print(f"❌ Failed: {column_name} - {str(e)}")
        
        print()
        print("🏦 FINANCING INTELLIGENCE RESULTS:")
        print(f"   ✅ Successfully added: {success_count}/{len(columns_to_add)} columns")
        print(f"   💰 Lending intelligence: PRIMARY + SECONDARY mortgage data")
        print(f"   📊 Portfolio analysis: LTV, equity, lien summary data")
        print(f"   🚀 Ready for Phase 2A field mapping test")
        
        # Verify final column count
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'properties' AND table_schema = 'datnest'
        """)
        total_columns = cursor.fetchone()[0]
        print(f"   📊 Total database columns: {total_columns}")
        
        cursor.close()
        conn.close()
        
        if success_count == len(columns_to_add):
            print()
            print("🔥 PHASE 2A: FINANCING INTELLIGENCE READY!")
            print("   🎯 Next: Add field mappings to bulletproof_production_loader.py")
            print("   💰 Business Value: Loan management, mortgage analysis, lending decisions")
            return True
        else:
            print()
            print("⚠️  PARTIAL SUCCESS: Some columns may need manual review")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False

if __name__ == "__main__":
    success = add_financing_intelligence_columns()
    if success:
        print("\n🚀 Next step: Update field mappings for Phase 2A validation")
    else:
        print("\n⚠️  Review any failed columns before proceeding") 