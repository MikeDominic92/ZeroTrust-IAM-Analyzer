"""
Dependency injection utilities for ZeroTrust IAM Analyzer.

This module provides FastAPI dependencies for database sessions,
authentication, and other common requirements.
"""

from typing import Generator

from app.core.database import SessionLocal
from sqlalchemy.orm import Session


def get_db() -> Generator[Session, None, None]:
    """
    Get database session dependency.

    Yields:
        Database session

    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
