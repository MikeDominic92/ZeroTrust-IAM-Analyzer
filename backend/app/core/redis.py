"""
Redis connection management for ZeroTrust IAM Analyzer.

This module handles Redis client initialization, connection pooling,
and graceful degradation when Redis is unavailable.
"""

from typing import Optional

import redis
from redis.connection import ConnectionPool

from .config import get_settings
from .logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Global Redis client instance
_redis_client: Optional[redis.Redis] = None
_connection_pool: Optional[ConnectionPool] = None


def init_redis() -> Optional[redis.Redis]:
    """
    Initialize Redis client with connection pooling.

    Creates a global Redis client instance with connection pooling for
    efficient connection management. Handles connection failures gracefully
    and logs warnings if Redis is unavailable.

    Returns:
        Redis client instance or None if connection fails

    Example:
        ```python
        client = init_redis()
        if client:
            client.set("key", "value")
        ```

    Connection Pool Configuration:
        - max_connections: 10 (shared pool for all operations)
        - socket_timeout: 5 seconds (fail fast on network issues)
        - socket_connect_timeout: 2 seconds (quick connection attempts)
        - decode_responses: True (auto-decode bytes to str)
        - health_check_interval: 30 seconds (proactive health monitoring)
    """
    global _redis_client, _connection_pool

    try:
        # Create connection pool for efficient connection reuse
        _connection_pool = ConnectionPool.from_url(
            settings.redis_url,
            max_connections=10,
            socket_timeout=5,
            socket_connect_timeout=2,
            decode_responses=True,  # Auto-decode bytes to strings
            health_check_interval=30,  # Proactive health checks
        )

        # Create Redis client from pool
        _redis_client = redis.Redis(connection_pool=_connection_pool)

        # Test connection with ping
        _redis_client.ping()

        logger.info(
            "redis_initialized",
            redis_url=(
                settings.redis_url.split("@")[-1]
                if "@" in settings.redis_url
                else settings.redis_url
            ),
            max_connections=10,
        )

        return _redis_client

    except redis.ConnectionError as e:
        logger.warning(
            "redis_connection_failed",
            error=str(e),
            redis_url=(
                settings.redis_url.split("@")[-1]
                if "@" in settings.redis_url
                else settings.redis_url
            ),
            message="Redis unavailable - falling back to database-only mode",
        )
        return None

    except Exception as e:
        logger.error(
            "redis_initialization_error",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        return None


def get_redis_client() -> Optional[redis.Redis]:
    """
    Get global Redis client instance.

    Returns the initialized Redis client or None if Redis is unavailable.
    This function is safe to call repeatedly - it returns the cached client
    instance after first initialization.

    Returns:
        Redis client instance or None if unavailable

    Example:
        ```python
        client = get_redis_client()
        if client:
            value = client.get("session:123")
        else:
            # Fall back to database query
            value = query_from_db()
        ```

    Notes:
        - Returns None gracefully if Redis unavailable (no exceptions raised)
        - Callers should always check for None before using
        - Automatically handles reconnection via connection pool health checks
    """

    # Return cached client if already initialized
    if _redis_client is not None:
        return _redis_client

    # Initialize on first call
    return init_redis()


def close_redis() -> None:
    """
    Close Redis connection and cleanup resources.

    Closes the global Redis client and connection pool. Should be called
    during application shutdown to ensure clean cleanup of connections.

    Example:
        ```python
        # In FastAPI shutdown event
        @app.on_event("shutdown")
        async def shutdown():
            close_redis()
        ```

    Notes:
        - Safe to call multiple times (idempotent)
        - Logs successful cleanup
        - Handles errors gracefully
    """
    global _redis_client, _connection_pool

    try:
        if _redis_client:
            _redis_client.close()
            _redis_client = None

        if _connection_pool:
            _connection_pool.disconnect()
            _connection_pool = None

        logger.info("redis_connections_closed")

    except Exception as e:
        logger.error(
            "redis_close_error",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )


def ping_redis() -> bool:
    """
    Check if Redis is available and responsive.

    Performs a health check by sending PING command to Redis.
    Returns True if Redis responds with PONG, False otherwise.

    Returns:
        True if Redis is healthy, False if unavailable

    Example:
        ```python
        if ping_redis():
            print("Redis is healthy")
        else:
            print("Redis is down - using database fallback")
        ```

    Notes:
        - Non-blocking health check (fast timeout: 5 seconds)
        - Safe to call frequently (lightweight operation)
        - Returns False on any error (no exceptions raised)
    """
    try:
        client = get_redis_client()
        if client is None:
            return False

        # Ping with timeout
        response = client.ping()
        if response:
            logger.debug("redis_ping_successful")
            return True

        logger.warning("redis_ping_failed", response=response)
        return False

    except redis.ConnectionError as e:
        logger.warning("redis_connection_error", error=str(e))
        return False

    except Exception as e:
        logger.error(
            "redis_ping_error",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        return False


def get_redis_info() -> dict:
    """
    Get Redis server information and statistics.

    Retrieves Redis server info including version, memory usage, connected
    clients, and other operational metrics. Useful for monitoring and debugging.

    Returns:
        Dictionary with Redis server information, or error dict if unavailable

    Example:
        ```python
        info = get_redis_info()
        print(f"Redis version: {info.get('redis_version', 'N/A')}")
        print(f"Used memory: {info.get('used_memory_human', 'N/A')}")
        ```

    Returned Fields (when available):
        - redis_version: Redis server version
        - used_memory_human: Human-readable memory usage
        - connected_clients: Number of active client connections
        - uptime_in_seconds: Server uptime
        - keyspace: Database statistics
    """
    try:
        client = get_redis_client()
        if client is None:
            return {"status": "unavailable", "error": "Redis client not initialized"}

        # Get server info
        info = client.info()

        return {
            "status": "available",
            "redis_version": info.get("redis_version", "unknown"),
            "used_memory_human": info.get("used_memory_human", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "uptime_in_seconds": info.get("uptime_in_seconds", 0),
            "keyspace": info.get("db0", {}),
        }

    except redis.ConnectionError as e:
        logger.warning("redis_info_connection_error", error=str(e))
        return {
            "status": "unavailable",
            "error": f"Connection error: {str(e)}",
        }

    except Exception as e:
        logger.error(
            "redis_info_error",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        return {
            "status": "error",
            "error": str(e),
        }


class RedisManager:
    """
    Redis connection manager with health check and monitoring capabilities.

    Provides high-level interface for Redis operations with built-in error
    handling, health checks, and graceful degradation. Useful for applications
    that need Redis management beyond simple client access.
    """

    def __init__(self):
        """Initialize Redis manager."""
        self.client = get_redis_client()

    def is_available(self) -> bool:
        """
        Check if Redis is currently available.

        Returns:
            True if Redis is available and responsive
        """
        return ping_redis()

    def get_client(self) -> Optional[redis.Redis]:
        """
        Get Redis client instance.

        Returns:
            Redis client or None if unavailable
        """
        return get_redis_client()

    def health_check(self) -> dict:
        """
        Perform comprehensive health check on Redis.

        Returns:
            Health check result dictionary

        Example:
            ```python
            manager = RedisManager()
            health = manager.health_check()

            if health["status"] == "healthy":
                print("Redis is operational")
            else:
                print(f"Redis issue: {health.get('error', 'Unknown')}")
            ```
        """
        try:
            if not self.is_available():
                return {
                    "status": "unhealthy",
                    "redis": "disconnected",
                    "error": "Cannot connect to Redis",
                }

            # Get server info
            info = get_redis_info()

            return {
                "status": "healthy",
                "redis": "connected",
                "version": info.get("redis_version", "unknown"),
                "memory": info.get("used_memory_human", "unknown"),
                "clients": info.get("connected_clients", 0),
                "uptime": info.get("uptime_in_seconds", 0),
            }

        except Exception as e:
            logger.error("redis_health_check_failed", error=str(e), exc_info=True)
            return {
                "status": "unhealthy",
                "redis": "error",
                "error": str(e),
            }

    def close(self) -> None:
        """Close Redis connections."""
        close_redis()


# Create global Redis manager instance
redis_manager = RedisManager()


def get_redis_manager() -> RedisManager:
    """
    Get global Redis manager instance.

    Returns:
        RedisManager instance
    """
    return redis_manager
