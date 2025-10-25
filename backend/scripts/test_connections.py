"""
Connection test script for ZeroTrust IAM Analyzer development environment.

Tests connections to:
- PostgreSQL database
- Redis cache
- Verifies database schema migrations
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio

import redis
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")


def test_postgresql():
    """Test PostgreSQL connection and verify schema."""
    print("\n[+] Testing PostgreSQL connection...")

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("[!] DATABASE_URL not found in environment")
        return False

    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"[+] PostgreSQL connected successfully")
            print(f"    Version: {version.split(',')[0]}")

            # Check if tables exist
            result = conn.execute(
                text(
                    """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """
                )
            )
            tables = [row[0] for row in result.fetchall()]

            if tables:
                print(f"[+] Found {len(tables)} tables:")
                for table in tables:
                    print(f"    - {table}")
            else:
                print("[!] No tables found. Run migrations first.")

            # Check alembic version
            try:
                result = conn.execute(text("SELECT version_num FROM alembic_version;"))
                migration_version = result.fetchone()[0]
                print(f"[+] Current migration version: {migration_version}")
            except Exception:
                print("[!] Alembic version table not found")

        return True

    except OperationalError as e:
        print(f"[!] PostgreSQL connection failed: {e}")
        return False
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        return False


def test_redis():
    """Test Redis connection."""
    print("\n[+] Testing Redis connection...")

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

    try:
        # Parse Redis URL
        if redis_url.startswith("redis://"):
            host_port = redis_url.replace("redis://", "").split(":")
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 6379
        else:
            host = "localhost"
            port = 6379

        client = redis.Redis(host=host, port=port, decode_responses=True)

        # Test connection
        ping_response = client.ping()
        if ping_response:
            print("[+] Redis connected successfully")

            # Get Redis info
            info = client.info("server")
            print(f"    Version: {info.get('redis_version', 'unknown')}")
            print(f"    Mode: {info.get('redis_mode', 'standalone')}")

            # Test set/get
            test_key = "zerotrust:connection_test"
            client.set(test_key, "test_value", ex=10)
            value = client.get(test_key)
            client.delete(test_key)

            if value == "test_value":
                print("[+] Redis read/write test passed")

        return True

    except redis.ConnectionError as e:
        print(f"[!] Redis connection failed: {e}")
        return False
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        return False


def main():
    """Run all connection tests."""
    print("=" * 60)
    print("ZeroTrust IAM Analyzer - Connection Tests")
    print("=" * 60)

    results = {}
    results["postgresql"] = test_postgresql()
    results["redis"] = test_redis()

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    all_passed = True
    for service, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {service}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n[+] All tests passed! Development environment is ready.")
        return 0
    else:
        print("\n[!] Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
