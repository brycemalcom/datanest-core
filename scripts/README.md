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

### 2. Data Processing Pipeline
```powershell
# Extract all TSV files
.\scripts\extract_all_files.ps1

# Or batch processing
.\scripts\extract_batch.ps1
```

### 3. Infrastructure Connection
```powershell
# Start secure database tunnel
.\scripts\start_ssh_tunnel.ps1
```

### 4. Schema Deployment
```python
# Deploy database schema
python scripts/deploy_schema.py

# Deploy Lambda functions
python scripts/deploy_schema_lambda.py
```

## 🎯 Script Status

- **PowerShell Scripts**: 6 automation scripts
- **Python Deployment**: 2 deployment utilities
- **Lambda Package**: 1 ready-to-deploy package
- **Total Functionality**: Complete platform automation

## 🔧 Prerequisites

### PowerShell Scripts
- PowerShell 5.0+ (Windows)
- Administrative privileges (for some setup scripts)
- Network access for data extraction

### Python Deployment Scripts
- Python 3.8+
- AWS CLI configured
- Database connection credentials
- Lambda deployment permissions

## 📊 Script Execution Order

1. **Setup**: `quick-start.ps1` (complete initialization)
2. **Data**: `extract_all_files.ps1` (data preparation)  
3. **Infrastructure**: `start_ssh_tunnel.ps1` (connectivity)
4. **Deployment**: `deploy_schema.py` → `deploy_schema_lambda.py`

## ⚠️ Important Notes

- Run PowerShell scripts as Administrator when needed
- Ensure AWS credentials are configured before deployment
- Verify database connectivity before schema deployment
- Test with small batches before full-scale extraction 