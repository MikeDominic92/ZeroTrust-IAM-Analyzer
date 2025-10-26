"""
Pytest configuration and fixtures for ZeroTrust IAM Analyzer tests.

This module provides shared test fixtures for database, Redis,
and authentication testing.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

import pytest
from app.core.config import get_settings
from app.core.redis import close_redis, get_redis_client
from app.core.security import get_password_hash
from app.models.base import Base
from app.models.role import Role
from app.models.session import Session as SessionModel
from app.models.user import User, UserStatus
from fastapi.testclient import TestClient
from jose import jwt
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


# ===================================================
# Test Data Factories (Task 1.12)
# ===================================================


@pytest.fixture(scope="session")
def default_user_role(test_db_engine):
    """
    Create default User role for tests (session-scoped for performance).

    This role is created once per test session and reused across tests.
    """
    SessionLocal = sessionmaker(bind=test_db_engine)
    session = SessionLocal()

    # Check if role already exists
    role = session.query(Role).filter(Role.name == "User").first()

    if not role:
        role = Role(
            id=uuid.uuid4(),
            name="User",
            description="Standard user role for testing",
            is_active=True,
            created_at=datetime.utcnow(),
            permissions='["user.read", "user.update_self"]',
        )
        session.add(role)
        session.commit()
        session.refresh(role)

    session.close()
    return role


@pytest.fixture(scope="session")
def admin_role(test_db_engine):
    """
    Create Admin role for RBAC tests (session-scoped for performance).
    """
    SessionLocal = sessionmaker(bind=test_db_engine)
    session = SessionLocal()

    # Check if role already exists
    role = session.query(Role).filter(Role.name == "Admin").first()

    if not role:
        role = Role(
            id=uuid.uuid4(),
            name="Admin",
            description="Administrator role for testing",
            is_active=True,
            created_at=datetime.utcnow(),
            permissions='["*"]',
        )
        session.add(role)
        session.commit()
        session.refresh(role)

    session.close()
    return role


@pytest.fixture
def user_factory(db_session, default_user_role):
    """
    Factory fixture for creating test users with customizable attributes.

    Usage:
        def test_something(user_factory):
            user = user_factory(email="test@example.com", username="testuser")
    """

    def _create_user(
        email: Optional[str] = None,
        username: Optional[str] = None,
        password: str = "TestPass123!",
        first_name: str = "Test",
        last_name: str = "User",
        status: UserStatus = UserStatus.ACTIVE,
        is_verified: bool = True,
        is_active: bool = True,
        roles: Optional[list] = None,
        **kwargs,
    ) -> User:
        """Create a test user with sensible defaults."""
        # Generate unique email and username if not provided
        unique_id = str(uuid.uuid4())[:8]
        if email is None:
            email = f"user_{unique_id}@example.com"
        if username is None:
            username = f"user_{unique_id}"

        # Hash password
        password_hash = get_password_hash(password)

        # Create user
        user = User(
            id=uuid.uuid4(),
            email=email.lower(),
            username=username.lower(),
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            status=status,
            is_verified=is_verified,
            is_active=is_active,
            created_at=datetime.utcnow(),
            **kwargs,
        )

        # Assign roles
        if roles is None:
            role = db_session.query(Role).filter(Role.name == "User").first()
            if role:
                user.roles.append(role)
        else:
            for role in roles:
                user.roles.append(role)

        # Add to database
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Store plain password for testing login
        user._test_password = password

        return user

    return _create_user


@pytest.fixture
def authenticated_user(user_factory, db_session):
    """
    Create a user with valid access and refresh tokens.

    Returns:
        dict with keys: user, access_token, refresh_token, session
    """
    # Create user
    user = user_factory()

    # Generate token JTIs
    access_jti = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())

    # Calculate expiration
    access_exp = datetime.utcnow() + timedelta(minutes=30)

    # Create access token
    access_token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "roles": [role.name for role in user.roles],
        "jti": access_jti,
        "type": "access",
        "exp": int(access_exp.timestamp()),
    }

    access_token = jwt.encode(
        access_token_payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    # Create refresh token
    refresh_token_payload = {
        "sub": str(user.id),
        "jti": refresh_jti,
        "type": "refresh",
        "exp": int((datetime.utcnow() + timedelta(days=7)).timestamp()),
    }

    refresh_token = jwt.encode(
        refresh_token_payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    # Create session
    session = SessionModel(
        id=uuid.uuid4(),
        user_id=user.id,
        token_jti=access_jti,
        refresh_token_jti=refresh_jti,
        expires_at=access_exp,
        created_at=datetime.utcnow(),
        last_activity_at=datetime.utcnow(),
    )

    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    return {
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "session": session,
        "access_jti": access_jti,
        "refresh_jti": refresh_jti,
    }


@pytest.fixture
def admin_user(user_factory, admin_role, db_session):
    """
    Create an admin user for RBAC testing.

    Returns:
        User object with Admin role
    """
    # Query admin role from database
    role = db_session.query(Role).filter(Role.name == "Admin").first()

    # Create admin user
    user = user_factory(
        email="admin@example.com",
        username="admin",
        roles=[role] if role else [],
    )

    return user


@pytest.fixture
def locked_user(user_factory):
    """
    Create a user with account locked due to failed login attempts.

    Returns:
        User object with is_account_locked=True
    """
    user = user_factory(
        email="locked@example.com",
        username="locked_user",
        failed_login_attempts=5,
        last_failed_login=datetime.utcnow(),
    )

    return user


@pytest.fixture
def test_client(db_session):
    """
    FastAPI TestClient for integration testing.

    Overrides get_db dependency to use test database session.
    """
    from app.api.v1.auth import router as auth_router
    from app.core.database import get_db
    from fastapi import FastAPI

    # Create FastAPI app
    app = FastAPI()

    # Include auth router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

    # Override get_db dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Create test client
    client = TestClient(app)

    return client
