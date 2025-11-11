#!/bin/bash
# Quick fix script to populate all database tables

set -e  # Exit on error

echo "================================================================================"
echo "DATABASE FIX SCRIPT - Populating Empty Tables"
echo "================================================================================"
echo ""

# Navigate to project directory
cd "/Users/biswajitsahu/Desktop/marketing-campaign-analysis/Genomic Data Analysis Visualization Platform"

echo "[1/5] Checking VCF file..."
if [ -f "data/raw/homo_sapiens-chrX.vcf" ]; then
    echo "✓ VCF file exists"
else
    echo "✗ VCF file not found. Please run extraction first."
    exit 1
fi

echo ""
echo "[2/5] Running TRANSFORMATION phase (creating CSV files)..."
python -m src.main --transform
if [ $? -eq 0 ]; then
    echo "✓ Transformation complete"
else
    echo "✗ Transformation failed"
    exit 1
fi

echo ""
echo "[3/5] Running ENRICHMENT phase (creating drug annotations)..."
python -m src.main --enrich
if [ $? -eq 0 ]; then
    echo "✓ Enrichment complete"
else
    echo "✗ Enrichment failed (this is optional, continuing...)"
fi

echo ""
echo "[4/5] LOADING data to database..."
python -m src.main --load --drop-existing
if [ $? -eq 0 ]; then
    echo "✓ Loading complete"
else
    echo "✗ Loading failed"
    exit 1
fi

echo ""
echo "[5/5] Verifying table counts..."
mysql -u root genomic_analysis -e "
SELECT 'variants' as table_name, COUNT(*) as row_count FROM variants
UNION ALL
SELECT 'genes', COUNT(*) FROM genes
UNION ALL
SELECT 'drug_annotations', COUNT(*) FROM drug_annotations
UNION ALL
SELECT 'mutation_summary', COUNT(*) FROM mutation_summary;
" 2>/dev/null || echo "Note: Install mysql client to verify counts"

echo ""
echo "================================================================================"
echo "✓ DATABASE FIX COMPLETE!"
echo "================================================================================"
echo ""
echo "All tables should now be populated with data."
echo "You can now use Power BI to connect and visualize the data."

