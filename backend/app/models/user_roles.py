"""
User-Roles association table for ZeroTrust IAM Analyzer.

This module defines the many-to-many relationship between users and roles.
Allows users to have multiple roles and roles to be assigned to multiple users.
"""

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
        comment="User ID in the user-role relationship",
    ),
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Role ID in the user-role relationship",
    ),
)
