#!/bin/bash
# Genomic Data Analysis Pipeline - Main Runner Script
# Optimized with MongoDB for 3-5x faster performance
# Author: Biswajit Sahu
# Last Updated: November 10, 2025

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Banner
print_banner() {
    echo ""
    echo "================================================================"
    echo "     GENOMIC DATA ANALYSIS & VISUALIZATION PLATFORM"
    echo "             Powered by MongoDB (3-5x faster!)"
    echo "================================================================"
    echo ""
}

# Print colored message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if virtual environment is activated
check_venv() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_warning "Virtual environment not activated!"
        if [[ -d ".venv" ]]; then
            print_info "Activating virtual environment..."
            source .venv/bin/activate
            print_success "Virtual environment activated"
        else
            print_error "Virtual environment not found. Run: python3 -m venv .venv"
            exit 1
        fi
    else
        print_success "Virtual environment is active"
    fi
}

# Check dependencies
check_dependencies() {
    print_info "Checking dependencies..."
    if ! python -c "import pandas, numpy, pymongo, vcfpy" 2>/dev/null; then
        print_error "Dependencies not installed!"
        print_info "Installing dependencies..."
        pip install -r requirements.txt
    fi
    print_success "All dependencies installed"
}

# Check MongoDB status
check_mongodb() {
    print_info "Checking MongoDB status..."
    if ! pgrep -x "mongod" > /dev/null; then
        print_warning "MongoDB is not running!"
        print_info "Starting MongoDB..."
        if command -v brew &> /dev/null; then
            brew services start mongodb-community
            sleep 2
            if pgrep -x "mongod" > /dev/null; then
                print_success "MongoDB started successfully"
            else
                print_error "Failed to start MongoDB. Please start it manually:"
                print_info "  brew services start mongodb-community"
                exit 1
            fi
        else
            print_error "Please start MongoDB manually:"
            print_info "  sudo systemctl start mongod"
            exit 1
        fi
    else
        print_success "MongoDB is running"
    fi
}

# Show help
show_help() {
    cat << EOF
Usage: ./run_project.sh [OPTION]

Options:
  help              Show this help message
  test              Run quick test (1000 variants, ~30 seconds)
  small             Run with 5,000 variants (~1-2 minutes)
  medium            Run with 50,000 variants (~5-10 minutes)
  full              Run full pipeline (~30-45 minutes with MongoDB)
  extract           Extract VCF data only
  transform         Transform VCF data only
  load              Load data to MongoDB only
  analyze           Run analysis only
  verify            Verify setup and MongoDB connection
  clean             Clean generated files
  tests             Run test suite
  status            Show MongoDB and database status

MongoDB Info:
  - Database: genomic_analysis
  - Connection: mongodb://localhost:27017/
  - Performance: 3-5x faster than MySQL
  - Batch size: 50,000 documents

Examples:
  ./run_project.sh test         # Quick test (1K variants)
  ./run_project.sh small        # Small dataset (5K variants)
  ./run_project.sh full         # Full pipeline (44M variants)
  ./run_project.sh status       # Check MongoDB status
  ./run_project.sh verify       # Verify all systems

EOF
}

# Run quick test
run_test() {
    print_banner
    check_mongodb
    print_info "Running quick test (1000 variants)..."
    print_info "Duration: ~30 seconds"
    echo ""

    python3 src/main.py --full --max-rows 1000 --skip-enrichment

    echo ""
    print_success "Test completed successfully!"
    print_info "Check MongoDB: mongosh genomic_analysis --eval 'db.variants.countDocuments()'"
    print_info "Check results in: data/processed/"
}

# Run small dataset
run_small() {
    print_banner
    check_mongodb
    print_info "Running with 5,000 variants..."
    print_info "Duration: ~1-2 minutes (with MongoDB optimization)"
    echo ""

    python3 src/main.py --full --max-rows 5000 --skip-enrichment

    echo ""
    print_success "Pipeline completed successfully!"
    print_info "Database loaded with 5,000 variants"
    print_info "View data: mongosh genomic_analysis --eval 'db.variants.find().limit(5).pretty()'"
}

# Run medium dataset
run_medium() {
    print_banner
    check_mongodb
    print_info "Running with 50,000 variants..."
    print_info "Duration: ~5-10 minutes (with MongoDB optimization)"
    echo ""

    python3 src/main.py --full --max-rows 50000 --skip-enrichment

    echo ""
    print_success "Pipeline completed successfully!"
    print_info "Database loaded with 50,000 variants"
}

# Run full pipeline
run_full() {
    print_banner
    check_mongodb
    print_warning "Running FULL pipeline (44M variants)..."
    print_info "This will process the entire chromosome X"
    print_info "Duration: ~30-45 minutes (with MongoDB - 3-5x faster!)"
    print_info "Previous MySQL time: ~2.5 hours"
    echo ""

    read -p "Continue? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_time=$(date +%s)

        python3 src/main.py --full

        end_time=$(date +%s)
        duration=$((end_time - start_time))
        minutes=$((duration / 60))
        seconds=$((duration % 60))

        echo ""
        print_success "Full pipeline completed successfully!"
        print_success "Total time: ${minutes}m ${seconds}s"
        print_info "Check MongoDB: mongosh genomic_analysis"
    else
        print_info "Cancelled"
        exit 0
    fi
}

