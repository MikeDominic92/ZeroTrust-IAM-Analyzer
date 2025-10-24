#!/usr/bin/env python3
"""
Dependency Verification Script for Phase 0
Verifies all installed dependencies can be imported successfully
"""

import sys
from typing import List, Tuple


def test_import(module_name: str) -> Tuple[bool, str]:
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        return (True, f"[+] {module_name}")
    except ImportError as e:
        return (False, f"[!] {module_name}: {str(e)}")


def main():
    """Run all import tests"""
    print("\n[NB] Phase 0 - Dependency Verification\n")
    print("=" * 70)

    # Define all required modules
    modules_to_test = [
        # Web Framework
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        # Database
        ("sqlalchemy", "SQLAlchemy"),
        ("alembic", "Alembic"),
        ("psycopg", "psycopg3"),
        # Authentication & Security
        ("jose", "python-jose"),
        ("passlib", "passlib"),
        # Data Validation
        ("pydantic", "Pydantic"),
        ("pydantic_settings", "Pydantic Settings"),
        # HTTP Client
        ("httpx", "HTTPX"),
        # Logging
        ("structlog", "structlog"),
        # Google Cloud SDK
        ("google.cloud.iam", "Google Cloud IAM"),
        ("google.cloud.asset_v1", "Google Cloud Asset"),
        ("google.cloud.recommender_v1", "Google Cloud Recommender"),
        ("google.cloud.securitycenter", "Google Cloud Security Center"),
        # Google Workspace SDK
        ("google.auth", "Google Auth"),
        ("google_auth_httplib2", "Google Auth HTTPLib2"),
        ("googleapiclient", "Google API Client"),
        # Testing Framework
        ("pytest", "pytest"),
        ("pytest_asyncio", "pytest-asyncio"),
        ("pytest_cov", "pytest-cov"),
        ("pytest_mock", "pytest-mock"),
        # Code Quality
        ("black", "Black"),
        ("isort", "isort"),
        ("flake8", "flake8"),
        ("mypy", "mypy"),
        ("bandit", "bandit"),
        # Dev Tools
        ("pre_commit", "pre-commit"),
    ]

    results: List[Tuple[bool, str]] = []

    for module, display_name in modules_to_test:
        success, message = test_import(module)
        results.append((success, message))
        print(message)

    # Summary
    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)

    passed = sum(1 for success, _ in results if success)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\n[+] SUCCESS - All dependencies verified!")
        print("    -> Ready to proceed with Phase 0.B (Code Quality)")
        return 0
    else:
        print("\n[!] FAILED - Some dependencies missing")
        print("    -> Review errors and reinstall missing packages")
        return 1


if __name__ == "__main__":
    sys.exit(main())
