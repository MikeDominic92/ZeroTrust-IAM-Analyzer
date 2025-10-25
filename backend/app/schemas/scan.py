"""
Scan schemas for ZeroTrust IAM Analyzer.

This module contains Pydantic schemas for security scan management,
including scan configuration, execution, and results.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from .common import (
    BaseResponse,
    BaseSchema,
    DateRangeFilter,
    PaginatedResponse,
    TimestampedSchema,
    UUIDSchema,
)


class ScanStatus(BaseSchema):
    """Scan status enumeration schema."""

    PENDING: str = "pending"
    RUNNING: str = "running"
    COMPLETED: str = "completed"
    FAILED: str = "failed"
    CANCELLED: str = "cancelled"
    TIMEOUT: str = "timeout"


class ScanType(BaseSchema):
    """Scan type enumeration schema."""

    MICROSOFT_ENTRA: str = "microsoft_entra"
    GOOGLE_CLOUD_IAM: str = "google_cloud_iam"
    AWS_IAM: str = "aws_iam"
    AZURE_AD: str = "azure_ad"
    COMPREHENSIVE: str = "comprehensive"


class ScanPriority(BaseSchema):
    """Scan priority enumeration schema."""

    LOW: str = "low"
    MEDIUM: str = "medium"
    HIGH: str = "high"
    CRITICAL: str = "critical"


# Base Scan Schemas
class ScanBase(BaseSchema):
    """Base scan schema with common fields."""

    name: str = Field(..., min_length=1, max_length=200, description="Scan name")
    description: Optional[str] = Field(None, description="Scan description")
    scan_type: str = Field(..., description="Type of scan")
    priority: str = Field(default="medium", description="Scan priority")
    target_scope: Optional[str] = Field(None, description="Target scope description")
    target_resource_id: Optional[str] = Field(None, description="Target resource ID")
    config: Optional[Dict[str, Any]] = Field(None, description="Scan configuration")
    tags: Optional[Dict[str, str]] = Field(None, description="Scan tags")
    notify_on_completion: bool = Field(default=True, description="Notify on completion")


class ScanCreate(ScanBase):
    """Scan creation schema."""

    credentials_used: Optional[str] = Field(None, description="Credentials to use")
    scheduled_at: Optional[datetime] = Field(None, description="Schedule scan for later")
    timeout_seconds: Optional[int] = Field(
        default=3600, ge=60, le=86400, description="Timeout in seconds"
    )
    is_recurring: bool = Field(default=False, description="Whether scan is recurring")

    @field_validator("scheduled_at")
    @classmethod
    def validate_scheduled_at(cls, v):
        """Validate scheduled time is in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError("Scheduled time must be in the future")
        return v