# Extract only
run_extract() {
    print_banner
    print_info "Extracting VCF data from Ensembl..."
    echo ""

    python3 src/main.py --extract

    echo ""
    print_success "Extraction completed!"
    print_info "VCF file saved to: data/raw/"
}

# Transform only
run_transform() {
    print_banner
    print_info "Transforming VCF data..."
    echo ""

    if [[ ! -f "data/raw/homo_sapiens-chrX.vcf" ]] && [[ ! -f "data/raw/homo_sapiens-chrX.vcf.gz" ]]; then
        print_error "VCF file not found! Run extract first."
        exit 1
    fi

    python3 src/main.py --transform --max-rows 10000

    echo ""
    print_success "Transformation completed!"
    print_info "Data saved to: data/processed/"
}

# Load only
run_load() {
    print_banner
    check_mongodb
    print_info "Loading data to MongoDB..."
    echo ""

    if [[ ! -f "data/processed/variants.csv" ]]; then
        print_error "Processed data not found! Run transform first."
        exit 1
    fi

    python3 src/main.py --load

    echo ""
    print_success "Data loaded to MongoDB successfully!"
    print_info "View data: mongosh genomic_analysis"
}

# Analyze only
run_analyze() {
    print_banner
    print_info "Running analysis..."
    echo ""

    python3 src/main.py --analyze

    echo ""
    print_success "Analysis completed!"
    print_info "Reports saved to: data/processed/"
}

# Verify setup
run_verify() {
    print_banner
    print_info "Verifying setup..."
    echo ""

    python verify_setup.py
}

# Clean generated files
run_clean() {
    print_banner
    print_warning "This will remove all generated files (logs, processed data, VCF files)"
    echo ""

    read -p "Continue? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning..."

        # Remove logs
        rm -f data/logs/*.log
        print_success "Removed log files"

        # Remove processed data
        rm -f data/processed/*.csv
        rm -f data/processed/*.txt
        print_success "Removed processed data"

        # Remove raw VCF files
        rm -f data/raw/*.vcf
        rm -f data/raw/*.vcf.gz
        print_success "Removed raw VCF files"

        # Remove Python cache
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
        find . -type f -name "*.pyc" -delete 2>/dev/null
        print_success "Removed Python cache"

        echo ""
        print_success "Cleanup completed!"
    else
        print_info "Cancelled"
    fi
}

# Run tests
run_tests() {
    print_banner
    print_info "Running test suite..."
    echo ""

    python -m pytest tests/ -v --tb=short

    echo ""
    print_success "All tests completed!"
}

# Show MongoDB status
show_status() {
    print_banner
    print_info "System Status Check"
    echo ""

    # Check MongoDB
    if pgrep -x "mongod" > /dev/null; then
        print_success "MongoDB is running"
    else
        print_error "MongoDB is not running"
        print_info "Start with: brew services start mongodb-community"
    fi

    # Check Python dependencies
    if python -c "import pymongo" 2>/dev/null; then
        print_success "pymongo installed"
    else
        print_error "pymongo not installed"
        print_info "Install with: pip install pymongo"
    fi

    # Check database
    if pgrep -x "mongod" > /dev/null; then
        echo ""
        print_info "Database Statistics:"
        python3 << 'PYEOF'
try:
    from src.etl.load_to_mysql import MongoDBLoader
    loader = MongoDBLoader()
    if loader.test_connection():
        counts = loader.get_collection_counts()
        print(f"  Database: {loader.db.name}")
        print(f"  Collections:")
        for coll, count in counts.items():
            print(f"    - {coll}: {count:,} documents")
except Exception as e:
    print(f"  Error: {e}")
PYEOF
    fi

    echo ""
    print_info "Virtual Environment:"
    if [[ -n "$VIRTUAL_ENV" ]]; then
        print_success "Active: $VIRTUAL_ENV"
    else
        print_warning "Not activated"
    fi

    echo ""
}

# Main execution
main() {
    # Check virtual environment
    check_venv

    # Get command
    COMMAND=${1:-help}

    case "$COMMAND" in
        help|--help|-h)
            print_banner
            show_help
            ;;
        test)
            check_dependencies
            run_test
            ;;
        small)
            check_dependencies
            run_small
            ;;
        medium)
            check_dependencies
            run_medium
            ;;
        full)
            check_dependencies
            run_full
            ;;
        extract)
            check_dependencies
            run_extract
            ;;
        transform)
            check_dependencies
            run_transform
            ;;
        load)
            check_dependencies
            run_load
            ;;
        analyze)
            check_dependencies
            run_analyze
            ;;
        verify)
            run_verify
            ;;
        clean)
            run_clean
            ;;
        tests)
            check_dependencies
            run_tests
            ;;
        status)
            show_status
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

