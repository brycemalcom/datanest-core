#!/usr/bin/env python3
"""
Minimal test to verify basic functionality
SECURITY: Uses secure configuration management - no hardcoded credentials
"""

import sys
import os

# Add src to path for secure config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def minimal_test():
    """Minimal test with secure configuration"""
    print("🧪 Minimal Functionality Test")
    print("=" * 35)
    
    try:
        # Import secure config
        from config import get_db_config
        
        # Load database configuration securely
        db_config = get_db_config()
        print("✅ Database configuration loaded securely")
        
        # Test database connection
        import psycopg2
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute('SELECT 1')
        result = cursor.fetchone()[0]
        
        if result == 1:
            print("✅ Database query test passed")
        else:
            print("❌ Database query test failed")
            return False
        
        # Test schema access
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'datnest'")
        table_count = cursor.fetchone()[0]
        print(f"✅ Found {table_count} tables in datnest schema")
        
        cursor.close()
        conn.close()
        
        print("🎉 Minimal test PASSED - System is functional")
        return True
        
    except Exception as e:
        print(f"❌ Minimal test FAILED: {e}")
        print("\n🔧 Setup Instructions:")
        print("1. Set environment variables: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME")
        print("2. Or create local_config.json with database credentials")
        print("3. See SECURITY_SETUP.md for detailed instructions")
        return False

if __name__ == "__main__":
    minimal_test() 