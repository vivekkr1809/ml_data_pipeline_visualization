#!/usr/bin/env python
"""
Convenience script to run the ML Data Pipeline Visualizer
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run main
from src.main import main

if __name__ == "__main__":
    main()
