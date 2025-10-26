"""
Authentication service for ZeroTrust IAM Analyzer.

This module provides authentication business logic including user registration,
login, token management, and password reset functionality.
"""

import uuid
from datetime import datetime
from typing import Optional

from app.core.security import get_password_hash, verify_password
from app.models.role import Role
from app.models.user import User, UserStatus
from app.schemas.auth import UserRegisterRequest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


class AuthService:
    """Authentication service for user management operations."""

    def __init__(self, db: Session):
        """
        Initialize authentication service.

        Args:
            db: Database session
        """
        self.db = db

    def register_user(self, user_data: UserRegisterRequest) -> User:
        """
        Register a new user account.

        Args:
            user_data: User registration data

        Returns:
            Created user object

        Raises:
            HTTPException: If email or username already exists
        """
        # Check if email already exists
        existing_email = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Check if username already exists
        existing_username = (
            self.db.query(User).filter(User.username == user_data.username.lower()).first()
        )
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

        # Hash password
        password_hash = get_password_hash(user_data.password)

        # Create user object
        new_user = User(
            id=uuid.uuid4(),
            email=user_data.email.lower(),
            username=user_data.username.lower(),
            password_hash=password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            department=user_data.department,
            job_title=user_data.job_title,
            status=UserStatus.PENDING_VERIFICATION,
            is_verified=False,
            is_active=True,
            created_at=datetime.utcnow(),
        )

        # Add to database
        self.db.add(new_user)
        self.db.flush()  # Flush to get the user ID before role assignment

        # Assign default "User" role
        default_role = self.db.query(Role).filter(Role.name == "User").first()
        if default_role:
            new_user.roles.append(default_role)

        self.db.commit()
        self.db.refresh(new_user)

        return new_user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User's email address

        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.email == email.lower()).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: User's username

        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.username == username.lower()).first()

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User's unique identifier

        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.id == user_id).first()


def get_auth_service(db: Session) -> AuthService:
    """
    Get authentication service instance.

    Args:
        db: Database session

    Returns:
        AuthService instance
    """
    return AuthService(db)
