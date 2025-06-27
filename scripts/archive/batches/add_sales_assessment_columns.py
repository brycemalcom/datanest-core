#!/usr/bin/env python3
"""
Add Sales & Assessment Intelligence Database Columns
AGGRESSIVE PATTERN-BATCH: 8-10 high-value fields for property intelligence
"""

import psycopg2
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import get_db_config

def add_sales_assessment_columns():
    """Add missing columns for sales and assessment intelligence fields"""
    
    print("🚀 AGGRESSIVE PATTERN-BATCH: SALES & ASSESSMENT INTELLIGENCE")
    print("=" * 65)
    
    # Define the columns we need - PATTERN-BATCHED by business value
    columns_to_add = [
        # SALES INTELLIGENCE BATCH (Core business intelligence)
        ("last_valid_sale_price", "DECIMAL(12,2)", "Last valid sale price (arms-length only)"),
        ("last_sale_date", "DATE", "Date of most recent sale"),
        ("prior_sale_price", "DECIMAL(12,2)", "Prior sale price for appreciation analysis"),
        ("prior_sale_date", "DATE", "Prior sale date"),
        
        # ASSESSMENT INTELLIGENCE BATCH (Critical appraisal data)
        ("assessed_improvement_value", "DECIMAL(12,2)", "County assessed value - improvements"),
        ("assessed_land_value", "DECIMAL(12,2)", "County assessed value - land only"),
        ("market_value_improvement", "DECIMAL(12,2)", "County market value - improvements"),
        ("market_value_land", "DECIMAL(12,2)", "County market value - land only"),
        
        # HIGH-VALUE BONUS FIELDS (Tax & property features)
        ("tax_amount", "DECIMAL(11,2)", "Annual property tax amount"),
        ("garage_cars", "INTEGER", "Number of garage parking spaces"),
    ]
    
    try:
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        
        print("📊 PATTERN-BATCH ANALYSIS:")
        print(f"   • Sales Intelligence: 4 fields (business critical)")
        print(f"   • Assessment Intelligence: 4 fields (appraisal data)")
        print(f"   • High-Value Bonus: 2 fields (tax + features)")
        print(f"   • TOTAL TARGET: {len(columns_to_add)} new fields")
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
        print("🎯 PATTERN-BATCH RESULTS:")
        print(f"   ✅ Successfully added: {success_count}/{len(columns_to_add)} columns")
        print(f"   📈 Database expansion: +{success_count} new business intelligence fields")
        print(f"   🚀 Ready for aggressive field mapping test")
        
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
            print("🔥 AGGRESSIVE STRATEGY: READY FOR PATTERN-BATCH TESTING")
            return True
        else:
            print()
            print("⚠️  PARTIAL SUCCESS: Some columns may need manual review")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False

if __name__ == "__main__":
    success = add_sales_assessment_columns()
    if success:
        print("\n🚀 Next step: Update bulletproof_production_loader.py with new field mappings")
    else:
        print("\n⚠️  Review any failed columns before proceeding") 