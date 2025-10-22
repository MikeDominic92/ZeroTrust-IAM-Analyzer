"""
Common schemas and base classes for ZeroTrust IAM Analyzer.

This module contains shared Pydantic models, base classes, and common
schemas used across different API endpoints.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

ModelType = TypeVar("ModelType")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
    )


class TimestampedSchema(BaseSchema):
    """Base schema with timestamp fields."""
    
    created_at: datetime = Field(
        ..., 
        description="Timestamp when the record was created"
    )
    updated_at: datetime = Field(
        ..., 
        description="Timestamp when the record was last updated"
    )
    deleted_at: Optional[datetime] = Field(
        None, 
        description="Timestamp when the record was soft deleted"
    )


class UUIDSchema(BaseSchema):
    """Base schema with UUID field."""
    
    id: uuid.UUID = Field(
        ..., 
        description="Unique identifier for the record"
    )


class BaseResponse(BaseSchema, Generic[ModelType]):
    """Base response schema."""
    
    success: bool = Field(
        default=True, 
        description="Whether the operation was successful"
    )
    message: str = Field(
        default="Operation completed successfully", 
        description="Response message"
    )
    data: Optional[ModelType] = Field(
        None, 
        description="Response data"
    )


class PaginatedResponse(BaseSchema, Generic[ModelType]):
    """Paginated response schema."""
    
    items: List[ModelType] = Field(
        ..., 
        description="List of items in the current page"
    )
    total: int = Field(
        ..., 
        description="Total number of items"
    )
    page: int = Field(
        ..., 
        description="Current page number"
    )
    size: int = Field(
        ..., 
        description="Number of items per page"
    )
    pages: int = Field(
        ..., 
        description="Total number of pages"
    )
    has_next: bool = Field(
        ..., 
        description="Whether there is a next page"
    )
    has_prev: bool = Field(
        ..., 
        description="Whether there is a previous page"
    )


class PaginationParams(BaseSchema):
    """Pagination parameters schema."""
    
    page: int = Field(
        default=1, 
        ge=1, 
        description="Page number (1-based)"
    )
    size: int = Field(
        default=20, 
        ge=1, 
        le=100, 
        description="Number of items per page"
    )
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.size


class SortParams(BaseSchema):
    """Sorting parameters schema."""
    
    sort_by: Optional[str] = Field(
        None, 
        description="Field to sort by"
    )
    sort_order: Optional[str] = Field(
        default="asc", 
        pattern="^(asc|desc)$", 
        description="Sort order (asc or desc)"
    )
    
    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        """Validate sort order."""
        if v and v.lower() not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v.lower() if v else "asc"


class FilterParams(BaseSchema):
    """Base filter parameters schema."""
    
    search: Optional[str] = Field(
        None, 
        description="Search term to filter results"
    )
    tags: Optional[List[str]] = Field(
        None, 
        description="Tags to filter by"
    )


class DateRangeFilter(BaseSchema):
    """Date range filter schema."""
    
    start_date: Optional[datetime] = Field(
        None, 
        description="Start date for filtering"
    )
    end_date: Optional[datetime] = Field(
        None, 
        description="End date for filtering"
    )
    
    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v, values):
        """Validate that end_date is after start_date."""
        if v and "start_date" in values and values["start_date"]:
            if v <= values["start_date"]:
                raise ValueError("end_date must be after start_date")
        return v


class ErrorResponse(BaseSchema):
    """Error response schema."""
    
    success: bool = Field(
        default=False, 
        description="Whether the operation was successful"
    )
    error: str = Field(
        ..., 
        description="Error type or code"
    )
    message: str = Field(
        ..., 
        description="Error message"
    )
    details: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional error details"
    )
    request_id: Optional[str] = Field(
        None, 
        description="Request identifier for tracking"
    )


class ValidationErrorResponse(BaseSchema):
    """Validation error response schema."""
    
    success: bool = Field(
        default=False, 
        description="Whether the operation was successful"
    )
    error: str = Field(
        default="validation_error", 
        description="Error type"
    )
    message: str = Field(
        default="Validation failed", 
        description="Error message"
    )
    details: Dict[str, List[str]] = Field(
        ..., 
        description="Field-specific validation errors"
    )


class HealthCheckResponse(BaseSchema):
    """Health check response schema."""
    
    status: str = Field(
        ..., 
        description="Health status (healthy/unhealthy)"
    )
    service: str = Field(
        ..., 
        description="Service name"
    )
    version: str = Field(
        ..., 
        description="Service version"
    )
    environment: Optional[str] = Field(
        None, 
        description="Environment name"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, 
        description="Health check timestamp"
    )


class DatabaseHealthCheck(BaseSchema):
    """Database health check schema."""
    
    status: str = Field(
        ..., 
        description="Database status"
    )
    connection: Optional[str] = Field(
        None, 
        description="Connection status"
    )
    latency_ms: Optional[float] = Field(
        None, 
        description="Database latency in milliseconds"
    )
    error: Optional[str] = Field(
        None, 
        description="Error message if connection failed"
    )


class DetailedHealthCheckResponse(HealthCheckResponse):
    """Detailed health check response schema."""
    
    checks: Dict[str, Any] = Field(
        ..., 
        description="Detailed health check results"
    )
    uptime_seconds: Optional[float] = Field(
        None, 
        description="Service uptime in seconds"
    )


class BulkOperationRequest(BaseSchema):
    """Bulk operation request schema."""
    
    ids: List[uuid.UUID] = Field(
        ..., 
        description="List of item IDs to operate on"
    )
    
    @field_validator("ids")
    @classmethod
    def validate_ids(cls, v):
        """Validate that IDs list is not empty."""
        if not v:
            raise ValueError("ids list cannot be empty")
        if len(v) > 100:
            raise ValueError("Cannot process more than 100 items at once")
        return v


class BulkOperationResponse(BaseSchema):
    """Bulk operation response schema."""
    
    success: bool = Field(
        ..., 
        description="Whether the bulk operation was successful"
    )
    message: str = Field(
        ..., 
        description="Response message"
    )
    processed: int = Field(
        ..., 
        description="Number of items processed"
    )
    successful: int = Field(
        ..., 
        description="Number of successful operations"
    )
    failed: int = Field(
        ..., 
        description="Number of failed operations"
    )
    errors: Optional[List[Dict[str, Any]]] = Field(
        None, 
        description="List of errors for failed operations"
    )


class BulkDeleteRequest(BulkOperationRequest):
    """Bulk delete request schema."""
    
    confirm: bool = Field(
        ..., 
        description="Confirmation for bulk delete operation"
    )
    
    @field_validator("confirm")
    @classmethod
    def validate_confirmation(cls, v):
        """Validate confirmation for bulk delete."""
        if not v:
            raise ValueError("confirm must be True for bulk delete operations")
        return v


class ExportRequest(BaseSchema):
    """Export request schema."""
    
    format: str = Field(
        default="json", 
        pattern="^(json|csv|xlsx)$", 
        description="Export format"
    )
    filters: Optional[Dict[str, Any]] = Field(
        None, 
        description="Filters to apply to export"
    )
    fields: Optional[List[str]] = Field(
        None, 
        description="Specific fields to include in export"
    )


class ExportResponse(BaseSchema):
    """Export response schema."""
    
    download_url: str = Field(
        ..., 
        description="URL to download the exported file"
    )
    filename: str = Field(
        ..., 
        description="Generated filename"
    )
    format: str = Field(
        ..., 
        description="Export format"
    )
    size_bytes: int = Field(
        ..., 
        description="File size in bytes"
    )
    expires_at: datetime = Field(
        ..., 
        description="When the download URL expires"
    )


class MetadataSchema(BaseSchema):
    """Generic metadata schema."""
    
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata"
    )
    tags: Optional[Dict[str, str]] = Field(
        None, 
        description="Tags for categorization"
    )


class VersionedSchema(BaseSchema):
    """Schema with version support."""
    
    version: int = Field(
        default=1, 
        ge=1, 
        description="Version number"
    )