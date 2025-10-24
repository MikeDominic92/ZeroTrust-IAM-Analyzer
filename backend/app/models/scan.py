"""
Scan model for ZeroTrust IAM Analyzer.

This module contains the Scan model for security scan records,
including scan status, configuration, timestamps, and results summary.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy import JSON, Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class ScanStatus(str, Enum):
    """Scan status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ScanType(str, Enum):
    """Scan type enumeration."""

    GOOGLE_CLOUD_IAM = "google_cloud_iam"
    GOOGLE_WORKSPACE = "google_workspace"
    COMPREHENSIVE = "comprehensive"


class ScanPriority(str, Enum):
    """Scan priority enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Scan(Base):
    """
    Scan model for security scan records.

    This model stores scan configuration, execution status,
    timing information, and results summary for IAM policy analysis.
    """

    # Basic scan information
    name: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True, comment="Human-readable name for the scan"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Detailed description of the scan purpose"
    )

    scan_type: Mapped[ScanType] = mapped_column(
        SQLEnum(ScanType), nullable=False, index=True, comment="Type of scan being performed"
    )

    status: Mapped[ScanStatus] = mapped_column(
        SQLEnum(ScanStatus),
        default=ScanStatus.PENDING,
        nullable=False,
        index=True,
        comment="Current status of the scan",
    )

    priority: Mapped[ScanPriority] = mapped_column(
        SQLEnum(ScanPriority),
        default=ScanPriority.MEDIUM,
        nullable=False,
        index=True,
        comment="Priority level of the scan",
    )

    # Scan configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="Scan configuration parameters in JSON format"
    )

    target_scope: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Target scope description (subscription, project, etc.)"
    )

    target_resource_id: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        index=True,
        comment="Identifier of the target resource being scanned",
    )

    credentials_used: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="Type of credentials used for the scan"
    )

    # Timing information
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Scheduled start time for the scan",
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True, comment="Actual start time of the scan"
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True, comment="Completion time of the scan"
    )

    duration_seconds: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Total duration of the scan in seconds"
    )

    timeout_seconds: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=3600, comment="Maximum allowed duration in seconds"
    )

    # Progress tracking
    progress_percentage: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False, comment="Progress percentage (0-100)"
    )

    current_step: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="Current step being processed"
    )

    total_steps: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Total number of steps in the scan"
    )

    completed_steps: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=0, comment="Number of completed steps"
    )

    # Results summary
    total_policies_scanned: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=0, comment="Total number of policies scanned"
    )

    total_resources_analyzed: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=0, comment="Total number of resources analyzed"
    )

    total_findings: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=0, comment="Total number of findings identified"
    )

    critical_findings: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=0, comment="Number of critical severity findings"
    )

    high_findings: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=0, comment="Number of high severity findings"
    )

    medium_findings: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=0, comment="Number of medium severity findings"
    )

    low_findings: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=0, comment="Number of low severity findings"
    )

    risk_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, index=True, comment="Overall risk score (0-100)"
    )

    compliance_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, index=True, comment="Overall compliance score (0-100)"
    )

    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Error message if scan failed"
    )

    error_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="Detailed error information in JSON format"
    )

    retry_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="Number of retry attempts"
    )

    max_retries: Mapped[int] = mapped_column(
        Integer, default=3, nullable=False, comment="Maximum number of retry attempts"
    )

    # Scan metadata
    tags: Mapped[Optional[Dict[str, str]]] = mapped_column(
        JSON, nullable=True, comment="Tags for categorizing and filtering scans"
    )

    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="Additional metadata in JSON format"
    )

    # External references
    external_scan_id: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        index=True,
        comment="External scan identifier from scanning tools",
    )

    parent_scan_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID of parent scan if this is a sub-scan",
    )

    # Ownership and tracking
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True, comment="ID of user who initiated the scan"
    )

    # Flags
    is_recurring: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Whether this is a recurring scan"
    )

    is_baseline: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Whether this scan serves as a baseline"
    )

    notify_on_completion: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="Whether to notify on scan completion"
    )

    # Relationships
    created_by_user: Mapped["User"] = relationship("User", back_populates="scans")

    policies: Mapped[list["Policy"]] = relationship(
        "Policy", back_populates="scan", cascade="all, delete-orphan", lazy="dynamic"
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation", back_populates="scan", cascade="all, delete-orphan", lazy="dynamic"
    )

    @property
    def is_running(self) -> bool:
        """Check if scan is currently running."""
        return self.status == ScanStatus.RUNNING

    @property
    def is_completed(self) -> bool:
        """Check if scan has completed (successfully or with failure)."""
        return self.status in [
            ScanStatus.COMPLETED,
            ScanStatus.FAILED,
            ScanStatus.CANCELLED,
            ScanStatus.TIMEOUT,
        ]

    @property
    def is_successful(self) -> bool:
        """Check if scan completed successfully."""
        return self.status == ScanStatus.COMPLETED

    @property
    def can_retry(self) -> bool:
        """Check if scan can be retried."""
        return (
            self.status in [ScanStatus.FAILED, ScanStatus.TIMEOUT]
            and self.retry_count < self.max_retries
        )

    def start_scan(self) -> None:
        """Mark scan as started."""
        self.status = ScanStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.progress_percentage = 0.0

    def complete_scan(self) -> None:
        """Mark scan as completed successfully."""
        self.status = ScanStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress_percentage = 100.0

        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())

    def fail_scan(self, error_message: str = None, error_details: Dict[str, Any] = None) -> None:
        """Mark scan as failed."""
        self.status = ScanStatus.FAILED
        self.completed_at = datetime.utcnow()

        if error_message:
            self.error_message = error_message

        if error_details:
            self.error_details = error_details

        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())

    def cancel_scan(self) -> None:
        """Cancel the scan."""
        self.status = ScanStatus.CANCELLED
        self.completed_at = datetime.utcnow()

        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())

    def update_progress(self, percentage: float, current_step: str = None) -> None:
        """
        Update scan progress.

        Args:
            percentage: Progress percentage (0-100)
            current_step: Description of current step
        """
        self.progress_percentage = max(0.0, min(100.0, percentage))

        if current_step:
            self.current_step = current_step

    def increment_step(self) -> None:
        """Increment the completed steps counter."""
        if self.completed_steps is not None:
            self.completed_steps += 1

            if self.total_steps and self.total_steps > 0:
                self.progress_percentage = (self.completed_steps / self.total_steps) * 100.0

    def add_finding(self, severity: str) -> None:
        """
        Add a finding to the scan results.

        Args:
            severity: Severity level of the finding
        """
        self.total_findings = (self.total_findings or 0) + 1

        severity = severity.lower()
        if severity == "critical":
            self.critical_findings = (self.critical_findings or 0) + 1
        elif severity == "high":
            self.high_findings = (self.high_findings or 0) + 1
        elif severity == "medium":
            self.medium_findings = (self.medium_findings or 0) + 1
        elif severity == "low":
            self.low_findings = (self.low_findings or 0) + 1

    def __repr__(self) -> str:
        """String representation of the Scan model."""
        return (
            f"<Scan(id={self.id}, name={self.name}, type={self.scan_type}, status={self.status})>"
        )
