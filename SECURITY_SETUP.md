# 🔒 DataNest Core Platform - Security Setup Guide

**CRITICAL**: This platform uses secure configuration management. **NEVER HARDCODE CREDENTIALS** in source code.

## 🚨 **SECURITY REQUIREMENTS**

### **Before Running Any Code**
1. ✅ **Set up secure configuration** (choose one method below)
2. ✅ **Verify .gitignore** protects sensitive files  
3. ✅ **Test database connection** with secure config
4. ✅ **Never commit credentials** to version control

## 🔧 **Configuration Methods** (Choose One)

### **Method 1: Environment Variables (Recommended for Development)**

```bash
# Set these environment variables (Windows PowerShell)
$env:DB_HOST = "localhost"
$env:DB_PORT = "15432"
$env:DB_USER = "datnest_admin"
$env:DB_PASSWORD = "your_secure_password"
$env:DB_NAME = "datnest"

# Or Linux/Mac
export DB_HOST="localhost"
export DB_PORT="15432" 
export DB_USER="datnest_admin"
export DB_PASSWORD="your_secure_password"
export DB_NAME="datnest"
```

### **Method 2: Local Configuration File (Development)**

1. Copy the example configuration:
   ```bash
   cp local_config.example.json local_config.json
   ```

2. Edit `local_config.json` with your real credentials:
   ```json
   {
     "database": {
       "host": "localhost",
       "port": 15432,
       "database": "datnest",
       "user": "datnest_admin", 
       "password": "YOUR_REAL_PASSWORD_HERE"
     }
   }
   ```

3. **IMPORTANT**: `local_config.json` is automatically protected by `.gitignore`

### **Method 3: AWS Secrets Manager (Production)**

For production deployment, credentials are automatically loaded from AWS Secrets Manager:
- Secret ID: `datnest-core/db/credentials`
- Region: `us-east-1`
- Format: JSON with keys: `host`, `username`, `password`, `dbname`, `port`

## 🧪 **Testing Your Setup**

### **1. Test Database Connection**
```bash
# From project root
python tests/test_db_connection.py
```

### **2. Test Production Loader**
```bash
# From project root  
python src/loaders/bulletproof_loader.py
```

### **Expected Output:**
```
✅ Database configuration loaded securely
✅ Database connected successfully
```

## ⚠️ **Security Violations - DO NOT DO THIS**

### **❌ NEVER Hardcode Credentials**
```python
# WRONG - Never do this
CONN_PARAMS = {
    'user': 'datnest_admin',
    'password': 'DatNest2024!SecurePass#'  # SECURITY VIOLATION
}
```

### **✅ ALWAYS Use Secure Config**
```python
# CORRECT - Always do this
from config import get_db_config
CONN_PARAMS = get_db_config()
```

## 🔒 **Files Protected by .gitignore**

The following files are automatically protected from git commits:
- `*.tfstate` - Terraform state files
- `*.tfvars` - Terraform variables
- `local_config.json` - Local configuration
- `*password*` - Any file with 'password' in name
- `*secret*` - Any file with 'secret' in name
- `temp/` - Temporary files directory

## 🚨 **If Credentials Are Exposed**

### **Immediate Actions:**
1. **Change all exposed passwords immediately**
2. **Rotate AWS keys if exposed** 
3. **Update AWS Secrets Manager**
4. **Review git history** for any committed credentials
5. **Notify security team**

### **Git History Cleanup** (if credentials were committed):
```bash
# Remove sensitive file from git history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/sensitive/file' \
  --prune-empty --tag-name-filter cat -- --all

# Force push (DANGER - coordinate with team)
git push origin --force --all
```

## 📋 **Security Checklist**

Before committing any code:
- [ ] No hardcoded passwords in any files
- [ ] No API keys in source code
- [ ] .gitignore includes all sensitive patterns
- [ ] Test with secure configuration methods
- [ ] All team members use secure setup

## 🎯 **Quick Setup for New Developers**

1. **Clone repository**
2. **Copy configuration**: `cp local_config.example.json local_config.json`
3. **Update credentials** in `local_config.json` 
4. **Test connection**: `python tests/test_db_connection.py`
5. **Start developing** with secure foundation

---

## 🚀 **Remember: Security First, Always**

**The DataNest platform is built with enterprise-level security. Every developer must follow these practices to maintain our security posture.**

*No exceptions. No shortcuts. No hardcoded credentials.* 