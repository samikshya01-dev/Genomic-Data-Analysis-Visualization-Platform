#!/bin/bash
# Quick Run Cheat Sheet Script
# Shows all ways to run the project

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        GENOMIC DATA ANALYSIS PLATFORM - RUN GUIDE            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝


❌ WRONG - DON'T DO THIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  python main.py --full
  python3 main.py --full

  ✗ Error: main.py is NOT in root directory
  ✗ Error: It's in src/main.py


✅ CORRECT WAYS TO RUN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

METHOD 1: Use Run Script (EASIEST) ⭐ RECOMMENDED
────────────────────────────────────────────────

  # First time only: make executable
  chmod +x run_project.sh

  # Then run:
  ./run_project.sh test      # Quick test (30s)
  ./run_project.sh small     # 5K rows (5-10min)
  ./run_project.sh medium    # 50K rows (10-20min)
  ./run_project.sh full      # All data (30-60min)


METHOD 2: Python Module
────────────────────────────────────────────────

  python -m src.main --help
  python -m src.main --full --max-rows 5000 --skip-enrichment
  python -m src.main --full --max-rows 1000
  python -m src.main --extract
  python -m src.main --transform
  python -m src.main --load
  python -m src.main --analyze


METHOD 3: Launcher Script
────────────────────────────────────────────────

  python run_pipeline.py --full
  python run_pipeline.py --full --max-rows 5000
  python run_pipeline.py --help


METHOD 4: Direct Path
────────────────────────────────────────────────

  python src/main.py --full
  python3 src/main.py --full --max-rows 5000
  python src/main.py --help


METHOD 5: Make Commands
────────────────────────────────────────────────

  make help           # Show all commands
  make test-run       # Quick test
  make full           # Full pipeline
  make extract        # Extract only
  make transform      # Transform only
  make load           # Load only
  make analyze        # Analyze only


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUICK EXAMPLES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Example 1: First Time (Recommended)
────────────────────────────────────────────────
  chmod +x run_project.sh
  ./run_project.sh test


Example 2: Quick Test Run
────────────────────────────────────────────────
  python -m src.main --full --max-rows 1000 --skip-enrichment


Example 3: Process 5,000 Variants
────────────────────────────────────────────────
  ./run_project.sh small


Example 4: Full Production Run
────────────────────────────────────────────────
  ./run_project.sh full


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMMAND OPTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Using run_project.sh:
────────────────────────────────────────────────
  test       Quick test (1K rows, 30s)
  small      Small run (5K rows, 5-10min)
  medium     Medium run (50K rows, 10-20min)
  full       Full pipeline (all data)
  extract    Download VCF only
  transform  Parse VCF only
  load       Load to database only
  analyze    Run analysis only
  verify     Verify setup
  clean      Clean generated files
  tests      Run test suite
  help       Show help


Using Python Module:
────────────────────────────────────────────────
  --help              Show help
  --full              Run full pipeline
  --extract           Extract VCF only
  --transform         Transform only
  --load              Load to DB only
  --analyze           Analysis only
  --max-rows N        Limit to N rows
  --skip-enrichment   Skip enrichment
  --skip-analysis     Skip analysis
  --force-download    Force re-download
  --drop-existing     Drop existing tables


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ⭐ EASIEST:   ./run_project.sh test

  ⭐ RELIABLE:  python -m src.main --full --max-rows 5000

  ⭐ FLEXIBLE:  python src/main.py --full --max-rows 10000


Remember: main.py is in src/ directory, not root!


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For more help:
  cat docs/RUN_PROJECT_GUIDE.md
  cat docs/QUICK_REFERENCE.md
  cat docs/QUICKSTART.md
  ./run_project.sh help

Utility Scripts:
  ./scripts/utilities/verify_database.sh    # Check database status
  ./scripts/utilities/run_pipeline_now.sh   # Interactive pipeline runner
  python scripts/utilities/fix_database.py  # Fix database issues

EOF

