"""
Database configuration and connection management for ZeroTrust IAM Analyzer.

This module handles SQLAlchemy engine setup, session management,
and database dependencies for FastAPI.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings
from .logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base will be imported from models when needed
Base = None


def get_base():
    """Get the Base class from models."""
    from app.models import Base

    return Base


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("database_session_error", error=str(e), exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def create_tables() -> None:
    """Create all database tables."""
    try:
        base = get_base()
        base.metadata.create_all(bind=engine)
        logger.info("database_tables_created")
    except Exception as e:
        logger.error("database_tables_creation_failed", error=str(e), exc_info=True)
        raise


def drop_tables() -> None:
    """Drop all database tables."""
    try:
        base = get_base()
        base.metadata.drop_all(bind=engine)
        logger.info("database_tables_dropped")
    except Exception as e:
        logger.error("database_tables_drop_failed", error=str(e), exc_info=True)
        raise


def check_database_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        True if connection is healthy, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("database_connection_healthy")
        return True
    except Exception as e:
        logger.error("database_connection_failed", error=str(e), exc_info=True)
        return False


class DatabaseManager:
    """Database connection manager."""

    def __init__(self):
        """Initialize database manager."""
        self.engine = engine
        self.session_factory = SessionLocal

    def get_session(self) -> Session:
        """
        Get a new database session.

        Returns:
            Database session
        """
        return self.session_factory()

    def health_check(self) -> dict:
        """
        Perform database health check.

        Returns:
            Health check result
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute("SELECT 1")
                row = result.fetchone()

            return {
                "status": "healthy",
                "database": "connected",
                "test_query": "SELECT 1",
                "result": row[0] if row else None,
            }
        except Exception as e:
            logger.error("database_health_check_failed", error=str(e), exc_info=True)
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
            }

    def close_connections(self) -> None:
        """Close all database connections."""
        try:
            self.engine.dispose()
            logger.info("database_connections_closed")
        except Exception as e:
            logger.error("database_connections_close_failed", error=str(e), exc_info=True)
            raise


# Create global database manager instance
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    """
    Get database manager instance.

    Returns:
        Database manager instance
    """
    return db_manager


class DatabaseTransaction:
    """Context manager for database transactions."""

    def __init__(self, session: Session):
        """
        Initialize transaction context manager.

        Args:
            session: Database session
        """
        self.session = session

    def __enter__(self) -> Session:
        """Enter transaction context."""
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context."""
        try:
            if exc_type is not None:
                # Exception occurred, rollback
                self.session.rollback()
                logger.error(
                    "database_transaction_rolled_back",
                    error=str(exc_val),
                    exc_info=True,
                )
            else:
                # No exception, commit
                self.session.commit()
                logger.debug("database_transaction_committed")
        except Exception as e:
            logger.error("database_transaction_error", error=str(e), exc_info=True)
            self.session.rollback()
            raise
        finally:
            self.session.close()


def transaction(session: Session) -> DatabaseTransaction:
    """
    Create a database transaction context manager.

    Args:
        session: Database session

    Returns:
        Database transaction context manager
    """
    return DatabaseTransaction(session)


async def execute_raw_sql(session: Session, query: str, params: dict = None) -> any:
    """
    Execute raw SQL query.

    Args:
        session: Database session
        query: SQL query string
        params: Query parameters (optional)

    Returns:
        Query result
    """
    try:
        result = session.execute(query, params or {})
        logger.debug("raw_sql_executed", query=query, params=params)
        return result
    except Exception as e:
        logger.error(
            "raw_sql_execution_failed",
            query=query,
            params=params,
            error=str(e),
            exc_info=True,
        )
        raise


def get_database_info() -> dict:
    """
    Get database information.

    Returns:
        Database information
    """
    try:
        with engine.connect() as connection:
            # Get database version (PostgreSQL specific)
            if "postgresql" in settings.database_url:
                result = connection.execute("SELECT version()")
                version = result.fetchone()[0]
            else:
                version = "Unknown"

            # Get connection pool info
            pool = engine.pool
            pool_info = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
            }

            return {
                "url": (
                    settings.database_url.split("@")[-1]
                    if "@" in settings.database_url
                    else "hidden"
                ),
                "version": version,
                "pool": pool_info,
                "driver": engine.driver,
            }
    except Exception as e:
        logger.error("database_info_failed", error=str(e), exc_info=True)
        return {
            "error": str(e),
        }
