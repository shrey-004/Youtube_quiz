"""
conftest.py — pytest configuration file.

Placing this in the backend/ root tells pytest to add this
directory to Python's path. That makes 'from app.core.scorer import ...'
work correctly from any test file.

This file can stay empty — its presence alone fixes the import issue.
pytest automatically finds and processes it before running tests.
"""

import sys
import os

# Add the backend directory to Python's module search path
sys.path.insert(0, os.path.dirname(__file__))