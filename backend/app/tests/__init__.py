"""
Tests package for ZeroTrust IAM Analyzer

This package contains all test cases for the ZeroTrust IAM Analyzer.
"""

import pytest
from app.core.config import settings

# Configure test settings
settings.TESTING = True

__all__ = ["pytest", "settings"]
