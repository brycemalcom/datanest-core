# DataNest Core Platform - Setup Guide

> **⚠️ IMPORTANT**: This document contains legacy setup information. For current development setup, please refer to the updated documentation structure.

## 🔗 **Current Documentation Structure**

### **For New Engineering Sessions:**
- **[PROJECT_README.md](PROJECT_README.md)** - High-level system architecture and quick start guide
- **[SECURITY_SETUP.md](SECURITY_SETUP.md)** - Secure configuration and credentials setup
- **[CURRENT_PROJECT_STATUS.md](CURRENT_PROJECT_STATUS.md)** - Current development status

### **For Development Progress:**
- **[DATANEST_PROGRESS_LOG.md](DATANEST_PROGRESS_LOG.md)** - Complete development history
- **[ENGINEERING_HANDOFF.md](ENGINEERING_HANDOFF.md)** - Session-to-session handoffs

## 🚀 **Quick Start for New Engineers**

### **1. Environment Setup**
```bash
# Clone repository and setup
git clone [repository]
cd datanest-core-platform
pip install -r requirements.txt
```

### **2. Secure Configuration**
Follow the comprehensive security setup guide:
```bash
# See detailed instructions in:
# SECURITY_SETUP.md
```

### **3. Database Connection**
```bash
# Start SSH tunnel
.\scripts\start_ssh_tunnel.ps1

# Verify connection
python tests/test_db_connection.py
```

### **4. Validate Current Status**
```python
# Check current schema status
python scripts/validate_current_schema_status.py
```

## 🎯 **Current System Status**

### **Infrastructure:**
- ✅ **AWS Environment**: Production-ready infrastructure operational
- ✅ **Database**: PostgreSQL with 209-column schema
- ✅ **Security**: Enterprise-level credential management
- ✅ **Processing**: 400+ records/second capability

### **Development Approach:**
- **Evidence-Based**: All field mappings verified against data_dictionary.txt
- **Systematic**: Category-by-category completion approach  
- **Zero Data Loss**: Target 449/449 field coverage
- **Production Quality**: Comprehensive validation framework

## 📊 **For Historical Reference**

This document previously contained AWS infrastructure setup instructions. The current system architecture and setup approach has evolved significantly. For the most current information:

1. **System Architecture**: See [PROJECT_README.md](PROJECT_README.md)
2. **Current Status**: See [CURRENT_PROJECT_STATUS.md](CURRENT_PROJECT_STATUS.md)
3. **Security Setup**: See [SECURITY_SETUP.md](SECURITY_SETUP.md)
4. **Development Progress**: See [DATANEST_PROGRESS_LOG.md](DATANEST_PROGRESS_LOG.md)

---

**🎯 The DataNest Core Platform is now focused on systematic field completion and comprehensive property intelligence. All setup and development guidance is available in the updated documentation structure.** 