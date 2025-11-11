.PHONY: help setup install clean test run extract transform load analyze full

help:
	@echo "Genomic Data Analysis Platform - Available Commands"
	@echo "===================================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup        - Run automated setup (creates venv, installs deps)"
	@echo "  make install      - Install dependencies only"
	@echo "  make clean        - Clean generated files and cache"
	@echo ""
	@echo "Pipeline Commands:"
	@echo "  make extract      - Run extraction phase only"
	@echo "  make transform    - Run transformation phase only"
	@echo "  make load         - Run database loading phase only"
	@echo "  make analyze      - Run analysis phase only"
	@echo "  make full         - Run full pipeline"
	@echo "  make test-run     - Run pipeline with limited rows (testing)"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test         - Run all tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make lint         - Run code linting"
	@echo ""
	@echo "Database:"
	@echo "  make db-create    - Create MySQL database"
	@echo "  make db-reset     - Reset database (drops and recreates)"
	@echo ""

setup:
	@echo "Running automated setup..."
	python3 setup_helper.py

install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt

clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete!"

test:
	@echo "Running tests..."
	pytest tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint:
	@echo "Running linting..."
	flake8 src/ --max-line-length=120 --exclude=__pycache__,*.pyc
	pylint src/ --max-line-length=120 || true

extract:
	@echo "Running extraction phase..."
	python -m src.main --extract

transform:
	@echo "Running transformation phase..."
	python -m src.main --transform

load:
	@echo "Running database loading phase..."
	python -m src.main --load

analyze:
	@echo "Running analysis phase..."
	python -m src.main --analyze

full:
	@echo "Running full pipeline..."
	python -m src.main --full

test-run:
	@echo "Running pipeline with limited rows (testing)..."
	python -m src.main --full --max-rows 10000

db-create:
	@echo "Creating MySQL database..."
	mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS genomic_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

db-reset:
	@echo "Resetting database..."
	mysql -u root -p -e "DROP DATABASE IF EXISTS genomic_analysis; CREATE DATABASE genomic_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
	@echo "Database reset complete!"

# Development helpers
dev-setup:
	@echo "Setting up development environment..."
	pip install flake8 pylint black isort
	@echo "Development tools installed!"

format:
	@echo "Formatting code..."
	black src/ tests/
	isort src/ tests/

check:
	@echo "Running all checks..."
	make lint
	make test
	@echo "All checks complete!"

.DEFAULT_GOAL := help

