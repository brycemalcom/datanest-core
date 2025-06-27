#!/usr/bin/env python3
"""
Add intelligent land use codes lookup table
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from config import get_db_config

def create_land_use_codes_table():
    print('🚀 Creating Intelligent Land Use Codes System')
    print('=============================================')
    
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print('✅ Database connection successful')
        
        # Create land use codes lookup table
        print('\n📋 Creating land use codes lookup table...')
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
        print('  ✅ Land use codes table created')
        
        # Add key land use codes (sample set for testing)
        print('\n🏷️  Populating key land use codes...')
        key_codes = [
            # Residential
            ('1000', 'Residential (General) (Single)', 'Residential', True, False, False, False, False, False),
            ('1001', 'Single Family Residential', 'Residential', True, False, False, False, False, False),
            ('1002', 'Townhouse (Residential)', 'Residential', True, False, False, False, False, False),
            ('1004', 'Condominium Unit (Residential)', 'Residential', True, False, False, False, False, False),
            ('1100', 'Residential Income (General) (Multi-Family)', 'Residential', True, False, False, False, False, False),
            ('1101', 'Duplex (2 units, any combination)', 'Residential', True, False, False, False, False, False),
            
            # Commercial
            ('2000', 'Commercial (General)', 'Commercial', False, True, False, False, False, False),
            ('2001', 'Retail Stores ( Personal Services, Photography, Travel)', 'Commercial', False, True, False, False, False, False),
            ('2006', 'Grocery, Supermarket', 'Commercial', False, True, False, False, False, False),
            ('2012', 'Restaurant', 'Commercial', False, True, False, False, False, False),
            ('2034', 'Hotel', 'Commercial', False, True, False, False, False, False),
            ('3000', 'Commercial Office (General)', 'Commercial', False, True, False, False, False, False),
            
            # Industrial
            ('5000', 'Industrial (General)', 'Industrial', False, False, True, False, False, False),
            ('5001', 'Manufacturing (light)', 'Industrial', False, False, True, False, False, False),
            ('5003', 'Warehouse (Industrial)', 'Industrial', False, False, True, False, False, False),
            ('6000', 'Heavy Industrial (General)', 'Industrial', False, False, True, False, False, False),
            
            # Agricultural
            ('7000', 'Agricultural / Rural (General)', 'Agricultural', False, False, False, True, False, False),
            ('7001', 'Farm (Irrigated or Dry)', 'Agricultural', False, False, False, True, False, False),
            ('7002', 'Ranch', 'Agricultural', False, False, False, True, False, False),
            
            # Vacant Land
            ('8000', 'Vacant Land (General)', 'Vacant', False, False, False, False, True, False),
            ('8001', 'Residential-Vacant Land', 'Vacant', False, False, False, False, True, False),
            ('8002', 'Commercial-Vacant Land', 'Vacant', False, False, False, False, True, False),
            
            # Exempt
            ('9000', 'Exempt (full or partial)', 'Exempt', False, False, False, False, False, True),
            ('9100', 'Institutional (General)', 'Exempt', False, False, False, False, False, True),
            ('9200', 'Governmental/Public Use (General)', 'Exempt', False, False, False, False, False, True),
        ]
        
        insert_sql = """
        INSERT INTO datnest.land_use_codes 
        (code, description, category, is_residential, is_commercial, is_industrial, is_agricultural, is_vacant, is_exempt) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (code) DO NOTHING
        """
        
        cursor.executemany(insert_sql, key_codes)
        print(f'  ✅ {len(key_codes)} key land use codes added')
        
        # Create auto-decoding trigger function
        print('\n🤖 Creating intelligent land use decoding trigger...')
        trigger_function_sql = """
        CREATE OR REPLACE FUNCTION datnest.update_land_use_description()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.property_land_use_standardized_code IS NOT NULL THEN
                -- Update description from lookup table
                SELECT description INTO NEW.property_land_use_description
                FROM datnest.land_use_codes 
                WHERE code = NEW.property_land_use_standardized_code;
                
                -- If no match found, set to 'Unknown Code: XXXX'
                IF NEW.property_land_use_description IS NULL THEN
                    NEW.property_land_use_description := 'Unknown Code: ' || NEW.property_land_use_standardized_code;
                END IF;
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        cursor.execute(trigger_function_sql)
        print('  ✅ Auto-decoding function created')
        
        # Create trigger
        trigger_sql = """
        DROP TRIGGER IF EXISTS update_properties_land_use_description ON datnest.properties;
        CREATE TRIGGER update_properties_land_use_description
            BEFORE INSERT OR UPDATE ON datnest.properties
            FOR EACH ROW EXECUTE FUNCTION datnest.update_land_use_description();
        """
        cursor.execute(trigger_sql)
        print('  ✅ Auto-decoding trigger created')
        
        # Add foreign key constraint
        print('\n🔗 Adding foreign key constraint...')
        fk_sql = """
        ALTER TABLE datnest.properties 
        ADD CONSTRAINT fk_properties_land_use_code 
        FOREIGN KEY (property_land_use_standardized_code) 
        REFERENCES datnest.land_use_codes(code);
        """
        try:
            cursor.execute(fk_sql)
            print('  ✅ Foreign key constraint added')
        except Exception as e:
            print(f'  ⚠️  Foreign key constraint skipped (may already exist): {e}')
        
        # Create indexes for performance
        print('\n⚡ Creating performance indexes...')
        index_sqls = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_land_use_codes_category ON datnest.land_use_codes(category);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_land_use_codes_residential ON datnest.land_use_codes(is_residential) WHERE is_residential = TRUE;",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_land_use_code ON datnest.properties(property_land_use_standardized_code);",
        ]
        
        for sql in index_sqls:
            try:
                cursor.execute(sql)
                print(f'  ✅ {sql.split("idx_")[1].split()[0]}')
            except Exception as e:
                print(f'  ⚠️  Index creation skipped: {e}')
        
        # Commit all changes
        conn.commit()
        
        # Verify 
        cursor.execute("SELECT COUNT(*) FROM datnest.land_use_codes")
        code_count = cursor.fetchone()[0]
        
        print(f'\n📊 Land use codes table created with {code_count} codes')
        print('🎉 Intelligent land use code system ready!')
        print('\n🤖 Auto-decoding feature: When property_land_use_standardized_code')
        print('   is set, property_land_use_description will be auto-populated!')
        
        conn.close()
        return True
        
    except Exception as e:
        print(f'❌ Failed to create land use system: {e}')
        return False

if __name__ == "__main__":
    create_land_use_codes_table() 