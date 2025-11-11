#!/usr/bin/env python3
"""
Fix corrupted variants.csv file with duplicate headers
"""
import sys
import os

print("=" * 80)
print("FIX CORRUPTED VARIANTS CSV FILE")
print("=" * 80)
print()

csv_path = "data/processed/variants.csv"

if not os.path.exists(csv_path):
    print(f"✗ File not found: {csv_path}")
    sys.exit(1)

print(f"Checking file: {csv_path}")
file_size = os.path.getsize(csv_path) / (1024**3)  # GB
print(f"File size: {file_size:.2f} GB")
print()

# Count lines and find duplicate headers
print("Analyzing file...")
header = None
duplicate_headers = []
line_count = 0

with open(csv_path, 'r') as f:
    for i, line in enumerate(f):
        line_count += 1
        if i == 0:
            header = line.strip()
            print(f"Header: {header[:100]}...")
        elif line.strip() == header:
            duplicate_headers.append(i)
            if len(duplicate_headers) <= 5:
                print(f"⚠ Found duplicate header at line {i+1}")

print()
print(f"Total lines: {line_count:,}")
print(f"Duplicate headers found: {len(duplicate_headers)}")
print()

if len(duplicate_headers) == 0:
    print("✓ No duplicate headers found. File is clean.")
    sys.exit(0)

# Fix the file
print("Fixing file by removing duplicate headers...")
fixed_path = csv_path + ".fixed"
removed_count = 0

with open(csv_path, 'r') as fin, open(fixed_path, 'w') as fout:
    for i, line in enumerate(fin):
        if i == 0:
            # Keep first header
            fout.write(line)
        elif line.strip() == header.strip():
            # Skip duplicate headers
            removed_count += 1
        else:
            # Keep data lines
            fout.write(line)

print(f"✓ Removed {removed_count} duplicate headers")
print()

# Replace original with fixed
print("Replacing original file with fixed version...")
import shutil
shutil.move(csv_path, csv_path + ".backup")
shutil.move(fixed_path, csv_path)

print(f"✓ Fixed file saved as: {csv_path}")
print(f"✓ Backup saved as: {csv_path}.backup")
print()

# Verify
print("Verifying fixed file...")
with open(csv_path, 'r') as f:
    first_line = f.readline().strip()
    data_lines = 0
    for i, line in enumerate(f):
        if line.strip() == first_line:
            print(f"✗ Still found duplicate at line {i+2}")
            break
        data_lines += 1
        if data_lines >= 10:
            break
    else:
        print("✓ File verified - no duplicate headers in first 10 data rows")

print()
print("=" * 80)
print("✓ CSV FILE FIXED!")
print("=" * 80)
print()
print("You can now run the loading phase:")
print("  python -m src.main --load --drop-existing")

