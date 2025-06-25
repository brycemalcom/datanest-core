#!/usr/bin/env python3
"""
Test database connection with secure configuration
SECURITY: Uses secure configuration management - no hardcoded credentials
"""

import sys
import os

# Add src to path for secure config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_db_connection():
    """Test database connection using secure configuration"""
    print("🔍 Testing Database Connection")
    print("=" * 40)
    
    try:
        # Import secure config
        from config import get_db_config
        
        # Load database configuration securely
        db_config = get_db_config()
        print("✅ Database configuration loaded securely")
        
        # Test connection
        import psycopg2
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute('SELECT version()')
        version = cursor.fetchone()[0]
        print(f"✅ Database connected successfully")
        print(f"📊 PostgreSQL version: {version}")
        
        # Test table access
        cursor.execute('SELECT COUNT(*) FROM datnest.properties')
        count = cursor.fetchone()[0]
        print(f"📈 Current records: {count:,}")
        
        cursor.close()
        conn.close()
        
        print("🎉 Database connection test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Database connection test FAILED: {e}")
        print("\n🔧 Setup Instructions:")
        print("1. Set environment variables: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME")
        print("2. Or create local_config.json with database credentials")
        print("3. Or configure AWS Secrets Manager")
        print("4. See SECURITY_SETUP.md for detailed instructions")
        return False

if __name__ == "__main__":
    test_db_connection() 