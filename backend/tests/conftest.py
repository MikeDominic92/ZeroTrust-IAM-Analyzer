"""
Pytest configuration and fixtures for ZeroTrust IAM Analyzer tests.

This module provides shared test fixtures for database, Redis,
and authentication testing.
"""

import pytest
from app.core.config import get_settings
from app.core.redis import close_redis, get_redis_client
from app.models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

settings = get_settings()


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Create test database engine.

    Uses in-memory SQLite for fast, isolated testing.
    For integration tests, use actual PostgreSQL test database.
    """
    # Use in-memory SQLite for unit tests (fast, isolated)
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """
    Create a fresh database session for each test.

    Automatically rolls back changes after each test for isolation.
    """
    connection = test_db_engine.connect()
    transaction = connection.begin()

    # Create session bound to connection
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()

    yield session

    # Rollback transaction and close session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def redis_client():
    """
    Get Redis client for tests.

    Yields Redis client if available, otherwise skips tests requiring Redis.
    Flushes test database after each test for isolation.
    """
    client = get_redis_client()

    if client is None:
        pytest.skip("Redis not available for testing")

    # Use test database (db 1) instead of default (db 0)
    client.select(1)

    # Clear test database before test
    client.flushdb()

    yield client

    # Clear test database after test
    client.flushdb()

    # Switch back to default database
    client.select(0)


@pytest.fixture(scope="session", autouse=True)
def cleanup_redis():
    """
    Cleanup Redis connections after all tests complete.
    """
    yield

    # Close Redis connections
    close_redis()
