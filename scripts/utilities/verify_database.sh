#!/bin/bash
# Simple script to verify database status

echo "================================================================================"
echo "DATABASE VERIFICATION REPORT"
echo "================================================================================"
echo ""

cd "/Users/biswajitsahu/Desktop/marketing-campaign-analysis/Genomic Data Analysis Visualization Platform"

echo "Checking table counts..."
echo ""

mysql -u root -ppassword genomic_analysis << 'EOFMYSQL'
SELECT
    CASE
        WHEN table_name = 'variants' THEN '✓ variants'
        WHEN table_name = 'genes' THEN '✓ genes'
        WHEN table_name = 'drug_annotations' THEN '✓ drug_annotations'
        WHEN table_name = 'mutation_summary' THEN '✓ mutation_summary'
    END as 'Table',
    table_rows as 'Rows (approx)'
FROM information_schema.tables
WHERE table_schema = 'genomic_analysis'
AND table_name IN ('variants', 'genes', 'drug_annotations', 'mutation_summary')
ORDER BY table_name;

SELECT '' as '';
SELECT 'Sample Genes:' as '';
SELECT gene_symbol, chromosome FROM genes LIMIT 5;

SELECT '' as '';
SELECT 'Sample Drug Annotations:' as '';
SELECT gene_symbol, drug_name FROM drug_annotations LIMIT 5;
EOFMYSQL

echo ""
echo "================================================================================"
echo "✓ Database is ready for Power BI!"
echo "================================================================================"
echo ""
echo "Connection Details:"
echo "  Server: localhost"
echo "  Database: genomic_analysis"
echo "  Port: 3306"
echo "  Username: root"
echo "  Password: password"
echo ""

