# 🚀 Quick Start Reference Card

## ⚡ Super Quick Start (Easiest Way)

```bash
# Make script executable (first time only)
chmod +x run_project.sh

# Run quick test
./run_project.sh test
```

## ⚡ Alternative Quick Start

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Run with Python module
python -m src.main --full --max-rows 1000 --skip-enrichment
```

## ❌ Common Mistake - DON'T DO THIS

```bash
python main.py --full  # ❌ WRONG - main.py is in src/ directory
```

## ✅ Correct Ways to Run

```bash
# Method 1: Use run script (RECOMMENDED)
./run_project.sh test

# Method 2: Python module
python -m src.main --full

# Method 3: Launcher script  
python run_pipeline.py --full

# Method 4: Direct path
python src/main.py --full
```

---

## 📋 Common Commands

### Setup & Installation
```bash
# Automated setup
python3 setup_helper.py

# Manual setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Verify setup
python verify_setup.py
```

### Running the Pipeline
```bash
# Full pipeline
make full                           # or: python -m src.main --full

# Test with limited rows
make test-run                       # or: python -m src.main --full --max-rows 10000

# Using launcher script (alternative)
python run_pipeline.py --full
python run_pipeline.py --full --max-rows 10000

# Individual phases
make extract                        # Download & extract VCF
make transform                      # Parse & transform data
make load                          # Load to database
make analyze                       # Generate reports

# Or with python -m
python -m src.main --extract
python -m src.main --transform
python -m src.main --load
python -m src.main --analyze
```

### Database Operations
```bash
# Create database
make db-create

# Reset database
make db-reset

# Manual MySQL commands
mysql -u root -p
CREATE DATABASE genomic_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Testing
```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test
pytest tests/test_vcf_parser.py -v
```

### Maintenance
```bash
# Clean generated files
make clean

# View all available commands
make help
```

---

## 📁 Key Files & Locations

| File/Directory | Purpose |
|----------------|---------|
| `src/main.py` | Main pipeline orchestrator |
| `config/db_config.yml` | Database settings |
| `config/etl_config.yml` | ETL configuration |
| `.env` | Environment variables (create from .env.template) |
| `data/raw/` | Downloaded VCF files |
| `data/processed/` | Processed CSV files |
| `data/logs/` | Application logs |

---

## ⚙️ Configuration Quick Reference

### Database Configuration (`config/db_config.yml`)
```yaml
database:
  host: localhost
  port: 3306
  database: genomic_analysis
  user: root
  password: your_password
```

### ETL Configuration (`config/etl_config.yml`)
```yaml
processing:
  chunk_size: 50000      # Reduce if memory issues
  max_workers: 4         # Adjust based on CPU cores
```

---

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | `source .venv/bin/activate` and `pip install -r requirements.txt` |
| Database connection failed | Check MySQL is running: `brew services start mysql` (macOS) |
| Out of memory | Use `--max-rows 10000` or reduce `chunk_size` in config |
| Download timeout | Use smaller chromosome or download manually |
| Permission denied | Run `chmod +x setup_helper.py verify_setup.py` |

---

## 📊 Pipeline Options

```bash
# Show all options
python -m src.main --help

# Common options
--full                  # Run complete pipeline
--extract              # Run extraction only
--transform            # Run transformation only
--load                 # Run loading only
--analyze              # Run analysis only
--max-rows N           # Process only N rows (testing)
--force-download       # Force re-download of VCF
--drop-existing        # Drop existing tables before loading
--skip-enrichment      # Skip annotation enrichment
--skip-analysis        # Skip analysis phase
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | Complete documentation |
| `QUICKSTART.md` | 5-minute setup guide |
| `TROUBLESHOOTING.md` | Common issues & solutions |
| `CONTRIBUTING.md` | Contribution guidelines |
| `PROJECT_SUMMARY.md` | Project overview |
| `powerbi/POWERBI_GUIDE.md` | Power BI integration |

---

## 🔍 Log Files

Check these for debugging:
```
data/logs/main_pipeline_YYYYMMDD.log      # Main pipeline
data/logs/src.etl_YYYYMMDD.log           # ETL operations
data/logs/src.analysis_YYYYMMDD.log      # Analysis
```

---

## 💡 Pro Tips

1. **First time?** Use `make test-run` to process limited rows
2. **Memory issues?** Use chr22 instead of chrX (edit `config/etl_config.yml`)
3. **Slow network?** Download VCF file manually to `data/raw/`
4. **Development?** Run `make dev-setup` for additional tools
5. **Check status:** Run `python verify_setup.py` anytime

---

## 🎯 Typical Workflow

```bash
# 1. Setup (one time)
python3 setup_helper.py
source .venv/bin/activate

# 2. Configure
cp .env.template .env
# Edit .env with your settings

# 3. Test run
make test-run

# 4. Full run
make full

# 5. View results
mysql -u root -p genomic_analysis
SELECT COUNT(*) FROM variants;

# 6. Open Power BI and connect to MySQL
```

---

## 📞 Getting Help

1. ✅ Check `TROUBLESHOOTING.md`
2. ✅ Review log files in `data/logs/`
3. ✅ Run `python verify_setup.py`
4. ✅ Check GitHub Issues
5. ✅ Contact maintainers

---

## 🔗 Quick Links

- Python: https://www.python.org/
- MySQL: https://dev.mysql.com/downloads/
- Power BI: https://powerbi.microsoft.com/
- Ensembl: https://www.ensembl.org/

---

**Version:** 1.0.0  
**Last Updated:** November 6, 2025  
**License:** MIT

