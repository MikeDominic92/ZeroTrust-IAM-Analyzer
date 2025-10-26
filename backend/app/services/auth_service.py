"""
Authentication service for ZeroTrust IAM Analyzer.

This module provides authentication business logic including user registration,
login, token management, and password reset functionality.
"""

import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional

from app.core.logging import get_logger
from app.core.security import get_password_hash, verify_password
from app.models.role import Role
from app.models.session import Session as SessionModel
from app.models.user import User, UserStatus
from app.schemas.auth import UserRegisterRequest
from app.services.cache_service import cache_session
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

logger = get_logger(__name__)


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

    def authenticate_user(
        self, username_or_email: str, password: str, ip_address: Optional[str] = None
    ) -> User:
        """
        Authenticate user with username/email and password.

        This method handles the complete authentication flow including:
        - User lookup by email or username
        - Account lockout checking
        - Password verification
        - Failed login attempt tracking
        - Successful login recording

        Args:
            username_or_email: Username or email address
            password: Plain text password
            ip_address: Optional IP address for login tracking

        Returns:
            Authenticated user object

        Raises:
            HTTPException 401: Invalid credentials (user not found or wrong password)
            HTTPException 403: Account locked due to too many failed attempts
        """
        # Try email first, then username
        user = self.get_user_by_email(username_or_email)
        if not user:
            user = self.get_user_by_username(username_or_email)

        # User not found - return generic error (security best practice)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        # Check if account is locked
        if user.is_account_locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account locked due to too many failed attempts. Please contact support.",
            )

        # Check if account is inactive
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive. Please contact support.",
            )

        # Verify password
        if not verify_password(password, user.password_hash):
            # Record failed attempt (also handles auto-lock at 5 attempts)
            user.record_login_attempt(success=False, ip_address=ip_address)
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        # Successful login - record it (updates last_login_at, resets failed attempts)
        user.record_login_attempt(success=True, ip_address=ip_address)
        self.db.commit()

        return user

    def create_session(
        self,
        user: User,
        access_token_jti: str,
        refresh_token_jti: str,
        expires_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> SessionModel:
        """
        Create new session for user.

        Sessions track JWT token pairs and allow for individual session revocation.
        Each login creates a new session record for audit and revocation purposes.

        Args:
            user: User object
            access_token_jti: Access token JTI (JWT ID claim)
            refresh_token_jti: Refresh token JTI
            expires_at: Session expiration timestamp (matches access token expiry)
            ip_address: Optional IP address where session was created
            user_agent: Optional user agent string for device identification

        Returns:
            Created session object
        """
        new_session = SessionModel(
            id=uuid.uuid4(),
            user_id=user.id,
            token_jti=access_token_jti,
            refresh_token_jti=refresh_token_jti,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            last_activity_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )

        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)

        # Cache session for fast authentication lookups (Task 1.11)
        cache_session(new_session, user)

        return new_session

    def request_password_reset(self, email: str) -> bool:
        """
        Request password reset for user account.

        Generates a secure reset token and stores it with expiration timestamp.
        Returns success regardless of whether user exists to prevent user enumeration.

        Args:
            email: User's email address

        Returns:
            Always returns True to prevent user enumeration

        Security Notes:
            - Generic response prevents user enumeration attacks
            - Token is cryptographically secure (secrets.token_urlsafe)
            - Token expires after 1 hour
            - Only one active reset token per user (overwrites previous)
        """
        # Query user by email (lowercase for case-insensitive lookup)
        user = self.get_user_by_email(email)

        # If user exists, generate and store reset token
        if user:
            # Generate cryptographically secure reset token (256 bits)
            reset_token = secrets.token_urlsafe(32)

            # Set token expiration to 1 hour from now
            expires_at = datetime.utcnow() + timedelta(hours=1)

            # Update user record with reset token and expiration
            user.password_reset_token = reset_token
            user.password_reset_expires = expires_at

            # Commit changes to database
            self.db.commit()

            # Log reset token for testing (no email service configured)
            # In production, this would send an email with a reset link
            logger.info(
                "password_reset_requested",
                user_id=str(user.id),
                email=user.email,
                reset_token=reset_token,
                expires_at=expires_at.isoformat(),
            )

        # Always return True to prevent user enumeration
        # Attackers cannot determine if email exists in system
        return True

    def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """
        Confirm password reset with token and new password.

        Validates reset token, updates user password, and clears reset token.

        Args:
            token: Password reset token
            new_password: New password (plain text, will be hashed)

        Returns:
            True if password reset successful

        Raises:
            HTTPException 400: Invalid or expired reset token
            HTTPException 500: Database error

        Security Notes:
            - Token must exist and not be expired
            - New password is hashed with bcrypt (12 rounds)
            - Reset token cleared after successful reset (single-use)
            - Updates last_password_change timestamp
        """
        # Query user by reset token
        user = self.db.query(User).filter(User.password_reset_token == token).first()

        # Validate token exists
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        # Validate token not expired
        if not user.password_reset_expires or user.password_reset_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        # Hash new password
        new_password_hash = get_password_hash(new_password)

        # Update user password
        user.password_hash = new_password_hash

        # Clear reset token fields (single-use token)
        user.password_reset_token = None
        user.password_reset_expires = None

        # Update last password change timestamp
        user.last_password_change = datetime.utcnow()

        # Commit changes to database
        self.db.commit()

        # Log successful password reset
        logger.info(
            "password_reset_confirmed",
            user_id=str(user.id),
            email=user.email,
        )

        return True


def get_auth_service(db: Session) -> AuthService:
    """
    Get authentication service instance.

    Args:
        db: Database session

    Returns:
        AuthService instance
    """
    return AuthService(db)
