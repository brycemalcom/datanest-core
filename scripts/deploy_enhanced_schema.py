#!/usr/bin/env python3
"""
DatNest Core Platform - Enhanced Schema Deployment
Deploys customer priority fields and intelligent land use code system
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def load_config():
    """Load database configuration"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'local_config.json')
    if not os.path.exists(config_path):
        print("❌ ERROR: local_config.json not found")
        return None
        
    with open(config_path, 'r') as f:
        return json.load(f)

def run_migration(config, migration_file):
    """Run a specific migration file"""
    migration_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'migrations', migration_file)
    
    if not os.path.exists(migration_path):
        print(f"❌ ERROR: Migration file {migration_file} not found")
        return False
    
    print(f"\n🔄 Running migration: {migration_file}")
    
    # Build psql command
    db_config = config['database']
    cmd = [
        'psql',
        f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}",
        '-f', migration_path,
        '-v', 'ON_ERROR_STOP=1'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ Migration {migration_file} completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ Migration {migration_file} failed")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Migration {migration_file} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running migration {migration_file}: {e}")
        return False

def verify_schema(config):
    """Verify that all new fields are present"""
    print("\n🔍 Verifying schema deployment...")
    
    # Test fields to verify
    test_fields = [
        'first_mtg_date',
        'first_mtg_amount', 
        'first_mtg_lender_name',
        'property_land_use_standardized_code',
        'property_land_use_description',
        'last_sale_date',
        'last_sale_price',
        'stories_number',
        'pool_flag'
    ]
    
    field_list = ','.join([f"'{field}'" for field in test_fields])
    db_config = config['database']
    cmd = [
        'psql',
        f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}",
        '-c', f"SELECT column_name FROM information_schema.columns WHERE table_schema='datnest' AND table_name='properties' AND column_name IN ({field_list});",
        '-t', '-A'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            found_fields = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            missing_fields = set(test_fields) - set(found_fields)
            
            if not missing_fields:
                print("✅ All customer priority fields verified in schema")
                return True
            else:
                print(f"❌ Missing fields: {missing_fields}")
                return False
        else:
            print(f"❌ Schema verification failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying schema: {e}")
        return False

def verify_land_use_codes(config):
    """Verify land use codes lookup table"""
    print("\n🔍 Verifying land use codes lookup table...")
    
    db_config = config['database']
    cmd = [
        'psql',
        f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}",
        '-c', "SELECT COUNT(*) FROM datnest.land_use_codes;",
        '-t', '-A'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            count = int(result.stdout.strip())
            if count >= 100:  # Should have 200+ codes
                print(f"✅ Land use codes table populated with {count} codes")
                return True
            else:
                print(f"❌ Land use codes table only has {count} codes (expected 200+)")
                return False
        else:
            print(f"❌ Land use codes verification failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying land use codes: {e}")
        return False

