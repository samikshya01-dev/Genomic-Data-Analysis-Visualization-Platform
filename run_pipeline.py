#!/usr/bin/env python3
"""
Launcher script for the Genomic Data Analysis Pipeline
This script can be run directly without module path issues
"""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import and run the main module
from src.main import main

if __name__ == "__main__":
    main()

