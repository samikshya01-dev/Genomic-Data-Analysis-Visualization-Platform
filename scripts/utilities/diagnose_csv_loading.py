#!/usr/bin/env python3
"""
Diagnose and fix CSV loading issue with column names
"""
import pandas as pd
import sys

print("=" * 80)
print("DIAGNOSE CSV LOADING ISSUE")
print("=" * 80)
print()

csv_path = "data/processed/variants.csv"

print(f"Reading CSV file: {csv_path}")
print()

# Test 1: Read just the header
print("[1] Reading header only...")
df_header = pd.read_csv(csv_path, nrows=0)
print(f"Column count: {len(df_header.columns)}")
print(f"Column names: {df_header.columns.tolist()}")
print()

# Check for duplicates
duplicates = df_header.columns[df_header.columns.duplicated()].tolist()
if duplicates:
    print(f"⚠ DUPLICATE COLUMNS FOUND: {duplicates}")
else:
    print("✓ No duplicate column names in header")
print()

# Test 2: Read first chunk
print("[2] Reading first 1000 rows...")
try:
    df_chunk = pd.read_csv(csv_path, nrows=1000)
    print(f"✓ Successfully read {len(df_chunk)} rows")
    print(f"Columns in chunk: {len(df_chunk.columns)}")

    if len(df_chunk.columns) != len(df_header.columns):
        print(f"⚠ WARNING: Column count mismatch!")
        print(f"  Header: {len(df_header.columns)}")
        print(f"  Chunk: {len(df_chunk.columns)}")

    # Check chunk columns
    chunk_duplicates = df_chunk.columns[df_chunk.columns.duplicated()].tolist()
    if chunk_duplicates:
        print(f"⚠ DUPLICATES IN CHUNK: {chunk_duplicates}")

    print()
    print("First row sample:")
    print(df_chunk.iloc[0][['chromosome', 'position', 'variant_id']].to_dict())

except Exception as e:
    print(f"✗ Error reading chunk: {e}")
    sys.exit(1)

print()

# Test 3: Read with explicit dtype
print("[3] Reading with chunksize (database loading simulation)...")
try:
    chunk_iter = pd.read_csv(csv_path, chunksize=10000)
    first_chunk = next(chunk_iter)
    print(f"✓ Successfully read first chunk: {len(first_chunk)} rows")
    print(f"Columns: {len(first_chunk.columns)}")
    print(f"Column names: {first_chunk.columns.tolist()[:5]}...")

    # Check if this chunk has issues
    if any('_m' in str(col) for col in first_chunk.columns):
        print("⚠ WARNING: Found '_m' suffix in column names!")
        print("This indicates duplicate column handling by pandas")
        problem_cols = [col for col in first_chunk.columns if '_m' in str(col)]
        print(f"Problem columns: {problem_cols[:10]}")
    else:
        print("✓ No '_m' suffixes found in column names")

except Exception as e:
    print(f"✗ Error with chunked reading: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)

