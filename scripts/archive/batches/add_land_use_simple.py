#!/usr/bin/env python3
"""
Simple land use codes table creation
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from config import get_db_config

def create_simple_land_use_system():
    print('🚀 Creating Simple Land Use Codes System')
    print('========================================')
    
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print('✅ Database connection successful')
        
        # Step 1: Create table
        print('\n📋 Creating land use codes table...')
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS datnest.land_use_codes (
            code VARCHAR(10) PRIMARY KEY,
            description VARCHAR(200) NOT NULL,
            category VARCHAR(50),
            is_residential BOOLEAN DEFAULT FALSE,
            is_commercial BOOLEAN DEFAULT FALSE,
            is_industrial BOOLEAN DEFAULT FALSE,
            is_agricultural BOOLEAN DEFAULT FALSE,
            is_vacant BOOLEAN DEFAULT FALSE,
            is_exempt BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_sql)
        conn.commit()
        print('  ✅ Land use codes table created')
        
        # Step 2: Add sample codes
        print('\n🏷️  Adding sample land use codes...')
        sample_codes = [
            ('1001', 'Single Family Residential', 'Residential', True, False, False, False, False, False),
            ('2000', 'Commercial (General)', 'Commercial', False, True, False, False, False, False),
            ('5000', 'Industrial (General)', 'Industrial', False, False, True, False, False, False),
            ('7000', 'Agricultural / Rural (General)', 'Agricultural', False, False, False, True, False, False),
            ('8000', 'Vacant Land (General)', 'Vacant', False, False, False, False, True, False),
            ('9000', 'Exempt (full or partial)', 'Exempt', False, False, False, False, False, True),
        ]
        
        insert_sql = """
        INSERT INTO datnest.land_use_codes 
        (code, description, category, is_residential, is_commercial, is_industrial, is_agricultural, is_vacant, is_exempt) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (code) DO NOTHING
        """
        
        cursor.executemany(insert_sql, sample_codes)
        conn.commit()
        print(f'  ✅ {len(sample_codes)} sample codes added')
        
        # Step 3: Create auto-decoding function
        print('\n🤖 Creating auto-decoding function...')
        function_sql = """
        CREATE OR REPLACE FUNCTION datnest.update_land_use_description()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.property_land_use_standardized_code IS NOT NULL THEN
                SELECT description INTO NEW.property_land_use_description
                FROM datnest.land_use_codes 
                WHERE code = NEW.property_land_use_standardized_code;
                
                IF NEW.property_land_use_description IS NULL THEN
                    NEW.property_land_use_description := 'Unknown Code: ' || NEW.property_land_use_standardized_code;
                END IF;
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        cursor.execute(function_sql)
        conn.commit()
        print('  ✅ Auto-decoding function created')
        
        # Step 4: Create trigger
        print('\n⚡ Creating auto-decoding trigger...')
        trigger_sql = """
        DROP TRIGGER IF EXISTS update_properties_land_use_description ON datnest.properties;
        CREATE TRIGGER update_properties_land_use_description
            BEFORE INSERT OR UPDATE ON datnest.properties
            FOR EACH ROW EXECUTE FUNCTION datnest.update_land_use_description();
        """
        cursor.execute(trigger_sql)
        conn.commit()
        print('  ✅ Auto-decoding trigger created')
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM datnest.land_use_codes")
        code_count = cursor.fetchone()[0]
        
        print(f'\n📊 Land use codes table has {code_count} codes')
        print('🎉 Simple land use system ready!')
        print('\n🤖 Intelligence: When property_land_use_standardized_code is set,')
        print('   property_land_use_description will be auto-populated!')
        
        conn.close()
        return True
        
    except Exception as e:
        print(f'❌ Failed: {e}')
        return False

if __name__ == "__main__":
    create_simple_land_use_system() 