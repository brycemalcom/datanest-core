# DataNest Core Platform - Scripts & Deployment

This directory contains all PowerShell scripts, deployment tools, and automation utilities for the DataNest platform.

## 📁 Script Categories

### 🚀 **Quick Start & Setup**
- `quick-start.ps1` - Complete platform initialization script (12KB)
- `setup_folders.ps1` - Project folder structure setup
- `setup_file_structure.ps1` - File organization automation

### 📦 **Data Extraction & Processing**
- `extract_all_files.ps1` - Bulk TSV file extraction (5.6KB)
- `extract_batch.ps1` - Batch processing utilities (1.9KB)

### 🔌 **Infrastructure & Connectivity**
- `start_ssh_tunnel.ps1` - SSH tunnel management for secure database access

### 🗄️ **Database Management**
- `run_single_migration.py` - Execute individual SQL migrations
- `validate_current_schema_status.py` - Comprehensive schema validation
- `get_category_fields.py` - Extract TSV headers by data category

### ☁️ **Deployment & Lambda**
- `deploy_schema_lambda.py` - Lambda function deployment (5.3KB)
- `deploy_schema.py` - Database schema deployment (2.2KB)
- `deploy_schema_lambda.zip` - Packaged Lambda deployment

## 🚀 Quick Start Guide

### 1. Initial Platform Setup
```powershell
# Run the comprehensive setup
.\scripts\quick-start.ps1

# Or manual setup
.\scripts\setup_folders.ps1
.\scripts\setup_file_structure.ps1
```

### 2. Database Management
```python
# Run a single migration
python scripts/run_single_migration.py 006_complete_building_characteristics.sql

# Validate current schema status
python scripts/validate_current_schema_status.py

# Extract category fields from data dictionary
python scripts/get_category_fields.py "Building Characteristics"
```

### 3. Data Processing Pipeline
```powershell
# Extract all TSV files
.\scripts\extract_all_files.ps1

# Or batch processing
.\scripts\extract_batch.ps1
```

### 4. Infrastructure Connection
```powershell
# Start secure database tunnel
.\scripts\start_ssh_tunnel.ps1
```

## 🎯 Script Status

- **PowerShell Scripts**: 6 automation scripts
- **Python Tools**: Multiple database and analysis utilities
- **Migration Tools**: Systematic database enhancement utilities
- **Lambda Package**: 1 ready-to-deploy package
- **Total Functionality**: Complete platform automation

## 🔧 Prerequisites

### PowerShell Scripts
- PowerShell 5.0+ (Windows)
- Administrative privileges (for some setup scripts)
- Network access for data extraction

### Python Scripts
- Python 3.8+
- Database connection configured (see [SECURITY_SETUP.md](../SECURITY_SETUP.md))
- Required dependencies from `requirements.txt`

### Deployment Scripts
- AWS CLI configured
- Lambda deployment permissions

## 📊 Script Execution Order

1. **Setup**: `quick-start.ps1` (complete initialization)
2. **Database**: `validate_current_schema_status.py` (verify schema)
3. **Infrastructure**: `start_ssh_tunnel.ps1` (connectivity)
4. **Development**: Use migration and analysis tools as needed

## ⚠️ Important Notes

- Run PowerShell scripts as Administrator when needed
- Ensure secure database configuration before running scripts
- Use `run_single_migration.py` for systematic database enhancements
- Test with validation scripts before production changes

## 🔗 **Documentation References**

> **Note**: For current development status and systematic approach, see our living documentation:
> - **[CURRENT_PROJECT_STATUS.md](../CURRENT_PROJECT_STATUS.md)** - Current development status
> - **[ENGINEERING_HANDOFF.md](../ENGINEERING_HANDOFF.md)** - Technical handoffs
> - **[PROJECT_README.md](../PROJECT_README.md)** - High-level system architecture 