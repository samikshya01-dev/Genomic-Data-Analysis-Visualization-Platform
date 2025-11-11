# 🚀 Run Project Script - Complete Guide

## Overview

The `run_project.sh` script is a comprehensive tool to run the Genomic Data Analysis Pipeline with various options.

---

## Quick Start

### Make Script Executable (First Time Only)
```bash
chmod +x run_project.sh
```

### Run the Script
```bash
./run_project.sh [OPTION]
```

---

## Available Commands

### 1. **help** - Show Help
```bash
./run_project.sh help
```
Shows all available commands and examples.

### 2. **test** - Quick Test (Recommended First)
```bash
./run_project.sh test
```
- **Duration:** ~30 seconds
- **Rows:** 1,000 variants
- **Purpose:** Verify everything works
- **Skips:** Enrichment (faster)

### 3. **small** - Small Dataset
```bash
./run_project.sh small
```
- **Duration:** ~5-10 minutes
- **Rows:** 5,000 variants
- **Purpose:** Test with reasonable data
- **Skips:** Enrichment

### 4. **medium** - Medium Dataset
```bash
./run_project.sh medium
```
- **Duration:** ~10-20 minutes
- **Rows:** 50,000 variants
- **Purpose:** Larger test run
- **Skips:** Enrichment

### 5. **full** - Full Pipeline
```bash
./run_project.sh full
```
- **Duration:** ~30-60 minutes
- **Rows:** All data (millions)
- **Purpose:** Complete production run
- **Includes:** Enrichment

### 6. **extract** - Download VCF Only
```bash
./run_project.sh extract
```
- Downloads VCF file from Ensembl
- Extracts .gz file
- Saves to `data/raw/`

### 7. **transform** - Transform VCF Only
```bash
./run_project.sh transform
```
- Parses VCF file
- Normalizes data
- Saves to `data/processed/`
- **Requires:** VCF file extracted first

### 8. **load** - Load to Database Only
```bash
./run_project.sh load
```
- Loads data into MySQL
- Creates tables
- Creates indexes
- **Requires:** Processed data files

### 9. **analyze** - Run Analysis Only
```bash
./run_project.sh analyze
```
- Generates summary reports
- Creates mutation analysis
- Saves to `data/processed/`
- **Requires:** Database loaded

### 10. **verify** - Verify Setup
```bash
./run_project.sh verify
```
- Checks Python version
- Verifies dependencies
- Tests configuration
- Shows setup status

### 11. **clean** - Clean Generated Files
```bash
./run_project.sh clean
```
- Removes log files
- Removes processed data
- Removes raw VCF files
- Removes Python cache
- **Warning:** Asks for confirmation

### 12. **tests** - Run Test Suite
```bash
./run_project.sh tests
```
- Runs all pytest tests
- Shows test results
- Verifies code quality

---

## Features

### ✨ Automatic Features

1. **Virtual Environment Check**
   - Automatically activates `.venv` if not active
   - Shows warning if virtual environment missing

2. **Dependency Check**
   - Verifies all packages installed
   - Auto-installs if missing

3. **Color-Coded Output**
   - ✓ Green: Success messages
   - ✗ Red: Error messages
   - ⚠ Yellow: Warnings
   - ℹ Blue: Information

4. **Safety Checks**
   - Asks confirmation before destructive operations
   - Checks for required files before running
   - Validates prerequisites

5. **Error Handling**
   - Exits on error (`set -e`)
   - Clear error messages
   - Helpful troubleshooting hints

---

## Usage Examples

### Example 1: First Time Setup and Test
```bash
# 1. Make executable
chmod +x run_project.sh

# 2. Verify setup
./run_project.sh verify

# 3. Run quick test
./run_project.sh test

# 4. Check results
ls -lh data/processed/
```

### Example 2: Full Pipeline Workflow
```bash
# Step 1: Download VCF data
./run_project.sh extract

# Step 2: Transform data
./run_project.sh transform

# Step 3: Load to database
./run_project.sh load

# Step 4: Run analysis
./run_project.sh analyze

# OR run all at once:
./run_project.sh small
```

### Example 3: Clean and Rerun
```bash
# Clean all generated files
./run_project.sh clean

# Run fresh pipeline
./run_project.sh small
```

### Example 4: Testing During Development
```bash
# Run tests
./run_project.sh tests

# Quick test run
./run_project.sh test

# Verify everything still works
./run_project.sh verify
```

---

## What Each Command Does