def update_production_loader():
    """Update the production loader with new field mappings"""
    print("\n🔄 Updating production loader with new fields...")
    
    loader_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'loaders', 'bulletproof_production_loader.py')
    
    # Read current loader
    with open(loader_path, 'r') as f:
        content = f.read()
    
    # Add new field mappings to FIELD_MAPPINGS
    new_mappings = '''
    # Customer Priority Fields - Mortgage/Lien Information
    'First_Mtg_Date': 'first_mtg_date',
    'First_Mtg_Amount': 'first_mtg_amount', 
    'First_Mtg_Rate': 'first_mtg_rate',
    'First_Mtg_Lender_Name': 'first_mtg_lender_name',
    'First_Mtg_Bal': 'first_mtg_bal',
    'Second_Mtg_Date': 'second_mtg_date',
    'Second_Mtg_Amount': 'second_mtg_amount',
    'Second_Mtg_Rate': 'second_mtg_rate', 
    'Second_Mtg_Lender_Name': 'second_mtg_lender_name',
    'Second_Mtg_Bal': 'second_mtg_bal',
    
    # Property Classification (with intelligent decoding)
    'Property_Land_Use_Standardized_Code': 'property_land_use_standardized_code',
    'Property_Type': 'property_type',
    'Property_Use_General': 'property_use_general',
    
    # Sales Intelligence
    'Last_Sale_Date': 'last_sale_date',
    'Last_Sale_Price': 'last_sale_price',
    'Last_Sale_Recording_Date': 'last_sale_recording_date',
    'Prior_Sale_Date': 'prior_sale_date',
    'Prior_Sale_Price': 'prior_sale_price',
    
    # Enhanced Property Details
    'Stories_Number': 'stories_number',
    'Garage_Spaces': 'garage_spaces',
    'Fireplace_Count': 'fireplace_count',
    'Pool_Flag': 'pool_flag',
    'Air_Conditioning_Flag': 'air_conditioning_flag','''
    
    # Update the FIELD_MAPPINGS dictionary
    if 'FIELD_MAPPINGS = {' in content:
        # Find the end of FIELD_MAPPINGS
        start_idx = content.find('FIELD_MAPPINGS = {')
        end_idx = content.find('}', start_idx) 
        
        # Insert new mappings before the closing brace
        updated_content = content[:end_idx] + new_mappings + '\n' + content[end_idx:]
        
        # Write updated loader
        with open(loader_path, 'w') as f:
            f.write(updated_content)
            
        print("✅ Production loader updated with customer priority fields")
        return True
    else:
        print("❌ Could not find FIELD_MAPPINGS in production loader")
        return False

def main():
    """Main deployment function"""
    print("🚀 DataNest Enhanced Schema Deployment")
    print("======================================")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Load configuration
    config = load_config()
    if not config:
        sys.exit(1)
    
    db_config = config['database']
    print(f"Database: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    # Check if SSH tunnel is needed (assume true for localhost with non-standard port)
    ssh_tunnel_needed = db_config['host'] == 'localhost' and db_config['port'] != 5432
    if ssh_tunnel_needed:
        print("\n⚠️  SSH tunnel required - make sure it's running!")
        print("Run: .\\scripts\\start_ssh_tunnel.ps1")
        input("Press Enter when SSH tunnel is ready...")
    
    deployment_success = True
    
    # Step 1: Deploy customer priority fields migration
    if not run_migration(config, '002_customer_priority_fields.sql'):
        deployment_success = False
    
    # Step 2: Populate land use codes lookup table
    if deployment_success and not run_migration(config, '002b_populate_land_use_codes.sql'):
        deployment_success = False
    
    # Step 3: Verify schema
    if deployment_success and not verify_schema(config):
        deployment_success = False
    
    # Step 4: Verify land use codes
    if deployment_success and not verify_land_use_codes(config):
        deployment_success = False
    
    # Step 5: Update production loader
    if deployment_success and not update_production_loader():
        deployment_success = False
    
    print("\n" + "="*50)
    if deployment_success:
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print("\n✅ Enhanced Schema Features Now Available:")
        print("   • 24 customer priority fields added to properties")
        print("   • Intelligent land use code decoding system")
        print("   • Mortgage/lien information fields")
        print("   • Sales intelligence fields")
        print("   • Enhanced property characteristics")
        print("   • Future-proof schema versioning system")
        print("   • Updated bulletproof production loader")
        print("\n🎯 Next Steps:")
        print("   1. Test the enhanced power batch loader")
        print("   2. Verify land use code auto-decoding works")
        print("   3. Run data quality analysis on new fields")
        print("   4. Update customer-facing API views")
        
        # Log successful deployment
        print(f"\n📝 Deployment logged at: {datetime.now().isoformat()}")
        
    else:
        print("❌ DEPLOYMENT FAILED!")
        print("Check error messages above and resolve issues before retrying.")
        sys.exit(1)

if __name__ == "__main__":
    main() 