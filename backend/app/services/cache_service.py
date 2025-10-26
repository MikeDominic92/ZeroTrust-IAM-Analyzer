"""
Cache service for session management with Redis.

This module provides session caching operations for improved authentication
performance. Reduces database queries by caching session data in Redis with
appropriate TTLs matching token expiration times.
"""

import json
from typing import Optional

from app.core.logging import get_logger
from app.core.redis import get_redis_client
from app.models.session import Session as SessionModel
from app.models.user import User

logger = get_logger(__name__)

# Cache key prefix for session data
SESSION_CACHE_PREFIX = "session"

# Cache TTL in seconds (15 minutes - matches access token expiry)
SESSION_CACHE_TTL = 900


def _get_session_cache_key(token_jti: str) -> str:
    """
    Generate Redis cache key for session data.

    Args:
        token_jti: JWT token JTI (unique identifier)

    Returns:
        Redis cache key (e.g., "session:abc123")

    Example:
        ```python
        key = _get_session_cache_key("a1b2c3d4-e5f6-...")
        # Returns: "session:a1b2c3d4-e5f6-..."
        ```
    """
    return f"{SESSION_CACHE_PREFIX}:{token_jti}"


def cache_session(session: SessionModel, user: User) -> bool:
    """
    Cache session data in Redis for fast authentication lookups.

    Stores session and user information in Redis with TTL matching access
    token expiration. Enables fast authentication validation without database
    queries for cache hits.

    Args:
        session: Session model instance
        user: User model instance (owner of session)

    Returns:
        True if cached successfully, False if Redis unavailable

    Example:
        ```python
        # After creating session in database
        session = create_session(...)
        user = get_user(session.user_id)
        cache_session(session, user)
        ```

    Cached Data Structure:
        ```json
        {
            "user_id": "uuid-string",
            "email": "user@example.com",
            "roles": ["User", "Admin"],
            "is_revoked": false,
            "expires_at": "2025-10-25T13:45:00Z",
            "session_id": "session-uuid"
        }
        ```

    Notes:
        - TTL set to 15 minutes (SESSION_CACHE_TTL)
        - Cache key format: session:{token_jti}
        - Returns False gracefully if Redis unavailable (no exception raised)
        - Role names extracted from user.roles relationship
    """
    try:
        client = get_redis_client()
        if client is None:
            logger.debug(
                "redis_unavailable_for_cache",
                message="Cannot cache session - Redis client not available",
            )
            return False

        # Build cache key
        cache_key = _get_session_cache_key(session.token_jti)

        # Extract role names from user's roles
        role_names = [role.name for role in user.roles if role.is_active]

        # Build cache payload
        cache_data = {
            "user_id": str(session.user_id),
            "email": user.email,
            "roles": role_names,
            "is_revoked": session.is_revoked,
            "expires_at": session.expires_at.isoformat(),
            "session_id": str(session.id),
        }

        # Serialize to JSON and store in Redis
        cache_json = json.dumps(cache_data)
        client.setex(cache_key, SESSION_CACHE_TTL, cache_json)

        logger.debug(
            "session_cached",
            token_jti=session.token_jti,
            user_id=str(session.user_id),
            email=user.email,
            ttl=SESSION_CACHE_TTL,
        )

        return True

    except json.JSONEncodeError as e:
        logger.error(
            "session_cache_json_error",
            error=str(e),
            token_jti=session.token_jti,
            exc_info=True,
        )
        return False

    except Exception as e:
        logger.error(
            "session_cache_error",
            error=str(e),
            error_type=type(e).__name__,
            token_jti=session.token_jti,
            exc_info=True,
        )
        return False


def get_cached_session(token_jti: str) -> Optional[dict]:
    """
    Retrieve cached session data from Redis.

    Attempts to get session data from Redis cache. Returns None if cache
    miss or Redis unavailable (caller should query database).

    Args:
        token_jti: JWT token JTI (unique identifier)

    Returns:
        Cached session dict or None if not found/unavailable

    Example:
        ```python
        # Try cache first
        cached = get_cached_session(token_jti)
        if cached:
            # Cache hit - validate and use
            if not cached["is_revoked"]:
                user_id = cached["user_id"]
        else:
            # Cache miss - query database
            session = db.query(Session).filter(...)
        ```

    Returned Dict Structure (on cache hit):
        ```python
        {
            "user_id": "uuid-string",
            "email": "user@example.com",
            "roles": ["User", "Admin"],
            "is_revoked": False,
            "expires_at": "2025-10-25T13:45:00Z",
            "session_id": "session-uuid"
        }
        ```

    Notes:
        - Returns None gracefully on any error (no exceptions raised)
        - Caller must validate expires_at and is_revoked
        - Cache misses are normal (new sessions, expired TTL, Redis restart)
        - Logs cache hits/misses for monitoring
    """
    try:
        client = get_redis_client()
        if client is None:
            logger.debug(
                "redis_unavailable_for_lookup",
                message="Cannot lookup session - Redis client not available",
            )
            return None

        # Build cache key
        cache_key = _get_session_cache_key(token_jti)

        # Try to get from cache
        cached_json = client.get(cache_key)

        if cached_json is None:
            # Cache miss - normal scenario
            logger.debug("session_cache_miss", token_jti=token_jti)
            return None

        # Parse JSON
        cached_data = json.loads(cached_json)

        logger.debug(
            "session_cache_hit",
            token_jti=token_jti,
            user_id=cached_data.get("user_id"),
            email=cached_data.get("email"),
        )

        return cached_data

    except json.JSONDecodeError as e:
        logger.error(
            "session_cache_json_decode_error",
            error=str(e),
            token_jti=token_jti,
            exc_info=True,
        )
        # Invalidate corrupted cache entry
        invalidate_session(token_jti)
        return None

    except Exception as e:
        logger.error(
            "session_cache_lookup_error",
            error=str(e),
            error_type=type(e).__name__,
            token_jti=token_jti,
            exc_info=True,
        )
        return None


