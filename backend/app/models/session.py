"""
Session model for ZeroTrust IAM Analyzer.

This module contains the Session model for JWT token and session management.
Supports multiple concurrent sessions per user with individual session tracking and revocation.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Session(Base):
    """
    Session model for tracking user sessions and JWT tokens.

    Supports multiple concurrent sessions per user with individual revocation capability.
    Each session corresponds to a JWT token pair (access + refresh tokens).
    """

    # Foreign key to user
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID this session belongs to",
    )

    # Token identifiers
    token_jti: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="JWT Token ID (jti claim) for access token identification",
    )

    refresh_token_jti: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="Refresh token JTI for token rotation and refresh flow",
    )

    # Session metadata
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True, comment="IP address where session was created"
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="User agent string for device identification"
    )

    # Session lifecycle
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Session expiration timestamp (matches access token expiry)",
    )

    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether session has been revoked (logout or security event)",
    )

    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when session was revoked",
    )

    last_activity_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of last activity in this session (for idle timeout)",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")

    def revoke(self) -> None:
        """
        Revoke this session.

        Marks the session as revoked and records the revocation timestamp.
        After revocation, the session's tokens will no longer be valid.
        """
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()

    @property
    def is_expired(self) -> bool:
        """Check if session has expired based on expiration timestamp."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if session is currently valid (not revoked and not expired)."""
        return not self.is_revoked and not self.is_expired

    def __repr__(self) -> str:
        """String representation of the Session model."""
        return f"<Session(id={self.id}, user_id={self.user_id}, token_jti={self.token_jti[:8]}..., valid={self.is_valid})>"
