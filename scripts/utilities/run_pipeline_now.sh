#!/bin/bash
# Quick script to run the pipeline after MySQL is configured

echo "================================================================================"
echo "GENOMIC DATA ANALYSIS PIPELINE - Quick Run"
echo "================================================================================"
echo ""

cd "/Users/biswajitsahu/Desktop/marketing-campaign-analysis/Genomic Data Analysis Visualization Platform"

# Check if MySQL is running
echo "[1/3] Checking MySQL status..."
if pgrep -x mysqld > /dev/null; then
    echo "✓ MySQL is running"
else
    echo "⚠️  MySQL is not running"
    echo "Starting MySQL..."
    brew services start mysql
    sleep 3
fi

# Test MySQL connection
echo ""
echo "[2/3] Testing MySQL connection..."
if mysql -u root -e "SELECT 1;" > /dev/null 2>&1; then
    echo "✓ MySQL connection successful (no password)"
    # Update config to use empty password
    sed -i '' 's/password: ".*"/password: ""/' config/db_config.yml
elif mysql -u root -p"" -e "SELECT 1;" > /dev/null 2>&1; then
    echo "✓ MySQL connection successful (empty password)"
    sed -i '' 's/password: ".*"/password: ""/' config/db_config.yml
else
    echo "✗ MySQL connection failed"
    echo ""
    echo "Please update your MySQL password in config/db_config.yml"
    echo "Or set MySQL to allow root login without password:"
    echo "  mysql -u root -p"
    echo "  ALTER USER 'root'@'localhost' IDENTIFIED BY '';"
    echo "  FLUSH PRIVILEGES;"
    exit 1
fi

echo ""
echo "[3/3] Running pipeline..."
echo ""
echo "Choose dataset size:"
echo "  1) small  - 5,000 variants (fast, for testing)"
echo "  2) medium - 50,000 variants (recommended)"
echo "  3) full   - ~600,000 variants (complete dataset)"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        ./run_project.sh small
        ;;
    2)
        ./run_project.sh medium
        ;;
    3)
        ./run_project.sh full
        ;;
    *)
        echo "Invalid choice. Running with medium dataset..."
        ./run_project.sh medium
        ;;
esac

echo ""
echo "================================================================================"
echo "Pipeline execution completed!"
echo "================================================================================"
echo ""
echo "To verify results, run:"
echo "  mysql -u root genomic_analysis -e \"SELECT 'variants' as table_name, COUNT(*) as count FROM variants UNION ALL SELECT 'genes', COUNT(*) FROM genes UNION ALL SELECT 'drug_annotations', COUNT(*) FROM drug_annotations UNION ALL SELECT 'mutation_summary', COUNT(*) FROM mutation_summary;\""

