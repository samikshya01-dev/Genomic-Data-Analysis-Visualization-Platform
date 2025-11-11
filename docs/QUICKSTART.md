# Quick Start Guide

This guide will help you get the Genomic Data Analysis Platform up and running quickly.

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.11+ installed
- ✅ MySQL 8.0+ installed and running
- ✅ At least 10GB free disk space
- ✅ Internet connection for downloading VCF data

## 5-Minute Setup

### Step 1: Environment Setup (2 minutes)

```bash
# Navigate to project directory
cd "Genomic Data Analysis Visualization Platform"

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Database Configuration (2 minutes)

```bash
# Start MySQL (if not running)
# macOS: brew services start mysql
# Linux: sudo systemctl start mysql
# Windows: Start MySQL service from Services

# Create database
mysql -u root -p
```

```sql
CREATE DATABASE genomic_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### Step 3: Configure Settings (1 minute)

Edit `config/db_config.yml`:
```yaml
database:
  host: localhost
  port: 3306
  database: genomic_analysis
  user: root  # Change this
  password: your_password  # Change this
```

## Running Your First Pipeline

### Option A: Test Run (Recommended for First Time)

Process only 1,000 variants to test the setup:

```bash
python src/main.py --full --max-rows 1000 --drop-existing
```

This will:
- ✅ Download VCF file (if not exists)
- ✅ Parse 1,000 variants
- ✅ Enrich with drug data
- ✅ Load to MySQL
- ✅ Generate analysis reports

**Expected time:** 5-10 minutes

### Option B: Full Pipeline

Process the complete chromosome X dataset:

```bash
python src/main.py --full --drop-existing
```

**Expected time:** 30-60 minutes (depending on connection speed)

## Verifying the Installation

### Check Database

```bash
mysql -u root -p genomic_analysis
```

```sql
-- Check table counts
SELECT 'variants' as table_name, COUNT(*) as count FROM variants
UNION ALL
SELECT 'genes', COUNT(*) FROM genes
UNION ALL
SELECT 'drug_annotations', COUNT(*) FROM drug_annotations
UNION ALL
SELECT 'mutation_summary', COUNT(*) FROM mutation_summary;
```

### Check Generated Files

```bash
# List processed files
ls -lh data/processed/

# View analysis report
cat data/processed/mutation_report_*.txt
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Or run specific test
pytest tests/test_vcf_parser.py -v
```

## Common Quick Start Issues

### Issue 1: MySQL Connection Error

**Error:** `Can't connect to MySQL server`

**Solution:**
```bash
# Check if MySQL is running
mysql --version
mysqladmin -u root -p status

# If not running, start it
# macOS: brew services start mysql
# Linux: sudo systemctl start mysql
```

### Issue 2: Import Errors

**Error:** `ModuleNotFoundError: No module named 'vcfpy'`

**Solution:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 3: Permission Denied

**Error:** `Permission denied: 'data/raw'`

**Solution:**
```bash
# Create directories with proper permissions
mkdir -p data/{raw,processed,logs}
chmod 755 data/*
```

### Issue 4: Out of Memory

**Error:** `MemoryError`

**Solution:**
```yaml
# Reduce chunk size in config/etl_config.yml
processing:
  chunk_size: 10000  # Reduce from 50000
```

Or use the `--max-rows` option:
```bash
python src/main.py --full --max-rows 10000
```

## Next Steps

After successful installation:

1. **Explore the Data**
   ```bash
   # Generate summary statistics
   python src/main.py --analyze
   ```

2. **Connect Power BI**
   - Open Power BI Desktop
   - Get Data → MySQL Database
   - Server: `localhost:3306`
   - Database: `genomic_analysis`
   - Import tables: `variants`, `genes`, `drug_annotations`, `mutation_summary`
   - Follow [Power BI Guide](powerbi/POWERBI_GUIDE.md)

3. **Schedule Automated Runs**
   ```bash
   # Add to crontab (macOS/Linux)
   crontab -e
   # Add: 0 2 * * 0 cd /path/to/project && /path/to/.venv/bin/python src/main.py --full
   ```

4. **Customize for Your Needs**
   - Edit `config/etl_config.yml` to change data sources
   - Modify `src/etl/enrich_annotations.py` to add custom annotations
   - Add new analysis in `src/analysis/`

## Usage Examples

### Example 1: Download and Transform Only

```bash
python src/main.py --extract
python src/main.py --transform --max-rows 5000
```

### Example 2: Re-process with Fresh Data

```bash
python src/main.py --full --force-download --drop-existing
```

### Example 3: Run Analysis on Existing Data

```bash
python src/main.py --analyze
```

### Example 4: Custom Pipeline

```python
from src.main import GenomicPipeline

pipeline = GenomicPipeline()

# Custom workflow
pipeline.run_extraction()
pipeline.run_transformation(max_rows=20000)
pipeline.run_loading(drop_existing=True)
```

## Performance Tips

### For Faster Processing

1. **Use SSD storage** for `data/` directory
2. **Increase MySQL buffer pool**:
   ```ini
   # In my.cnf or my.ini
   innodb_buffer_pool_size = 2G
   ```
3. **Use parallel processing**:
   ```yaml
   # In config/etl_config.yml
   processing:
     max_workers: 8
   ```

### For Limited Resources

1. **Process in smaller chunks**:
   ```bash
   python src/main.py --transform --max-rows 5000
   ```
2. **Skip enrichment** to save time:
   ```bash
   python src/main.py --full --skip-enrichment
   ```

## Getting Help

- 📖 Full documentation: [README.md](README.md)
- 📊 Power BI guide: [powerbi/POWERBI_GUIDE.md](powerbi/POWERBI_GUIDE.md)
- 🐛 Report issues: Create an issue on GitHub
- 💬 Questions: Contact the project team

## Quick Reference Commands

```bash
# Full pipeline
python src/main.py --full

# Test with 1000 rows
python src/main.py --full --max-rows 1000

# Individual phases
python src/main.py --extract
python src/main.py --transform
python src/main.py --enrich
python src/main.py --load
python src/main.py --analyze

# Force refresh
python src/main.py --full --force-download --drop-existing

# Run tests
pytest tests/ -v

# Check logs
tail -f data/logs/main_pipeline_*.log
```

## Success Checklist

After setup, you should have:
- ✅ Virtual environment activated
- ✅ All dependencies installed
- ✅ MySQL database created
- ✅ Configuration files updated
- ✅ Test pipeline completed successfully
- ✅ Data in MySQL tables
- ✅ Analysis reports generated
- ✅ Tests passing

Congratulations! Your Genomic Data Analysis Platform is ready to use! 🎉

---

**Need help?** Check the [README.md](README.md) for detailed documentation or contact the project team.

