"""
Role model for ZeroTrust IAM Analyzer.

This module contains the Role model for flexible role-based access control (RBAC).
Supports dynamic role creation with custom permissions.
"""

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Role(Base):
    """
    Role model for role-based access control.

    Supports dynamic role creation with custom permissions for flexible RBAC.
    Roles can be system-defined (protected from deletion) or custom-created.
    """

    # Core fields
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique role name (e.g., 'Admin', 'Analyst', 'Viewer')",
    )

    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Human-readable role name for UI display",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Role description and purpose"
    )

    # Permissions
    permissions: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="JSON array of permission strings (e.g., ['read', 'write', 'delete'])",
    )

    # Role metadata
    is_system_role: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether role is system-defined (cannot be deleted)",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether role is active and can be assigned to users",
    )

    # Relationships
    users: Mapped[List["User"]] = relationship(
        secondary="user_roles", back_populates="roles", lazy="dynamic"
    )

    def __repr__(self) -> str:
        """String representation of the Role model."""
        return f"<Role(id={self.id}, name={self.name}, display_name={self.display_name})>"
