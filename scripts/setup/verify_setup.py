#!/usr/bin/env python3
"""
Project Verification Script
Checks if all required files and configurations are in place
"""
import os
import sys
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def check_mark(passed):
    """Return check mark or X based on test result"""
    return f"{Colors.GREEN}✓{Colors.ENDC}" if passed else f"{Colors.RED}✗{Colors.ENDC}"


def print_section(title):
    """Print section header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'=' * len(title)}{Colors.ENDC}")


def check_files():
    """Check if all required files exist"""
    print_section("Checking Project Files")

    required_files = {
        "Core Files": [
            "README.md",
            "QUICKSTART.md",
            "requirements.txt",
            "setup.py",
            "setup_helper.py",
            "Makefile",
        ],
        "Documentation": [
            "TROUBLESHOOTING.md",
            "CONTRIBUTING.md",
            "CHANGELOG.md",
            "PROJECT_SUMMARY.md",
            "LICENSE",
        ],
        "Configuration": [
            "config/db_config.yml",
            "config/etl_config.yml",
            ".env.template",
            ".gitignore",
        ],
        "Source Code": [
            "src/__init__.py",
            "src/main.py",
            "src/etl/__init__.py",
            "src/etl/extract_vcf.py",
            "src/etl/transform_vcf.py",
            "src/etl/load_to_mysql.py",
            "src/etl/enrich_annotations.py",
            "src/analysis/__init__.py",
            "src/analysis/variant_summary.py",
            "src/analysis/mutation_analysis.py",
            "src/utils/__init__.py",
            "src/utils/logger.py",
            "src/utils/db_config.py",
            "src/utils/file_utils.py",
        ],
        "Tests": [
            "tests/__init__.py",
            "tests/test_vcf_parser.py",
            "tests/test_db_inserts.py",
            "tests/test_data_quality.py",
        ],
        "Directories": [
            "data/raw",
            "data/processed",
            "data/logs",
            "powerbi",
        ],
    }

    all_passed = True

    for category, files in required_files.items():
        print(f"\n{Colors.BOLD}{category}:{Colors.ENDC}")
        for file in files:
            exists = os.path.exists(file)
            all_passed = all_passed and exists
            status = check_mark(exists)
            print(f"  {status} {file}")

    return all_passed


def check_python_version():
    """Check Python version"""
    print_section("Checking Python Version")

    version = sys.version_info
    required = (3, 11)
    passed = version >= required

    status = check_mark(passed)
    print(f"  {status} Python {version.major}.{version.minor}.{version.micro} "
          f"(Required: {required[0]}.{required[1]}+)")

    return passed


def check_virtual_env():
    """Check if virtual environment exists"""
    print_section("Checking Virtual Environment")

    venv_exists = os.path.exists(".venv")
    status = check_mark(venv_exists)
    print(f"  {status} Virtual environment (.venv)")

    if venv_exists:
        # Check if it's activated
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        status_active = check_mark(in_venv)
        print(f"  {status_active} Virtual environment activated")

    return venv_exists


def check_dependencies():
    """Check if dependencies are installed"""
    print_section("Checking Dependencies")

    required_packages = [
        "pandas",
        "numpy",
        "sqlalchemy",
        "pymysql",
        "yaml",
        "requests",
        "tqdm",
    ]

    all_passed = True

    for package in required_packages:
        try:
            __import__(package)
            passed = True
        except ImportError:
            passed = False
            all_passed = False

        status = check_mark(passed)
        print(f"  {status} {package}")

    return all_passed


def check_config_files():
    """Check configuration files"""
    print_section("Checking Configuration")

    checks = []

    # Check if .env exists
    env_exists = os.path.exists(".env")
    checks.append(("Environment file (.env)", env_exists, "Optional - copy from .env.template"))

    # Check YAML configs
    db_config = os.path.exists("config/db_config.yml")
    checks.append(("Database configuration", db_config, "Required"))

    etl_config = os.path.exists("config/etl_config.yml")
    checks.append(("ETL configuration", etl_config, "Required"))

    for name, passed, note in checks:
        status = check_mark(passed)
        print(f"  {status} {name} - {note}")

    return all([c[1] for c in checks if "Required" in c[2]])


def print_summary(results):
    """Print summary of checks"""
    print_section("Verification Summary")

    total = len(results)
    passed = sum(1 for r in results.values() if r)

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All checks passed! ({passed}/{total}){Colors.ENDC}")
        print(f"\n{Colors.CYAN}Project is ready to use!{Colors.ENDC}")
        print(f"\nNext steps:")
        print(f"  1. Activate virtual environment: {Colors.YELLOW}source .venv/bin/activate{Colors.ENDC}")
        print(f"  2. Configure settings in: {Colors.YELLOW}.env{Colors.ENDC} and {Colors.YELLOW}config/*.yml{Colors.ENDC}")
        print(f"  3. Run quick test: {Colors.YELLOW}make test-run{Colors.ENDC}")
        print(f"  4. View help: {Colors.YELLOW}python -m src.main --help{Colors.ENDC}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some checks failed ({passed}/{total} passed){Colors.ENDC}")
        print(f"\n{Colors.CYAN}Action required:{Colors.ENDC}")

        if not results.get("files"):
            print(f"  - Some required files are missing")

        if not results.get("python"):
            print(f"  - Upgrade Python to 3.11+")

        if not results.get("venv"):
            print(f"  - Run: {Colors.YELLOW}python3 setup_helper.py{Colors.ENDC}")

        if not results.get("dependencies"):
            print(f"  - Install dependencies: {Colors.YELLOW}pip install -r requirements.txt{Colors.ENDC}")

        if not results.get("config"):
            print(f"  - Check configuration files in config/ directory")


def main():
    """Run all verification checks"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("=" * 80)
    print("Genomic Data Analysis Platform - Project Verification".center(80))
    print("=" * 80)
    print(f"{Colors.ENDC}")

    results = {
        "files": check_files(),
        "python": check_python_version(),
        "venv": check_virtual_env(),
        "dependencies": check_dependencies(),
        "config": check_config_files(),
    }

    print_summary(results)

    # Return exit code
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

