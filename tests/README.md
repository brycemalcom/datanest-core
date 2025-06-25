# DataNest Core Platform - Test Suite

This directory contains all test files for validating system functionality, data processing, and performance.

## 📁 Test Categories

### 🔍 **Data Processing Tests**
- `test_data_cleaning.py` - Data cleaning and validation tests
- `test_csv_limits.py` - CSV/TSV file size and format limit tests
- `test_file_read.py` - File reading and parsing tests

### 🗄️ **Database Tests**
- `test_db_connection.py` - Database connectivity and authentication tests
- `quick_test_loader.py` - Quick loader functionality tests

### ⚡ **Performance Tests**
- `test_multiprocessing.py` - Parallel processing and concurrency tests
- `minimal_test.py` - Minimal functionality validation tests

### 🔒 **System Tests**  
- `read_only_test.py` - Read-only operations and safety tests

## 🚀 Running Tests

### Individual Test Execution
```bash
# Database connectivity
python tests/test_db_connection.py

# Data processing
python tests/test_file_read.py

# Performance validation
python tests/test_multiprocessing.py
```

### Quick Validation
```bash
# Run minimal test suite
python tests/minimal_test.py

# Quick loader test
python tests/quick_test_loader.py
```

## 🎯 Test Status

- **Total Tests**: 8 test modules
- **Coverage Areas**: Database, File I/O, Performance, Data Processing
- **Status**: All organized and ready for execution

## 📊 Critical Test Priorities

1. **Database Connection** - Ensure infrastructure connectivity
2. **File Processing** - Validate TSV parsing with 449 columns
3. **Performance** - Test with 160M record scale
4. **Data Integrity** - Validate complete data capture

## 🔧 Test Environment Setup

1. Ensure database connection is configured
2. Verify test data files are available
3. Install required dependencies from `requirements.txt`
4. Run tests in order: connection → file processing → performance 