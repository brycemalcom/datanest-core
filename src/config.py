"""
DataNest Core Platform - Secure Configuration Management
CRITICAL: Never hardcode credentials in source code
"""

import os
import json
import boto3
from typing import Dict, Optional

class SecureConfig:
    """Secure configuration management for DataNest platform"""
    
    def __init__(self):
        self.db_config = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from secure sources (never hardcoded)"""
        # Priority: Environment Variables > AWS Secrets Manager > Local Config File
        
        # Try environment variables first (for local development)
        if self._load_from_env():
            print("✅ Configuration loaded from environment variables")
            return
            
        # Try AWS Secrets Manager (for production)
        if self._load_from_secrets_manager():
            print("✅ Configuration loaded from AWS Secrets Manager")
            return
            
        # Fallback to local config file (must be in .gitignore)
        if self._load_from_local_config():
            print("✅ Configuration loaded from local config file")
            return
            
        raise Exception("❌ SECURITY ERROR: No secure configuration source found!")
    
    def _load_from_env(self) -> bool:
        """Load from environment variables"""
        required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
        
        if all(os.getenv(var) for var in required_vars):
            self.db_config = {
                'host': os.getenv('DB_HOST'),
                'user': os.getenv('DB_USER'), 
                'password': os.getenv('DB_PASSWORD'),
                'database': os.getenv('DB_NAME'),
                'port': int(os.getenv('DB_PORT', 5432))
            }
            return True
        return False
    
    def _load_from_secrets_manager(self) -> bool:
        """Load from AWS Secrets Manager"""
        try:
            secrets_client = boto3.client('secretsmanager')
            response = secrets_client.get_secret_value(
                SecretId='datnest-core/db/credentials'
            )
            
            db_creds = json.loads(response['SecretString'])
            self.db_config = {
                'host': db_creds['host'],
                'user': db_creds['username'],
                'password': db_creds['password'], 
                'database': db_creds['dbname'],
                'port': db_creds['port']
            }
            return True
        except Exception as e:
            print(f"⚠️  AWS Secrets Manager not available: {e}")
            return False
    
    def _load_from_local_config(self) -> bool:
        """Load from local config file (must be in .gitignore)"""
        config_path = 'local_config.json'
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.db_config = config.get('database')
                    return True
            except Exception as e:
                print(f"⚠️  Local config file error: {e}")
        return False
    
    def get_db_config(self) -> Dict:
        """Get database configuration"""
        if not self.db_config:
            raise Exception("❌ SECURITY ERROR: Database configuration not loaded!")
        return self.db_config.copy()
    
    def get_connection_string(self) -> str:
        """Get PostgreSQL connection string"""
        config = self.get_db_config()
        return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

# Global configuration instance
config = SecureConfig()

def get_db_config() -> Dict:
    """Get secure database configuration"""
    return config.get_db_config()

def get_connection_string() -> str:
    """Get secure database connection string"""
    return config.get_connection_string() 