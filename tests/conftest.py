"""
Pytest configuration for nih-reporter-grant-similarity-agent test suite.
"""
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path for test imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set stable audit key for reproducible tests
os.environ.setdefault("AUDIT_SECRET_KEY", "test-suite-audit-key-do-not-use-in-production")