class ScanUpdate(BaseSchema):
    """Scan update schema."""

    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Scan name")
    description: Optional[str] = Field(None, description="Scan description")
    priority: Optional[str] = Field(None, description="Scan priority")
    config: Optional[Dict[str, Any]] = Field(None, description="Scan configuration")
    tags: Optional[Dict[str, str]] = Field(None, description="Scan tags")
    notify_on_completion: Optional[bool] = Field(None, description="Notify on completion")
    scheduled_at: Optional[datetime] = Field(None, description="Schedule scan for later")
    timeout_seconds: Optional[int] = Field(None, ge=60, le=86400, description="Timeout in seconds")

    @field_validator("scheduled_at")
    @classmethod
    def validate_scheduled_at(cls, v):
        """Validate scheduled time is in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError("Scheduled time must be in the future")
        return v


# Scan Configuration Schemas
class MicrosoftEntraConfig(BaseSchema):
    """Microsoft Entra ID scan configuration."""

    tenant_id: str = Field(..., description="Azure tenant ID")
    client_id: str = Field(..., description="Azure client ID")
    client_secret: str = Field(..., description="Azure client secret")
    subscription_id: Optional[str] = Field(None, description="Azure subscription ID")
    resource_groups: Optional[List[str]] = Field(None, description="Resource groups to scan")
    include_builtin_policies: bool = Field(default=False, description="Include built-in policies")
    exclude_system_managed: bool = Field(
        default=True, description="Exclude system-managed policies"
    )


class GoogleCloudConfig(BaseSchema):
    """Google Cloud IAM scan configuration."""

    project_id: str = Field(..., description="GCP project ID")
    service_account_key: Dict[str, Any] = Field(..., description="Service account key JSON")
    organizations: Optional[List[str]] = Field(None, description="Organization IDs to scan")
    folders: Optional[List[str]] = Field(None, description="Folder IDs to scan")
    include_service_accounts: bool = Field(default=True, description="Include service accounts")
    include_builtin_roles: bool = Field(default=False, description="Include built-in roles")


class AWSConfig(BaseSchema):
    """AWS IAM scan configuration."""

    access_key_id: str = Field(..., description="AWS access key ID")
    secret_access_key: str = Field(..., description="AWS secret access key")
    region: str = Field(default="us-east-1", description="AWS region")
    account_id: Optional[str] = Field(None, description="AWS account ID")
    roles_arn: Optional[List[str]] = Field(None, description="Specific role ARNs to scan")
    include_managed_policies: bool = Field(default=True, description="Include managed policies")


class ComprehensiveConfig(BaseSchema):
    """Comprehensive multi-cloud scan configuration."""

    azure_config: Optional[MicrosoftEntraConfig] = Field(None, description="Azure configuration")
    gcp_config: Optional[GoogleCloudConfig] = Field(None, description="GCP configuration")
    aws_config: Optional[AWSConfig] = Field(None, description="AWS configuration")
    parallel_execution: bool = Field(default=True, description="Execute scans in parallel")
    fail_fast: bool = Field(default=False, description="Stop on first failure")


# Scan Execution Schemas
class ScanExecutionRequest(BaseSchema):
    """Scan execution request schema."""

    scan_id: uuid.UUID = Field(..., description="Scan ID to execute")
    force_restart: bool = Field(default=False, description="Force restart if already running")
    override_config: Optional[Dict[str, Any]] = Field(None, description="Override configuration")


class ScanExecutionResponse(BaseSchema):
    """Scan execution response schema."""

    scan_id: uuid.UUID = Field(..., description="Scan ID")
    execution_id: str = Field(..., description="Execution ID")
    status: str = Field(..., description="Execution status")
    started_at: datetime = Field(..., description="Start time")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in seconds")
    message: str = Field(..., description="Execution message")


class ScanProgress(BaseSchema):
    """Scan progress schema."""

    scan_id: uuid.UUID = Field(..., description="Scan ID")
    status: str = Field(..., description="Current status")
    progress_percentage: float = Field(..., ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = Field(None, description="Current step")
    total_steps: Optional[int] = Field(None, description="Total steps")
    completed_steps: Optional[int] = Field(None, description="Completed steps")
    started_at: Optional[datetime] = Field(None, description="Start time")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion")
    message: Optional[str] = Field(None, description="Status message")


# Response Schemas
class ScanResponse(UUIDSchema, TimestampedSchema, ScanBase):
    """Scan response schema."""

    status: str = Field(..., description="Scan status")
    created_by: uuid.UUID = Field(..., description="User who created the scan")
    started_at: Optional[datetime] = Field(None, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    duration_seconds: Optional[int] = Field(None, description="Duration in seconds")
    progress_percentage: float = Field(..., description="Progress percentage")
    current_step: Optional[str] = Field(None, description="Current step")
    total_steps: Optional[int] = Field(None, description="Total steps")
    completed_steps: Optional[int] = Field(None, description="Completed steps")

    # Results summary
    total_policies_scanned: Optional[int] = Field(None, description="Total policies scanned")
    total_resources_analyzed: Optional[int] = Field(None, description="Total resources analyzed")
    total_findings: Optional[int] = Field(None, description="Total findings")
    critical_findings: Optional[int] = Field(None, description="Critical findings")
    high_findings: Optional[int] = Field(None, description="High findings")
    medium_findings: Optional[int] = Field(None, description="Medium findings")
    low_findings: Optional[int] = Field(None, description="Low findings")
    risk_score: Optional[float] = Field(None, description="Overall risk score")
    compliance_score: Optional[float] = Field(None, description="Overall compliance score")

    # Error handling
    error_message: Optional[str] = Field(None, description="Error message")
    retry_count: int = Field(..., description="Retry count")
    max_retries: int = Field(..., description="Maximum retries")

    # Flags
    is_recurring: bool = Field(..., description="Whether scan is recurring")
    is_baseline: bool = Field(..., description="Whether scan is baseline")
    external_scan_id: Optional[str] = Field(None, description="External scan ID")
    parent_scan_id: Optional[uuid.UUID] = Field(None, description="Parent scan ID")

    # Computed properties
    is_running: bool = Field(..., description="Whether scan is running")
    is_completed: bool = Field(..., description="Whether scan is completed")
    is_successful: bool = Field(..., description="Whether scan was successful")
    can_retry: bool = Field(..., description="Whether scan can be retried")

    model_config = {"from_attributes": True}


class ScanSummary(BaseSchema):
    """Scan summary schema for list views."""

    id: uuid.UUID = Field(..., description="Scan ID")
    name: str = Field(..., description="Scan name")
    scan_type: str = Field(..., description="Scan type")
    status: str = Field(..., description="Scan status")
    priority: str = Field(..., description="Scan priority")
    progress_percentage: float = Field(..., description="Progress percentage")
    risk_score: Optional[float] = Field(None, description="Risk score")
    total_findings: Optional[int] = Field(None, description="Total findings")
    created_at: datetime = Field(..., description="Creation time")
    started_at: Optional[datetime] = Field(None, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    duration_seconds: Optional[int] = Field(None, description="Duration")
    created_by: uuid.UUID = Field(..., description="Creator user ID")

    model_config = {"from_attributes": True}


class ScanDetail(ScanResponse):
    """Detailed scan response schema."""

    credentials_used: Optional[str] = Field(None, description="Credentials used")
    timeout_seconds: Optional[int] = Field(None, description="Timeout in seconds")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


# Scan Comparison Schemas
class ScanComparisonRequest(BaseSchema):
    """Scan comparison request schema."""

    baseline_scan_id: uuid.UUID = Field(..., description="Baseline scan ID")
    comparison_scan_id: uuid.UUID = Field(..., description="Comparison scan ID")
    compare_policies: bool = Field(default=True, description="Compare policies")
    compare_findings: bool = Field(default=True, description="Compare findings")
    compare_risk_scores: bool = Field(default=True, description="Compare risk scores")


class ScanComparisonResult(BaseSchema):
    """Scan comparison result schema."""

    baseline_scan: ScanSummary = Field(..., description="Baseline scan")
    comparison_scan: ScanSummary = Field(..., description="Comparison scan")
    policies_added: int = Field(..., description="Number of policies added")
    policies_removed: int = Field(..., description="Number of policies removed")
    policies_modified: int = Field(..., description="Number of policies modified")
    findings_added: int = Field(..., description="Number of findings added")
    findings_resolved: int = Field(..., description="Number of findings resolved")
    risk_score_change: float = Field(..., description="Risk score change")
    compliance_score_change: float = Field(..., description="Compliance score change")
    comparison_timestamp: datetime = Field(..., description="Comparison timestamp")


# Scan Scheduling Schemas
class ScanSchedule(BaseSchema):
    """Scan schedule schema."""

    scan_id: uuid.UUID = Field(..., description="Scan ID")
    schedule_type: str = Field(..., description="Schedule type (daily, weekly, monthly)")
    interval: int = Field(..., ge=1, description="Interval between scans")
    next_run: datetime = Field(..., description="Next scheduled run")
    timezone: str = Field(default="UTC", description="Timezone")
    is_active: bool = Field(default=True, description="Whether schedule is active")
    max_runs: Optional[int] = Field(None, description="Maximum number of runs")


class ScanScheduleCreate(BaseSchema):
    """Scan schedule creation schema."""

    scan_id: uuid.UUID = Field(..., description="Scan ID")
    schedule_type: str = Field(..., description="Schedule type")
    interval: int = Field(..., ge=1, description="Interval")
    start_date: datetime = Field(..., description="Start date")
    timezone: str = Field(default="UTC", description="Timezone")
    max_runs: Optional[int] = Field(None, description="Maximum runs")

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, v):
        """Validate start date is in the future."""
        if v <= datetime.utcnow():
            raise ValueError("Start date must be in the future")
        return v


# Scan Statistics Schemas
class ScanStats(BaseSchema):
    """Scan statistics schema."""

    total_scans: int = Field(..., description="Total scans")
    running_scans: int = Field(..., description="Running scans")
    completed_scans: int = Field(..., description="Completed scans")
    failed_scans: int = Field(..., description="Failed scans")
    scans_by_type: Dict[str, int] = Field(..., description="Scans by type")
    scans_by_status: Dict[str, int] = Field(..., description="Scans by status")
    average_duration: Optional[float] = Field(None, description="Average duration in seconds")
    total_findings: int = Field(..., description="Total findings across all scans")
    high_risk_scans: int = Field(..., description="Scans with high risk score")
    recent_scans: int = Field(..., description="Scans in last 24 hours")


class ScanTypeStats(BaseSchema):
    """Scan type statistics schema."""

    scan_type: str = Field(..., description="Scan type")
    total_scans: int = Field(..., description="Total scans")
    successful_scans: int = Field(..., description="Successful scans")
    failed_scans: int = Field(..., description="Failed scans")
    average_duration: Optional[float] = Field(None, description="Average duration")
    average_risk_score: Optional[float] = Field(None, description="Average risk score")
    total_policies_scanned: int = Field(..., description="Total policies scanned")
    total_findings: int = Field(..., description="Total findings")


# Response Types
class ScanListResponse(PaginatedResponse[ScanSummary]):
    """Scan list response schema."""

    pass


class ScanDetailResponse(BaseResponse[ScanDetail]):
    """Scan detail response schema."""

    pass


class ScanProgressResponse(BaseResponse[ScanProgress]):
    """Scan progress response schema."""

    pass


class ScanComparisonResponse(BaseResponse[ScanComparisonResult]):
    """Scan comparison response schema."""

    pass


class ScanStatsResponse(BaseResponse[ScanStats]):
    """Scan statistics response schema."""

    pass


# Bulk Operations
class BulkScanOperation(BaseSchema):
    """Bulk scan operation schema."""

    scan_ids: List[uuid.UUID] = Field(..., description="List of scan IDs")
    operation: str = Field(..., description="Operation type")

    @field_validator("scan_ids")
    @classmethod
    def validate_scan_ids(cls, v):
        """Validate scan IDs list."""
        if not v:
            raise ValueError("scan_ids cannot be empty")
        if len(v) > 20:
            raise ValueError("Cannot operate on more than 20 scans at once")
        return v


class BulkScanResponse(BaseSchema):
    """Bulk scan operation response schema."""

    success: bool = Field(..., description="Whether operation was successful")
    message: str = Field(..., description="Response message")
    processed: int = Field(..., description="Number of scans processed")
    successful: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="Error details")


# Scan Filters
class ScanFilter(BaseSchema, DateRangeFilter):
    """Scan filter schema."""

    scan_type: Optional[str] = Field(None, description="Filter by scan type")
    status: Optional[str] = Field(None, description="Filter by status")
    priority: Optional[str] = Field(None, description="Filter by priority")
    created_by: Optional[uuid.UUID] = Field(None, description="Filter by creator")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    min_risk_score: Optional[float] = Field(None, ge=0, le=100, description="Minimum risk score")
    max_risk_score: Optional[float] = Field(None, ge=0, le=100, description="Maximum risk score")
    has_findings: Optional[bool] = Field(None, description="Filter scans with findings")
    is_baseline: Optional[bool] = Field(None, description="Filter baseline scans")
