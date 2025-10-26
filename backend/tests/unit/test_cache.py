"""
Unit tests for Redis cache service.

Tests cache operations for session management including
cache/retrieve/invalidate operations and TTL behavior.
"""

import uuid
from datetime import datetime, timedelta

from app.models.role import Role
from app.models.session import Session as SessionModel
from app.models.user import User, UserStatus
from app.services.cache_service import (
    cache_session,
    get_cache_stats,
    get_cached_session,
    invalidate_session,
)


class TestCacheService:
    """Test suite for cache service operations."""

    def test_cache_and_retrieve_session(self, redis_client, db_session):
        """Test caching a session and retrieving it."""
        # Create test user
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            status=UserStatus.ACTIVE,
            is_verified=True,
            is_active=True,
            created_at=datetime.utcnow(),
        )

        # Create test role
        role = Role(
            id=uuid.uuid4(),
            name="User",
            description="Standard user role",
            is_active=True,
            created_at=datetime.utcnow(),
        )

        # Assign role to user
        user.roles.append(role)

        db_session.add(user)
        db_session.add(role)
        db_session.commit()

        # Create test session
        session = SessionModel(
            id=uuid.uuid4(),
            user_id=user.id,
            token_jti="test-jti-123",
            refresh_token_jti="test-refresh-jti-123",
            expires_at=datetime.utcnow() + timedelta(minutes=15),
            is_revoked=False,
            created_at=datetime.utcnow(),
        )

        db_session.add(session)
        db_session.commit()

        # Cache the session
        result = cache_session(session, user)
        assert result is True, "Session should be cached successfully"

        # Retrieve from cache
        cached = get_cached_session("test-jti-123")

        assert cached is not None, "Session should be found in cache"
        assert cached["user_id"] == str(user.id)
        assert cached["email"] == "test@example.com"
        assert cached["roles"] == ["User"]
        assert cached["is_revoked"] is False

    def test_cache_miss(self, redis_client):
        """Test retrieving non-existent session from cache."""
        cached = get_cached_session("non-existent-jti")
        assert cached is None, "Non-existent session should return None"

    def test_invalidate_session(self, redis_client, db_session):
        """Test invalidating a cached session."""
        # Create and cache a session
        user = User(
            id=uuid.uuid4(),
            email="test2@example.com",
            username="testuser2",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
            is_active=True,
            created_at=datetime.utcnow(),
        )

        role = Role(
            id=uuid.uuid4(),
            name="User",
            is_active=True,
            created_at=datetime.utcnow(),
        )

        user.roles.append(role)
        db_session.add(user)
        db_session.add(role)
        db_session.commit()

        session = SessionModel(
            id=uuid.uuid4(),
            user_id=user.id,
            token_jti="test-jti-invalidate",
            expires_at=datetime.utcnow() + timedelta(minutes=15),
            created_at=datetime.utcnow(),
        )

        db_session.add(session)
        db_session.commit()

        # Cache the session
        cache_session(session, user)

        # Verify it's cached
        cached = get_cached_session("test-jti-invalidate")
        assert cached is not None

        # Invalidate the session
        result = invalidate_session("test-jti-invalidate")
        assert result is True

        # Verify it's no longer in cache
        cached_after = get_cached_session("test-jti-invalidate")
        assert cached_after is None, "Session should be removed from cache"

    def test_cache_expired_session_data(self, redis_client, db_session):
        """Test that cached data includes expiration timestamp."""
        user = User(
            id=uuid.uuid4(),
            email="test3@example.com",
            username="testuser3",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
            is_active=True,
            created_at=datetime.utcnow(),
        )

        role = Role(
            id=uuid.uuid4(),
            name="User",
            is_active=True,
            created_at=datetime.utcnow(),
        )

        user.roles.append(role)
        db_session.add(user)
        db_session.add(role)
        db_session.commit()

        expires_at = datetime.utcnow() + timedelta(minutes=15)
        session = SessionModel(
            id=uuid.uuid4(),
            user_id=user.id,
            token_jti="test-jti-expiry",
            expires_at=expires_at,
            created_at=datetime.utcnow(),
        )

        db_session.add(session)
        db_session.commit()

        cache_session(session, user)

        cached = get_cached_session("test-jti-expiry")
        assert cached is not None
        assert "expires_at" in cached
        assert cached["expires_at"] == expires_at.isoformat()

    def test_cache_revoked_session(self, redis_client, db_session):
        """Test caching a revoked session."""
        user = User(
            id=uuid.uuid4(),
            email="test4@example.com",
            username="testuser4",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
            is_active=True,
            created_at=datetime.utcnow(),
        )

        role = Role(
            id=uuid.uuid4(),
            name="User",
            is_active=True,
            created_at=datetime.utcnow(),
        )

        user.roles.append(role)
        db_session.add(user)
        db_session.add(role)
        db_session.commit()

        session = SessionModel(
            id=uuid.uuid4(),
            user_id=user.id,
            token_jti="test-jti-revoked",
            expires_at=datetime.utcnow() + timedelta(minutes=15),
            is_revoked=True,
            revoked_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )

        db_session.add(session)
        db_session.commit()

        cache_session(session, user)

        cached = get_cached_session("test-jti-revoked")
        assert cached is not None
        assert cached["is_revoked"] is True

    def test_get_cache_stats(self, redis_client):
        """Test getting cache statistics."""
        stats = get_cache_stats()

        assert stats is not None
        assert "status" in stats

        if stats["status"] == "available":
            assert "session_count" in stats
            assert "memory_used" in stats
            assert "redis_version" in stats
