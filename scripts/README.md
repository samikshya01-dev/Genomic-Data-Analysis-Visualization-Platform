# Scripts Directory

Utility and setup scripts for the Genomic Data Analysis platform.

## Directory Structure

```
scripts/
├── utilities/          # Utility scripts for database and pipeline management
│   ├── fix_database.py
│   ├── populate_sample_data.py
│   ├── quick_fix.sh
│   ├── run_pipeline_now.sh
│   └── verify_database.sh
└── setup/             # Initial setup and verification scripts
    └── verify_setup.py
```

## Utilities

### Database Management

**verify_database.sh**
- Quick verification of database status
- Shows table counts and sample data
- Usage: `./scripts/utilities/verify_database.sh`

**populate_sample_data.py**
- Populates genes and drug_annotations tables with sample data
- Useful when VCF data doesn't have gene information
- Usage: `python scripts/utilities/populate_sample_data.py`

**fix_database.py**
- Automated database fix script
- Runs transformation → enrichment → loading phases
- Usage: `python scripts/utilities/fix_database.py`

### Pipeline Shortcuts

**run_pipeline_now.sh**
- Interactive pipeline runner with dataset size selection
- Automatically checks MySQL status
- Usage: `./scripts/utilities/run_pipeline_now.sh`

**quick_fix.sh**
- Quick pipeline execution for fixing database issues
- Runs all phases with error handling
- Usage: `./scripts/utilities/quick_fix.sh`

## Setup

**verify_setup.py**
- Verifies Python environment and dependencies
- Checks configuration files
- Tests database connection
- Usage: `python scripts/setup/verify_setup.py`

## Usage Examples

```bash
# Verify database status
./scripts/utilities/verify_database.sh

# Run interactive pipeline
./scripts/utilities/run_pipeline_now.sh

# Populate sample data
python scripts/utilities/populate_sample_data.py

# Verify setup
python scripts/setup/verify_setup.py
```

## Notes

- All scripts should be run from the project root directory
- Make sure virtual environment is activated before running Python scripts
- Shell scripts are executable (chmod +x already applied)

