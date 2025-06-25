# DataNest Core Platform - Source Code

This directory contains the core application source code for the DataNest platform, organized by functionality.

## 📁 Directory Structure

### `/loaders`
**Production data loading modules**
- `production_copy_loader.py` - Primary working loader using COPY command (ACTIVE)
- `bulletproof_loader.py` - Simplified, error-resistant loader (BACKUP)

### `/analyzers` 
**Data analysis and field mapping tools**
- `analyze_all_columns.py` - Comprehensive column analysis across all TSV files
- `dataset_scale_analysis.py` - Scale and performance analysis tools
- `analyze_tsv_fields.py` - TSV field structure analysis
- `analyze_fields.py` - General field analysis utilities

### `/utils`
**Utility functions and helpers**
- `status_check.py` - System and database status monitoring
- `find_table.py` - Database table discovery utilities
- `check_schema.py` - Schema validation tools
- `check_excel.py` - Excel file validation

## 🚀 Getting Started

1. **Data Loading**: Use `loaders/production_copy_loader.py` for production data loading
2. **Analysis**: Run analyzers to understand data structure and quality
3. **Utilities**: Use utils for system monitoring and validation

## 📊 Current Status

- **Active Loaders**: 2 production-ready loaders
- **Analysis Tools**: 4 comprehensive analyzers  
- **Utilities**: 4 essential utility functions
- **Data Loss Issue**: 97% data loss identified (436/449 columns not captured)

## 🎯 Next Steps

1. Implement hybrid architecture (SQL + JSONB) for complete data capture
2. Consolidate mapping logic from analyzers into production loader
3. Expand schema to capture all 449 TSV columns 