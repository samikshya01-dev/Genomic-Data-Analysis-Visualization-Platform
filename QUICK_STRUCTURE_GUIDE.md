# Quick Reference - New Project Structure

## 📂 Where Everything Is Now

### 🏠 Root Directory (Clean!)
```
├── README.md              # Start here
├── PROJECT_STRUCTURE.md   # Complete structure guide
├── CHEATSHEET.sh         # Command reference
├── run_project.sh        # Main runner
├── Makefile              # Build commands
├── requirements.txt      # Dependencies
└── .gitignore           # Git rules
```

### 🔧 Utility Scripts → `scripts/`

**Database & Pipeline**: `scripts/utilities/`
- `verify_database.sh` - Check database status
- `fix_database.py` - Fix database issues
- `populate_sample_data.py` - Add sample data
- `run_pipeline_now.sh` - Interactive runner
- `quick_fix.sh` - Quick pipeline fix

**Setup**: `scripts/setup/`
- `verify_setup.py` - Verify installation

### 📚 Documentation → `docs/`

**User Guides**: `docs/`
- `QUICKSTART.md` - 5-minute start
- `RUN_PROJECT_GUIDE.md` - Complete guide
- `QUICK_REFERENCE.md` - Command reference
- `TROUBLESHOOTING.md` - Fix issues
- `README.md` - Documentation index

**Technical**: `docs/`
- `architecture/` - System design
- `technology/` - Tech stack
- `interview/` - Interview prep

**Historical**: `docs/fixes/`
- Fix documentation (reference only)

### 💻 Source Code → `src/`
```
src/
├── main.py          # Pipeline orchestrator
├── etl/            # Extract, Transform, Load
├── analysis/       # Data analysis
└── utils/          # Utilities
```

### 📊 Data → `data/`
```
data/
├── raw/            # VCF files (gitignored)
├── processed/      # CSV files (gitignored)
└── logs/           # Logs (gitignored)
```

---

## 🎯 Quick Commands

### Run Pipeline
```bash
./run_project.sh small              # 5K variants
./scripts/utilities/run_pipeline_now.sh  # Interactive
python -m src.main --full --max-rows 5000
```

### Verify & Fix
```bash
./scripts/utilities/verify_database.sh   # Check status
python scripts/utilities/fix_database.py # Fix issues
python scripts/setup/verify_setup.py     # Verify setup
```

### Documentation
```bash
cat README.md                       # Main docs
cat docs/QUICKSTART.md             # Quick start
cat docs/RUN_PROJECT_GUIDE.md      # Full guide
cat PROJECT_STRUCTURE.md           # Structure
```

---

## 📍 Path Updates

| Old | New |
|-----|-----|
| `./fix_database.py` | `./scripts/utilities/fix_database.py` |
| `./verify_database.sh` | `./scripts/utilities/verify_database.sh` |
| `./QUICKSTART.md` | `./docs/QUICKSTART.md` |

---

## 🗂️ File Organization

**Keep at Root:**
- ✅ README, LICENSE, requirements.txt
- ✅ Main runners (run_project.sh)
- ✅ Configuration (Makefile, CHEATSHEET.sh)

**Move to scripts/:**
- ✅ Utility scripts
- ✅ Setup scripts
- ✅ Helper tools

**Move to docs/:**
- ✅ User guides
- ✅ Technical docs
- ✅ References

**Move to src/:**
- ✅ Python source code
- ✅ Main modules
- ✅ Package code

---

## 🎨 Directory Colors (Convention)

- 📂 **config/** - Blue (configuration)
- 📂 **data/** - Yellow (data files)
- 📂 **src/** - Green (source code)
- 📂 **scripts/** - Cyan (utilities)
- 📂 **docs/** - Purple (documentation)
- 📂 **tests/** - Red (test code)

---

## ✨ Benefits

1. **Clean Root** - Only essential files
2. **Organized** - Logical grouping
3. **Professional** - Industry standard
4. **Documented** - Clear guides
5. **Maintainable** - Easy to update

---

**This structure is now production-ready! 🚀**

