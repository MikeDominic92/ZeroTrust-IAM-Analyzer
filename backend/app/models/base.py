"""
Base model for ZeroTrust IAM Analyzer database models.

This module contains the abstract base class with common fields
and functionality that all other models will inherit from.
"""

import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Abstract base class for all database models."""
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="Unique identifier for the record"
    )
    
    # Timestamp fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Timestamp when the record was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
        comment="Timestamp when the record was last updated"
    )
    
    # Soft delete field
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp when the record was soft deleted"
    )
    
    # Version for optimistic locking
    version: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
        comment="Version number for optimistic locking"
    )
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower()
    
    def to_dict(self, exclude_fields: list[str] = None) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Args:
            exclude_fields: List of field names to exclude from the output
            
        Returns:
            Dictionary representation of the model
        """
        exclude_fields = exclude_fields or []
        result = {}
        
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif isinstance(value, uuid.UUID):
                    value = str(value)
                result[column.name] = value
                
        return result
    
    def update_from_dict(self, data: Dict[str, Any], exclude_fields: list[str] = None) -> None:
        """
        Update model instance from dictionary.
        
        Args:
            data: Dictionary with field values to update
            exclude_fields: List of field names to exclude from updating
        """
        exclude_fields = exclude_fields or ['id', 'created_at', 'updated_at']
        
        for key, value in data.items():
            if key not in exclude_fields and hasattr(self, key):
                setattr(self, key, value)
    
    def soft_delete(self) -> None:
        """Mark the record as soft deleted."""
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore a soft deleted record."""
        self.deleted_at = None
    
    @property
    def is_deleted(self) -> bool:
        """Check if the record is soft deleted."""
        return self.deleted_at is not None
    
    def increment_version(self) -> None:
        """Increment the version number for optimistic locking."""
        self.version += 1
    
    def __repr__(self) -> str:
        """String representation of the model."""
        class_name = self.__class__.__name__
        return f"<{class_name}(id={self.id}, created_at={self.created_at})>"