### Test Command Flow
```
test → Check venv → Install deps → Run pipeline (1K rows) → Show results
```

### Small Command Flow
```
small → Check venv → Install deps → Run pipeline (5K rows) → Show results
```

### Full Command Flow
```
full → Check venv → Install deps → Confirm → Run pipeline (all data) → Show results
```

### Clean Command Flow
```
clean → Confirm → Remove logs → Remove processed → Remove raw → Remove cache → Done
```

---

## Output Examples

### Success Output
```
================================================================
     GENOMIC DATA ANALYSIS & VISUALIZATION PLATFORM
================================================================

✓ Virtual environment is active
ℹ Running quick test (1000 variants)...
ℹ Duration: ~30 seconds

... (pipeline execution) ...

✓ Test completed successfully!
ℹ Check results in: data/processed/
```

### Error Output
```
✗ Virtual environment not found. Run: python3 -m venv .venv
```

### Warning Output
```
⚠ Virtual environment not activated!
ℹ Activating virtual environment...
✓ Virtual environment activated
```

---

## Troubleshooting

### Issue: "Permission denied"
```bash
# Solution: Make script executable
chmod +x run_project.sh
```

### Issue: "Virtual environment not found"
```bash
# Solution: Create virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue: "VCF file not found"
```bash
# Solution: Run extract first
./run_project.sh extract
```

### Issue: "Dependencies not installed"
```bash
# Solution: Install manually
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Advanced Usage

### Run with Custom Options
```bash
# Use Python directly for custom options
python3 src/main.py --full --max-rows 10000 --force-download
```

### Run Individual Phases
```bash
# Extract
./run_project.sh extract

# Transform with specific rows
python3 src/main.py --transform --max-rows 5000

# Load
./run_project.sh load
```

### Run in Background
```bash
# Run full pipeline in background
nohup ./run_project.sh full > pipeline.log 2>&1 &

# Check progress
tail -f pipeline.log
```

---

## Script Features

### 1. Color-Coded Messages
- Makes output easy to read
- Identifies issues quickly
- Highlights important information

### 2. Safety Confirmations
- Asks before destructive operations
- Prevents accidental data loss
- Clear cancel options

### 3. Automatic Setup
- Activates virtual environment
- Installs missing dependencies
- Validates prerequisites

### 4. Progress Indicators
- Shows duration estimates
- Displays what's happening
- Reports completion status

### 5. Error Prevention
- Checks for required files
- Validates setup before running
- Clear error messages

---

## File Locations

### Input
- VCF files: `data/raw/`
- Configuration: `config/`

### Output
- Processed data: `data/processed/`
- Log files: `data/logs/`
- Reports: `data/processed/mutation_report_*.txt`

### Database
- Host: localhost
- Database: genomic_analysis
- Tables: variants, genes, drug_annotations

---

## Quick Reference

| Command | Duration | Rows | Purpose |
|---------|----------|------|---------|
| `test` | 30 sec | 1K | Quick test |
| `small` | 5-10 min | 5K | Small run |
| `medium` | 10-20 min | 50K | Medium run |
| `full` | 30-60 min | All | Full pipeline |
| `extract` | 5-10 min | - | Download only |
| `transform` | 1-5 min | Varies | Parse only |
| `load` | 1-5 min | - | Load only |
| `analyze` | 1 min | - | Analysis only |
| `verify` | 10 sec | - | Check setup |
| `clean` | 10 sec | - | Clean files |
| `tests` | 2 min | - | Run tests |

---

## Tips

### For First-Time Users
1. Run `./run_project.sh verify` first
2. Then run `./run_project.sh test`
3. Check results in `data/processed/`
4. Try `./run_project.sh small` next

### For Daily Use
- Use `test` for quick checks
- Use `small` for development
- Use `full` for production runs
- Use `clean` to start fresh

### For Development
- Run `tests` after code changes
- Use `test` to verify changes work
- Use `verify` to check setup
- Use `clean` before git commits

---

## Summary

The `run_project.sh` script provides:
- ✅ Simple, intuitive commands
- ✅ Automatic setup and checks
- ✅ Color-coded output
- ✅ Safety confirmations
- ✅ Error handling
- ✅ Progress indicators
- ✅ Multiple run options

**Your all-in-one tool for running the Genomic Data Analysis Pipeline!** 🚀

---

**Created:** November 7, 2025  
**Version:** 1.0.0  
**Status:** ✅ Ready to use

