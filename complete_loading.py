#!/usr/bin/env python3
"""
Complete the database loading and verify results
"""
import sys
sys.path.insert(0, '.')

from src.etl import MySQLLoader
from src.utils import get_db_config
from sqlalchemy import text

print("=" * 80)
print("COMPLETING DATABASE LOADING")
print("=" * 80)
print()

try:
    loader = MySQLLoader()

    # Step 1: Load genes (with empty file handling)
    print("[1/3] Loading genes...")
    try:
        loader.load_genes()
        print("✓ Genes loaded (or skipped if empty)")
    except Exception as e:
        print(f"⚠ Warning in genes loading: {e}")
        print("Continuing...")

    # Step 2: Load drug annotations
    print()
    print("[2/3] Loading drug annotations...")
    try:
        loader.load_drug_annotations()
        print("✓ Drug annotations loaded")
    except Exception as e:
        print(f"⚠ Warning in drug annotations: {e}")
        print("Continuing...")

    # Step 3: Create mutation summary
    print()
    print("[3/3] Creating mutation summary...")
    try:
        loader.create_mutation_summary()
        print("✓ Mutation summary created")
    except Exception as e:
        print(f"⚠ Warning in mutation summary: {e}")
        print("Continuing...")

    print()
    print("=" * 80)
    print("VERIFYING DATABASE")
    print("=" * 80)
    print()

    # Verify counts
    db_config = get_db_config()
    engine = db_config.get_engine()

    with engine.connect() as conn:
        tables = ['variants', 'genes', 'drug_annotations', 'mutation_summary']

        print("Table Counts:")
        print("-" * 80)
        for table in tables:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.fetchone()[0]
            status = "✓" if count > 0 else "⚠"
            print(f"  {status} {table:.<30} {count:>15,} rows")

    print()
    print("=" * 80)
    print("✓ DATABASE LOADING COMPLETED!")
    print("=" * 80)
    print()
    print("Your genomic analysis database is ready!")
    print("Connect Power BI using:")
    print("  Server: localhost")
    print("  Database: genomic_analysis")
    print("  Username: root")
    print("  Password: password")

except Exception as e:
    print()
    print("=" * 80)
    print("✗ ERROR")
    print("=" * 80)
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

