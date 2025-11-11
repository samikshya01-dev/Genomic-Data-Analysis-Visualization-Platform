#!/bin/bash
# Quick script to test the memory fix

echo "=========================================================================="
echo "Testing Memory-Optimized Pipeline"
echo "=========================================================================="
echo ""

cd "/Users/biswajitsahu/Desktop/marketing-campaign-analysis/Genomic Data Analysis Visualization Platform"

echo "This will test the memory optimization in stages:"
echo ""
echo "1. Small dataset (5K variants) - ~30 seconds"
echo "2. Medium dataset (50K variants) - ~2 minutes"
echo "3. Large sample (500K variants) - ~10 minutes"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Test 1: Small
echo ""
echo "=========================================================================="
echo "TEST 1: Small Dataset (5,000 variants)"
echo "=========================================================================="
./run_project.sh small
if [ $? -eq 0 ]; then
    echo "✓ Small dataset test PASSED"
else
    echo "✗ Small dataset test FAILED"
    exit 1
fi

# Test 2: Medium
echo ""
echo "=========================================================================="
echo "TEST 2: Medium Dataset (50,000 variants)"
echo "=========================================================================="
./run_project.sh medium
if [ $? -eq 0 ]; then
    echo "✓ Medium dataset test PASSED"
else
    echo "✗ Medium dataset test FAILED"
    exit 1
fi

# Test 3: Large sample
echo ""
echo "=========================================================================="
echo "TEST 3: Large Sample (500,000 variants)"
echo "=========================================================================="
python -m src.main --transform --max-rows 500000
if [ $? -eq 0 ]; then
    echo "✓ Large sample test PASSED"
    echo ""
    echo "All tests passed! Memory optimization is working correctly."
    echo ""
    echo "You can now run the full dataset:"
    echo "  ./run_project.sh full"
    echo ""
    echo "This will process all ~37M variants in about 15-20 minutes."
else
    echo "✗ Large sample test FAILED"
    exit 1
fi

echo ""
echo "=========================================================================="
echo "✓ ALL TESTS PASSED - Memory optimization working!"
echo "=========================================================================="

