"""
User model for ZeroTrust IAM Analyzer.

This module contains the User model with authentication, profile data,
role-based access control fields, and account status management.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base

if TYPE_CHECKING:
    from .role import Role
    from .session import Session


class UserRole(str, Enum):
    """User role enumeration for role-based access control."""

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    AUDITOR = "auditor"


class UserStatus(str, Enum):
    """User account status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    LOCKED = "locked"


class AuthenticationProvider(str, Enum):
    """Authentication provider enumeration."""

    LOCAL = "local"
    MICROSOFT = "microsoft"
    GOOGLE = "google"
    SAML = "saml"


class User(Base):
    """
    User model for authentication and profile management.

    This model stores user authentication data, profile information,
    role-based access control fields, and account status tracking.
    """

    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="User's email address (unique identifier)",
    )

    username: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False, comment="Unique username for login"
    )

    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="Hashed password (null for external auth providers)"
    )

    auth_provider: Mapped[AuthenticationProvider] = mapped_column(
        SQLEnum(AuthenticationProvider),
        default=AuthenticationProvider.LOCAL,
        nullable=False,
        comment="Authentication provider used by the user",
    )

    provider_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Unique identifier from external auth provider",
    )

    # Profile fields
    first_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="User's first name"
    )

    last_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="User's last name"
    )

    display_name: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="Display name for UI purposes"
    )

    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="URL to user's avatar image"
    )

    phone_number: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="User's phone number"
    )

    department: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="User's department or organization unit"
    )

    job_title: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="User's job title"
    )

    # Role and permissions
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.VIEWER,
        nullable=False,
        index=True,
        comment="User's role for access control",
    )

    permissions: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Additional permissions in JSON format"
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Whether user has superuser privileges"
    )

    # Account status
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus),
        default=UserStatus.PENDING_VERIFICATION,
        nullable=False,
        index=True,
        comment="Current status of the user account",
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Whether user's email is verified"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, index=True, comment="Whether user account is active"
    )

    # Security and tracking
    failed_login_attempts: Mapped[int] = mapped_column(
        default=0, nullable=False, comment="Number of consecutive failed login attempts"
    )

    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp of last successful login",
    )

    last_login_ip: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True, comment="IP address of last login"
    )

    last_password_change: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Timestamp of last password change"
    )

    password_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Timestamp when password expires"
    )

    must_change_password: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether user must change password on next login",
    )

    two_factor_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether two-factor authentication is enabled",
    )

    two_factor_secret: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="Two-factor authentication secret"
    )

    backup_codes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Backup codes for two-factor authentication"
    )

    # Session management
    session_token: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True, comment="Current active session token"
    )

    refresh_token: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="Refresh token for session management"
    )

    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Timestamp when current token expires"
    )

    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Administrative notes about the user"
    )

    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True, comment="ID of user who created this account"
    )

    # Relationships
    scans: Mapped[List["Scan"]] = relationship(
        "Scan", back_populates="created_by_user", cascade="all, delete-orphan", lazy="dynamic"
    )

    # Many-to-many relationship with roles for flexible RBAC
    roles: Mapped[List["Role"]] = relationship(
        secondary="user_roles", back_populates="users", lazy="dynamic"
    )

    # One-to-many relationship with sessions for multi-session support
    sessions: Mapped[List["Session"]] = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan", lazy="dynamic"
    )

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name or self.username

    @property
    def is_account_locked(self) -> bool:
        """Check if account is locked due to security reasons."""
        return self.status == UserStatus.LOCKED or self.failed_login_attempts >= 5

    def lock_account(self) -> None:
        """Lock the user account."""
        self.status = UserStatus.LOCKED

    def unlock_account(self) -> None:
        """Unlock the user account."""
        self.status = UserStatus.ACTIVE
        self.failed_login_attempts = 0

    def record_login_attempt(self, success: bool, ip_address: str = None) -> None:
        """
        Record a login attempt.

        Args:
            success: Whether the login attempt was successful
            ip_address: IP address of the login attempt
        """
        if success:
            self.last_login_at = datetime.utcnow()
            self.last_login_ip = ip_address
            self.failed_login_attempts = 0

            # Auto-activate pending verification account
            if self.status == UserStatus.PENDING_VERIFICATION:
                self.status = UserStatus.ACTIVE
                self.is_verified = True
        else:
            self.failed_login_attempts += 1

            # Lock account after too many failed attempts
            if self.failed_login_attempts >= 5:
                self.lock_account()

    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission.

        Args:
            permission: Permission to check

        Returns:
            True if user has the permission
        """
        if self.is_superuser:
            return True

        # Check role-based permissions
        role_permissions = {
            UserRole.ADMIN: ["read", "write", "delete", "manage_users", "manage_system"],
            UserRole.ANALYST: ["read", "write", "analyze"],
            UserRole.AUDITOR: ["read", "audit"],
            UserRole.VIEWER: ["read"],
        }

        return permission in role_permissions.get(self.role, [])

    def __repr__(self) -> str:
        """String representation of the User model."""
        return (
            f"<User(id={self.id}, username={self.username}, email={self.email}, role={self.role})>"
        )
