#!/usr/bin/env python3
"""
Emergency Ultra-Fast MongoDB Loader
Bypasses all overhead for maximum speed
"""
import pandas as pd
import numpy as np
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import time
import os

print("="*80)
print("EMERGENCY ULTRA-FAST LOADER")
print("="*80)
print()

# Configuration
CSV_PATH = "data/processed/variants.csv"
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "genomic_analysis"
COLLECTION_NAME = "variants"
CHUNK_SIZE = 500000  # 500k rows per chunk

# Connect to MongoDB with RADICAL settings
print("🔌 Connecting to MongoDB...")
client = MongoClient(
    MONGO_URI,
    w=0,  # No acknowledgment (fastest)
    journal=False,
    maxPoolSize=200,
    minPoolSize=50,
    retryWrites=False,
    serverSelectionTimeoutMS=5000,
    socketTimeoutMS=120000  # 2 minutes
)

db = client[DB_NAME]
collection = db[COLLECTION_NAME]

print(f"✓ Connected to {DB_NAME}.{COLLECTION_NAME}")
print()

# Get file info
file_size_mb = os.path.getsize(CSV_PATH) / (1024 * 1024)
print(f"📁 File: {CSV_PATH}")
print(f"📊 Size: {file_size_mb:.1f} MB")
print(f"📦 Chunk size: {CHUNK_SIZE:,} rows")
print()

# Confirm
response = input("⚠️  This will DROP existing data. Continue? (yes/no): ")
if response.lower() != 'yes':
    print("Cancelled.")
    exit(0)

# Drop existing data
print("\n🗑️  Dropping existing collection...")
collection.drop()
print("✓ Collection dropped")
print()

# Load data
print("="*80)
print("LOADING DATA - MAXIMUM SPEED MODE")
print("="*80)
print()

start_time = time.time()
total_rows = 0
chunk_num = 0

# Read CSV in chunks
print("📖 Reading CSV in chunks...")
chunk_iterator = pd.read_csv(
    CSV_PATH,
    chunksize=CHUNK_SIZE,
    low_memory=False,
    engine='c',
    na_filter=False  # Disable NA filtering for speed
)

for chunk in chunk_iterator:
    chunk_num += 1
    chunk_start = time.time()

    # Convert to dict
    documents = chunk.to_dict('records')

    # Bulk insert
    try:
        result = collection.insert_many(
            documents,
            ordered=False
        )
        inserted = len(result.inserted_ids)
    except BulkWriteError as e:
        inserted = e.details['nInserted']

    total_rows += inserted
    chunk_duration = time.time() - chunk_start

    # Progress
    elapsed = time.time() - start_time
    rate = total_rows / elapsed if elapsed > 0 else 0
    print(f"✓ Chunk {chunk_num}: {inserted:,} rows in {chunk_duration:.1f}s | Total: {total_rows:,} | Rate: {rate:,.0f}/sec")

# Final stats
total_duration = time.time() - start_time
final_rate = total_rows / total_duration

print()
print("="*80)
print("COMPLETE!")
print("="*80)
print(f"✓ Loaded: {total_rows:,} variants")
print(f"✓ Time: {total_duration/60:.1f} minutes ({total_duration:.0f} seconds)")
print(f"✓ Average speed: {final_rate:,.0f} variants/second")
print()

# Verify
count = collection.count_documents({})
print(f"🔍 Verification: {count:,} documents in MongoDB")
print()

if count == total_rows:
    print("✅ SUCCESS - All data loaded correctly!")
else:
    print(f"⚠️  WARNING - Count mismatch: {total_rows:,} inserted vs {count:,} in DB")

client.close()

