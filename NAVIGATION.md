# 🗺️ Navigation Guide - Start Here!

Welcome to the Genomic Data Analysis Visualization Platform! This guide will help you find everything quickly.

---

## 🚀 Quick Start (First Time Users)

1. **Read This First**: [README.md](README.md)
2. **Quick Setup**: [docs/QUICKSTART.md](docs/QUICKSTART.md)
3. **Run Pipeline**: `./run_project.sh small`
4. **Verify Database**: `./scripts/utilities/verify_database.sh`

---

## 📚 Documentation Map

### 🎯 Essential Reading
- **[README.md](README.md)** - Main project documentation
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - 5-minute quick start
- **[CHEATSHEET.sh](CHEATSHEET.sh)** - All commands at a glance

### 📖 User Guides
- **[docs/RUN_PROJECT_GUIDE.md](docs/RUN_PROJECT_GUIDE.md)** - Complete run guide
- **[docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Command reference
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Fix common issues

### 🏗️ Technical Documentation
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Complete file structure
- **[docs/architecture/](docs/architecture/)** - System architecture
- **[docs/technology/](docs/technology/)** - Technology stack

### 🎨 Quick References
- **[QUICK_STRUCTURE_GUIDE.md](QUICK_STRUCTURE_GUIDE.md)** - Where everything is
- **[docs/README.md](docs/README.md)** - Documentation index
- **[scripts/README.md](scripts/README.md)** - Scripts documentation

---

## 🔧 Common Tasks

### Running the Pipeline
```bash
./run_project.sh small              # 5K variants (5-10 min)
./run_project.sh medium             # 50K variants (10-20 min)
./scripts/utilities/run_pipeline_now.sh  # Interactive mode
```

### Database Management
```bash
./scripts/utilities/verify_database.sh   # Check status
python scripts/utilities/fix_database.py # Fix issues
./scripts/utilities/quick_fix.sh        # Quick fix
```

### Setup & Verification
```bash
python scripts/setup/verify_setup.py    # Verify installation
cat docs/QUICKSTART.md                  # Setup guide
```

---

## 📂 Where Everything Is

### Configuration
- **Database**: `config/db_config.yml`
- **Pipeline**: `config/etl_config.yml`

### Source Code
- **Main Pipeline**: `src/main.py`
- **ETL Modules**: `src/etl/`
- **Analysis**: `src/analysis/`
- **Utilities**: `src/utils/`

### Scripts
- **Utilities**: `scripts/utilities/`
- **Setup**: `scripts/setup/`

### Data
- **Raw VCF**: `data/raw/`
- **Processed CSV**: `data/processed/`
- **Logs**: `data/logs/`

### Documentation
- **All Docs**: `docs/`
- **Guides**: `docs/*.md`
- **Architecture**: `docs/architecture/`
- **Fixes**: `docs/fixes/`

---

## 🎯 For Different Users

### 👨‍💻 Developers
1. Read [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
2. Check [docs/architecture/](docs/architecture/)
3. Review [src/](src/) source code
4. Run tests: `python -m pytest tests/`

### 👥 Data Scientists
1. Read [docs/QUICKSTART.md](docs/QUICKSTART.md)
2. Run pipeline: `./run_project.sh medium`
3. Check [data/processed/](data/processed/) for CSVs
4. See [docs/RUN_PROJECT_GUIDE.md](docs/RUN_PROJECT_GUIDE.md)

### 📊 Business Analysts
1. Read [README.md](README.md)
2. See [powerbi/POWERBI_GUIDE.md](powerbi/POWERBI_GUIDE.md)
3. Connect Power BI to database
4. Check [docs/interview/](docs/interview/) for presentations

### 🆕 New Contributors
1. Read [README.md](README.md)
2. Run [scripts/setup/verify_setup.py](scripts/setup/verify_setup.py)
3. Read [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
4. Check [docs/](docs/) for all guides

---

## 🔍 Finding Specific Information

| I want to... | Go to... |
|--------------|----------|
| Get started quickly | [docs/QUICKSTART.md](docs/QUICKSTART.md) |
| Understand the project | [README.md](README.md) |
| Run the pipeline | [docs/RUN_PROJECT_GUIDE.md](docs/RUN_PROJECT_GUIDE.md) |
| Fix an issue | [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) |
| See all commands | [CHEATSHEET.sh](CHEATSHEET.sh) |
| Understand file structure | [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) |
| Find a script | [scripts/README.md](scripts/README.md) |
| Read documentation index | [docs/README.md](docs/README.md) |
| Connect Power BI | [powerbi/POWERBI_GUIDE.md](powerbi/POWERBI_GUIDE.md) |
| Prepare for interview | [docs/interview/](docs/interview/) |

---

## 📞 Quick Help

### Stuck?
1. Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Run diagnostics: `python scripts/setup/verify_setup.py`
3. Verify database: `./scripts/utilities/verify_database.sh`

### Need Commands?
```bash
./CHEATSHEET.sh              # Show all commands
./run_project.sh help        # Pipeline help
python -m src.main --help    # Python module help
```

### Looking for Files?
```bash
cat QUICK_STRUCTURE_GUIDE.md # Quick reference
cat PROJECT_STRUCTURE.md     # Complete structure
tree -L 2                    # Visual tree (if installed)
```

---

## 🎓 Learning Path

### Beginner
1. [README.md](README.md)
2. [docs/QUICKSTART.md](docs/QUICKSTART.md)
3. [CHEATSHEET.sh](CHEATSHEET.sh)
4. Run: `./run_project.sh small`

### Intermediate
1. [docs/RUN_PROJECT_GUIDE.md](docs/RUN_PROJECT_GUIDE.md)
2. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
3. [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)
4. Explore [scripts/](scripts/)

### Advanced
1. [docs/architecture/](docs/architecture/)
2. [docs/technology/](docs/technology/)
3. Review [src/](src/) code
4. [docs/interview/TECHNICAL_QA.md](docs/interview/TECHNICAL_QA.md)

---

## ✅ Checklist for New Users

- [ ] Read [README.md](README.md)
- [ ] Review [docs/QUICKSTART.md](docs/QUICKSTART.md)
- [ ] Configure `config/db_config.yml`
- [ ] Run `python scripts/setup/verify_setup.py`
- [ ] Execute `./run_project.sh small`
- [ ] Check `./scripts/utilities/verify_database.sh`
- [ ] Review [docs/](docs/) for more info

---

## 🌟 Pro Tips

1. **Bookmark** [CHEATSHEET.sh](CHEATSHEET.sh) for quick commands
2. **Always run** from project root directory
3. **Check** [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) first
4. **Use** `./run_project.sh` for easiest execution
5. **Read** [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) to understand layout

---

## 📋 All Documentation Files

```
📄 README.md                        # Main documentation
📄 PROJECT_STRUCTURE.md             # Structure guide
📄 QUICK_STRUCTURE_GUIDE.md         # Quick reference
📄 NAVIGATION.md                    # This file
📄 CHEATSHEET.sh                    # Command reference
📄 REORGANIZATION_COMPLETE.md       # Reorganization summary
📄 CHECKLIST.md                     # Completion checklist

📂 docs/
   📄 README.md                     # Documentation index
   📄 QUICKSTART.md                 # Quick start guide
   📄 QUICK_REFERENCE.md            # Command reference
   📄 RUN_PROJECT_GUIDE.md          # Complete run guide
   📄 TROUBLESHOOTING.md            # Troubleshooting
   📂 architecture/                 # System design
   📂 technology/                   # Tech stack
   📂 interview/                    # Interview prep
   📂 fixes/                        # Historical fixes

📂 scripts/
   📄 README.md                     # Scripts documentation

📂 powerbi/
   📄 POWERBI_GUIDE.md             # Power BI setup
```

---

## 🚀 Ready to Start?

```bash
# Quick start command:
./run_project.sh small

# Or read the quick start guide:
cat docs/QUICKSTART.md
```

**Happy analyzing! 🎉**

