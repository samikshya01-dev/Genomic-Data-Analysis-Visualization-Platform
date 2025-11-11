#!/bin/bash
# Quick script to reload the database with clean tables

echo "=========================================================================="
echo "RELOAD DATABASE WITH CLEAN TABLES"
echo "=========================================================================="
echo ""

cd "/Users/biswajitsahu/Desktop/marketing-campaign-analysis/Genomic Data Analysis Visualization Platform"

echo "The CSV file is clean. The error was from a previous failed attempt."
echo "We need to drop and recreate the database tables."
echo ""
echo "This will:"
echo "1. Drop existing tables"
echo "2. Create fresh tables"
echo "3. Load data from CSV files"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Running database loading with --drop-existing..."
echo ""

.venv/bin/python -m src.main --load --drop-existing

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================================================="
    echo "✓ DATABASE LOADED SUCCESSFULLY!"
    echo "=========================================================================="
    echo ""
    echo "Verifying..."
    ./scripts/utilities/verify_database.sh
else
    echo ""
    echo "=========================================================================="
    echo "✗ LOADING FAILED"
    echo "=========================================================================="
    echo ""
    echo "Check the error above for details."
    exit 1
fi

