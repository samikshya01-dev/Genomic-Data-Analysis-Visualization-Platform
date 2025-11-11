# Troubleshooting Guide

This guide helps resolve common issues you might encounter when setting up or running the Genomic Data Analysis Platform.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Database Connection Issues](#database-connection-issues)
3. [Data Download Issues](#data-download-issues)
4. [Memory Issues](#memory-issues)
5. [Import Errors](#import-errors)
6. [Performance Issues](#performance-issues)
7. [Power BI Connection Issues](#power-bi-connection-issues)

---

## Installation Issues

### Issue: Python version error

**Error:** `Python 3.11+ required, but 3.X detected`

**Solution:**
1. Install Python 3.11 or higher from [python.org](https://www.python.org/downloads/)
2. Create a new virtual environment with the correct Python version:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

### Issue: pip install fails

**Error:** `ERROR: Could not find a version that satisfies the requirement...`

**Solution:**
1. Upgrade pip:
   ```bash
   pip install --upgrade pip
   ```
2. Install dependencies one by one to identify the problematic package:
   ```bash
   pip install pandas numpy sqlalchemy
   pip install -r requirements.txt
   ```
3. Check if you're using the correct Python version (3.11+)

### Issue: Virtual environment not activating

**Solution:**

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```cmd
.venv\Scripts\activate
```

If still not working, try:
```bash
python -m venv --clear .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Database Connection Issues

### Issue: Database connection failed

**Error:** `Database connection test failed`

**Solutions:**

1. **Check if MySQL is running:**
   ```bash
   # macOS
   brew services list
   brew services start mysql
   
   # Linux
   sudo systemctl status mysql
   sudo systemctl start mysql
   
   # Windows
   # Check Services app for MySQL service
   ```

2. **Verify credentials in config/db_config.yml:**
   ```yaml
   database:
     host: localhost
     port: 3306
     database: genomic_analysis
     user: root
     password: your_actual_password
   ```

3. **Test MySQL connection manually:**
   ```bash
   mysql -u root -p
   ```

4. **Create database if it doesn't exist:**
   ```bash
   mysql -u root -p -e "CREATE DATABASE genomic_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   ```

### Issue: Access denied for user

**Error:** `Access denied for user 'root'@'localhost'`

**Solution:**
1. Reset MySQL root password:
   ```bash
   # Stop MySQL
   brew services stop mysql  # macOS
   
   # Start MySQL in safe mode
   mysqld_safe --skip-grant-tables &
   
   # Connect and reset password
   mysql -u root
   FLUSH PRIVILEGES;
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
   quit;
   
   # Restart MySQL normally
   brew services start mysql
   ```

2. Or create a new database user:
   ```sql
   CREATE USER 'genomic_user'@'localhost' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON genomic_analysis.* TO 'genomic_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

### Issue: Table already exists error

**Error:** `Table 'variants' already exists`

**Solution:**
Run pipeline with `--drop-existing` flag to recreate tables:
```bash
python -m src.main --full --drop-existing
```

---

## Data Download Issues

### Issue: Download timeout or slow download

**Error:** `Timeout error` or very slow download speed

**Solutions:**

1. **Use a different VCF file (smaller chromosome):**
   
   Edit `config/etl_config.yml`:
   ```yaml
   data_sources:
     vcf_url: "https://ftp.ensembl.org/pub/release-115/variation/vcf/homo_sapiens/homo_sapiens-chr22.vcf.gz"
   ```

2. **Resume interrupted download:**
   
   If download was interrupted, delete the partial file and retry:
   ```bash
   rm data/raw/homo_sapiens-chrX.vcf.gz
   python -m src.main --extract --force-download
   ```

3. **Download manually:**
   
   Download the file manually and place it in `data/raw/`:
   ```bash
   wget https://ftp.ensembl.org/pub/release-115/variation/vcf/homo_sapiens/homo_sapiens-chrX.vcf.gz -O data/raw/homo_sapiens-chrX.vcf.gz
   ```

### Issue: File extraction fails

**Error:** `Error decompressing file`

**Solution:**
1. Verify the downloaded file is not corrupted:
   ```bash
   gunzip -t data/raw/homo_sapiens-chrX.vcf.gz
   ```

2. If corrupted, re-download:
   ```bash
   python -m src.main --extract --force-download
   ```

---

## Memory Issues

### Issue: Out of memory error

**Error:** `MemoryError` or system becomes unresponsive

**Solutions:**

1. **Process data in smaller chunks:**
   
   Edit `config/etl_config.yml`:
   ```yaml
   processing:
     chunk_size: 10000  # Reduce from 50000
     max_workers: 2     # Reduce from 4
   ```

2. **Run with limited rows (testing):**
   ```bash
   python -m src.main --full --max-rows 50000
   ```

3. **Use a smaller chromosome:**
   
   Edit `config/etl_config.yml` to use chr22 instead of chrX (smaller file)

4. **Increase system swap space:**
   ```bash
   # Linux
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### Issue: Pandas DataFrame too large

**Solution:**
Use dtype optimization in transform phase:
```python
# This is already implemented in the transformer
# If you're modifying code, ensure you use appropriate dtypes
variants_df['POS'] = variants_df['POS'].astype('int32')
variants_df['AF'] = variants_df['AF'].astype('float32')
```

---

## Import Errors

### Issue: Module not found

**Error:** `ModuleNotFoundError: No module named 'pandas'`

**Solution:**
1. Ensure virtual environment is activated:
   ```bash
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate      # Windows
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify installation:
   ```bash
   pip list | grep pandas
   ```

### Issue: Cannot import from src

**Error:** `ModuleNotFoundError: No module named 'src'`

**Solution:**
Run from project root directory:
```bash
cd "Genomic Data Analysis Visualization Platform"
python -m src.main --help
```

Or install package in development mode:
```bash
pip install -e .
```

---

## Performance Issues

### Issue: Pipeline is very slow

**Solutions:**

1. **Enable parallel processing:**
   
   Edit `config/etl_config.yml`:
   ```yaml
   processing:
     max_workers: 8  # Increase based on CPU cores
   ```

2. **Optimize database loading:**
   
   Edit `config/db_config.yml`:
   ```yaml
   performance:
     batch_size: 50000  # Increase from 10000
     commit_frequency: 100000
   ```

3. **Skip enrichment phase (for testing):**
   ```bash
   python -m src.main --full --skip-enrichment
   ```

4. **Use smaller dataset for testing:**
   ```bash
   python -m src.main --full --max-rows 10000
   ```

### Issue: Database queries are slow

**Solutions:**

1. **Ensure indexes are created:**
   
   Check `config/db_config.yml`:
   ```yaml
   performance:
     enable_indexes: true
   ```

2. **Add custom indexes:**
   ```sql
   CREATE INDEX idx_variant_gene ON variants(gene_symbol);
   CREATE INDEX idx_variant_sig ON variants(clinical_significance);
   ```

3. **Optimize MySQL configuration:**
   
   Edit MySQL config file (my.cnf or my.ini):
   ```ini
   [mysqld]
   innodb_buffer_pool_size = 2G
   max_connections = 200
   query_cache_size = 64M
   ```

---

## Power BI Connection Issues

### Issue: Cannot connect Power BI to MySQL

**Solutions:**

1. **Install MySQL ODBC Driver:**
   - Download from: https://dev.mysql.com/downloads/connector/odbc/
   - Install the appropriate version for your system

2. **Use correct connection string in Power BI:**
   ```
   Server: localhost
   Database: genomic_analysis
   ```

3. **Check MySQL user permissions:**
   ```sql
   GRANT SELECT ON genomic_analysis.* TO 'root'@'localhost';
   FLUSH PRIVILEGES;
   ```

4. **Test connection with MySQL Workbench first** to verify credentials

### Issue: Power BI reports are slow

**Solutions:**

1. **Use aggregated views instead of raw tables**

2. **Create materialized views in MySQL:**
   ```sql
   CREATE TABLE mutation_summary_materialized AS
   SELECT gene_symbol, COUNT(*) as variant_count
   FROM variants
   GROUP BY gene_symbol;
   ```

3. **Import data instead of DirectQuery** for better performance

---

## Common Log File Locations

Check these logs for more detailed error information:

- Pipeline logs: `data/logs/main_pipeline_YYYYMMDD.log`
- ETL logs: `data/logs/src.etl_YYYYMMDD.log`
- Analysis logs: `data/logs/src.analysis_YYYYMMDD.log`

---

## Getting Help

If you're still experiencing issues:

1. Check the logs in `data/logs/` directory
2. Review the configuration files in `config/` directory
3. Run with verbose logging:
   ```bash
   python -m src.main --full 2>&1 | tee pipeline_output.log
   ```

4. Create an issue on GitHub with:
   - Error message
   - Relevant log files
   - System information (OS, Python version, MySQL version)
   - Steps to reproduce the issue

---

## Quick Diagnostic Commands

```bash
# Check Python version
python --version

# Check if virtual environment is active
which python

# Check installed packages
pip list

# Test MySQL connection
mysql -u root -p -e "SELECT VERSION();"

# Check if database exists
mysql -u root -p -e "SHOW DATABASES LIKE 'genomic_analysis';"

# Check disk space
df -h

# Check available memory
free -h  # Linux
vm_stat  # macOS

# Test import of key modules
python -c "import pandas, numpy, sqlalchemy; print('All imports successful')"
```