def invalidate_session(token_jti: str) -> bool:
    """
    Remove session from Redis cache.

    Deletes cached session data for a specific token. Should be called on
    logout, session revocation, or when cached data becomes invalid.

    Args:
        token_jti: JWT token JTI to invalidate

    Returns:
        True if invalidated (or key didn't exist), False if Redis unavailable

    Example:
        ```python
        # On logout
        def logout(session: Session):
            # Invalidate cache BEFORE marking revoked in DB
            invalidate_session(session.token_jti)

            # Then update database
            session.is_revoked = True
            db.commit()
        ```

    Notes:
        - Returns True even if key didn't exist (idempotent)
        - Returns False only if Redis client unavailable
        - Safe to call multiple times for same token
        - Call BEFORE database update to ensure consistency
    """
    try:
        client = get_redis_client()
        if client is None:
            logger.debug(
                "redis_unavailable_for_invalidation",
                message="Cannot invalidate session - Redis client not available",
            )
            return False

        # Build cache key
        cache_key = _get_session_cache_key(token_jti)

        # Delete from cache
        deleted_count = client.delete(cache_key)

        logger.debug(
            "session_cache_invalidated",
            token_jti=token_jti,
            was_cached=deleted_count > 0,
        )

        return True

    except Exception as e:
        logger.error(
            "session_cache_invalidation_error",
            error=str(e),
            error_type=type(e).__name__,
            token_jti=token_jti,
            exc_info=True,
        )
        return False


def invalidate_user_sessions(user_id: str) -> int:
    """
    Invalidate all cached sessions for a specific user.

    Useful when user's roles change, account is disabled, or during
    security events requiring full session logout. Scans Redis for all
    sessions belonging to the user and deletes them.

    Args:
        user_id: User UUID string

    Returns:
        Number of sessions invalidated (0 if Redis unavailable or no sessions)

    Example:
        ```python
        # When user account is disabled
        def disable_user_account(user_id: str):
            # Invalidate all cached sessions
            count = invalidate_user_sessions(user_id)

            # Update database
            user.is_active = False
            db.query(Session).filter(
                Session.user_id == user_id
            ).update({"is_revoked": True})
            db.commit()

            logger.info(f"Invalidated {count} sessions for user {user_id}")
        ```

    Notes:
        - Scans Redis using SCAN (not KEYS for production safety)
        - Returns 0 if Redis unavailable
        - Returns count of deleted cache entries
        - Database sessions still need to be revoked separately
        - Performance: O(N) where N = total sessions in cache
    """
    try:
        client = get_redis_client()
        if client is None:
            logger.debug(
                "redis_unavailable_for_bulk_invalidation",
                message="Cannot invalidate user sessions - Redis unavailable",
            )
            return 0

        # Use SCAN to find all session keys (production-safe, non-blocking)
        pattern = f"{SESSION_CACHE_PREFIX}:*"
        invalidated_count = 0

        # Scan for all session keys
        for key in client.scan_iter(match=pattern, count=100):
            # Get session data to check user_id
            try:
                cached_json = client.get(key)
                if cached_json:
                    cached_data = json.loads(cached_json)
                    if cached_data.get("user_id") == user_id:
                        # This session belongs to the user - delete it
                        client.delete(key)
                        invalidated_count += 1
            except (json.JSONDecodeError, KeyError):
                # Corrupted cache entry - delete it anyway
                client.delete(key)
                continue

        logger.info(
            "user_sessions_invalidated",
            user_id=user_id,
            count=invalidated_count,
        )

        return invalidated_count

    except Exception as e:
        logger.error(
            "user_sessions_invalidation_error",
            error=str(e),
            error_type=type(e).__name__,
            user_id=user_id,
            exc_info=True,
        )
        return 0


def get_cache_stats() -> dict:
    """
    Get session cache statistics for monitoring.

    Returns statistics about cached sessions including total count,
    memory usage, and hit/miss rates (if available).

    Returns:
        Dictionary with cache statistics

    Example:
        ```python
        stats = get_cache_stats()
        print(f"Cached sessions: {stats['session_count']}")
        print(f"Memory used: {stats['memory_used']}")
        ```

    Returned Dict Structure:
        ```python
        {
            "status": "available",
            "session_count": 42,
            "memory_used": "1.2MB",
            "redis_version": "7.0.0",
        }
        ```

    Notes:
        - Returns error dict if Redis unavailable
        - Session count obtained by scanning session:* keys
        - Memory stats from Redis INFO command
    """
    try:
        client = get_redis_client()
        if client is None:
            return {
                "status": "unavailable",
                "error": "Redis client not available",
            }

        # Count session keys
        pattern = f"{SESSION_CACHE_PREFIX}:*"
        session_count = sum(1 for _ in client.scan_iter(match=pattern, count=100))

        # Get Redis info
        info = client.info()

        return {
            "status": "available",
            "session_count": session_count,
            "memory_used": info.get("used_memory_human", "unknown"),
            "redis_version": info.get("redis_version", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
        }

    except Exception as e:
        logger.error("cache_stats_error", error=str(e), exc_info=True)
        return {
            "status": "error",
            "error": str(e),
        }
