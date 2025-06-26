#!/usr/bin/env python3
"""
Add customer priority fields to properties table
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from config import get_db_config

def add_customer_priority_fields():
    print('🚀 Adding Customer Priority Fields to Properties Table')
    print('====================================================')
    
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print('✅ Database connection successful')
        print('📝 Adding customer priority fields...')
        
        # Add fields in groups to make it easier to troubleshoot
        
        # Group 1: Mortgage/Lien Information
        print('\n🏦 Adding mortgage/lien fields...')
        mortgage_fields = [
            "ALTER TABLE datnest.properties ADD COLUMN first_mtg_date DATE;",
            "ALTER TABLE datnest.properties ADD COLUMN first_mtg_amount DECIMAL(12,2);",
            "ALTER TABLE datnest.properties ADD COLUMN first_mtg_rate DECIMAL(6,4);",
            "ALTER TABLE datnest.properties ADD COLUMN first_mtg_lender_name VARCHAR(200);",
            "ALTER TABLE datnest.properties ADD COLUMN first_mtg_bal DECIMAL(12,2);",
            "ALTER TABLE datnest.properties ADD COLUMN second_mtg_date DATE;",
            "ALTER TABLE datnest.properties ADD COLUMN second_mtg_amount DECIMAL(12,2);",
            "ALTER TABLE datnest.properties ADD COLUMN second_mtg_rate DECIMAL(6,4);",
            "ALTER TABLE datnest.properties ADD COLUMN second_mtg_lender_name VARCHAR(200);",
            "ALTER TABLE datnest.properties ADD COLUMN second_mtg_bal DECIMAL(12,2);"
        ]
        
        for sql in mortgage_fields:
            cursor.execute(sql)
            print(f"  ✅ {sql.split('ADD COLUMN')[1].split()[0]}")
        
        # Group 2: Property Classification
        print('\n🏷️  Adding property classification fields...')
        classification_fields = [
            "ALTER TABLE datnest.properties ADD COLUMN property_land_use_standardized_code VARCHAR(10);",
            "ALTER TABLE datnest.properties ADD COLUMN property_land_use_description VARCHAR(200);",
            "ALTER TABLE datnest.properties ADD COLUMN property_type VARCHAR(100);",
            "ALTER TABLE datnest.properties ADD COLUMN property_use_general VARCHAR(100);",
            "ALTER TABLE datnest.properties ADD COLUMN property_subtype VARCHAR(100);"
        ]
        
        for sql in classification_fields:
            cursor.execute(sql)
            print(f"  ✅ {sql.split('ADD COLUMN')[1].split()[0]}")
        
        # Group 3: Sales Intelligence
        print('\n💰 Adding sales intelligence fields...')
        sales_fields = [
            "ALTER TABLE datnest.properties ADD COLUMN last_sale_date DATE;",
            "ALTER TABLE datnest.properties ADD COLUMN last_sale_price DECIMAL(12,2);",
            "ALTER TABLE datnest.properties ADD COLUMN last_sale_recording_date DATE;",
            "ALTER TABLE datnest.properties ADD COLUMN prior_sale_date DATE;",
            "ALTER TABLE datnest.properties ADD COLUMN prior_sale_price DECIMAL(12,2);",
            "ALTER TABLE datnest.properties ADD COLUMN sales_history_count INTEGER DEFAULT 0;"
        ]
        
        for sql in sales_fields:
            cursor.execute(sql)
            print(f"  ✅ {sql.split('ADD COLUMN')[1].split()[0]}")
        
        # Group 4: Enhanced Property Details
        print('\n🏠 Adding enhanced property detail fields...')
        detail_fields = [
            "ALTER TABLE datnest.properties ADD COLUMN stories_number DECIMAL(3,1);",
            "ALTER TABLE datnest.properties ADD COLUMN garage_spaces INTEGER;",
            "ALTER TABLE datnest.properties ADD COLUMN fireplace_count INTEGER;",
            "ALTER TABLE datnest.properties ADD COLUMN pool_flag BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE datnest.properties ADD COLUMN air_conditioning_flag BOOLEAN DEFAULT FALSE;"
        ]
        
        for sql in detail_fields:
            cursor.execute(sql)
            print(f"  ✅ {sql.split('ADD COLUMN')[1].split()[0]}")
        
        # Commit all changes
        conn.commit()
        
        # Verify field count
        cursor.execute("""SELECT COUNT(*) FROM information_schema.columns 
                         WHERE table_schema='datnest' AND table_name='properties'""")
        new_field_count = cursor.fetchone()[0]
        
        print(f'\n📊 Properties table now has {new_field_count} fields (+{new_field_count-26} added)')
        print('🎉 Customer priority fields added successfully!')
        
        conn.close()
        return True
        
    except Exception as e:
        print(f'❌ Failed to add fields: {e}')
        return False

if __name__ == "__main__":
    add_customer_priority_fields() 