# DataNest Core Platform - Source Code

This directory contains the core application source code for the DataNest platform, organized by functionality.

## 📁 Directory Structure

### `/loaders`
**Production data loading modules**
- `enhanced_production_loader_batch4a.py` - Current production loader (ACTIVE)
- `bulletproof_production_loader.py` - Enhanced production loader (ACTIVE)
- `production_copy_loader.py` - Legacy loader (REFERENCE)

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

1. **Data Loading**: Use `loaders/enhanced_production_loader_batch4a.py` for production data loading
2. **Analysis**: Run analyzers to understand data structure and quality
3. **Utilities**: Use utils for system monitoring and validation

## 📊 Current Status

> **Note**: For current project status and field mapping progress, see **[CURRENT_PROJECT_STATUS.md](../CURRENT_PROJECT_STATUS.md)**

- **Active Loaders**: Enhanced production loaders operational
- **Analysis Tools**: 4 comprehensive analyzers  
- **Utilities**: 4 essential utility functions
- **Database Schema**: 209 columns with systematic migration approach
- **Field Mapping**: Systematic completion in progress (see current status document)

## 🎯 Development Approach

1. **Evidence-Based Mapping**: All field mappings verified against data_dictionary.txt
2. **Systematic Enhancement**: Category-by-category completion approach
3. **Production Quality**: Comprehensive validation and testing framework
4. **Zero Data Loss Goal**: Complete capture of all 449 TSV fields

## 🔗 **Documentation References**

- **[CURRENT_PROJECT_STATUS.md](../CURRENT_PROJECT_STATUS.md)** - Real-time project status
- **[DATANEST_PROGRESS_LOG.md](../DATANEST_PROGRESS_LOG.md)** - Development history
- **[ENGINEERING_HANDOFF.md](../ENGINEERING_HANDOFF.md)** - Session handoffs 