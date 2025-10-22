"""
Recommendation model for ZeroTrust IAM Analyzer.

This module contains the Recommendation model for security recommendations,
including severity, priority levels, implementation status, and policy relationships.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List

from sqlalchemy import Boolean, Enum as SQLEnum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class RecommendationType(str, Enum):
    """Recommendation type enumeration."""
    SECURITY_HARDENING = "security_hardening"
    COMPLIANCE = "compliance"
    BEST_PRACTICE = "best_practice"
    RISK_MITIGATION = "risk_mitigation"
    ACCESS_CONTROL = "access_control"
    MONITORING = "monitoring"
    GOVERNANCE = "governance"


class Severity(str, Enum):
    """Severity level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Priority(str, Enum):
    """Priority level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ImplementationStatus(str, Enum):
    """Implementation status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    NOT_APPLICABLE = "not_applicable"


class Recommendation(Base):
    """
    Recommendation model for security recommendations.
    
    This model stores security recommendations generated from policy analysis,
    including severity, priority, implementation status, and related policies.
    """
    
    # Basic recommendation information
    title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True,
        comment="Recommendation title"
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Detailed description of the recommendation"
    )
    
    recommendation_type: Mapped[RecommendationType] = mapped_column(
        SQLEnum(RecommendationType),
        nullable=False,
        index=True,
        comment="Type of recommendation"
    )
    
    severity: Mapped[Severity] = mapped_column(
        SQLEnum(Severity),
        nullable=False,
        index=True,
        comment="Severity level of the recommendation"
    )
    
    priority: Mapped[Priority] = mapped_column(
        SQLEnum(Priority),
        nullable=False,
        index=True,
        comment="Priority level for implementation"
    )
    
    # Classification and categorization
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Recommendation category"
    )
    
    subcategory: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Recommendation subcategory"
    )
    
    framework: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Security framework reference (NIST, CIS, etc.)"
    )
    
    control_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Control identifier from security framework"
    )
    
    tags: Mapped[Optional[Dict[str, str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Tags for categorization and filtering"
    )
    
    # Implementation guidance
    implementation_steps: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Step-by-step implementation instructions"
    )
    
    remediation_code: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Code snippets or commands for remediation"
    )
    
    rollback_procedure: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Procedure to rollback changes if needed"
    )
    
    testing_instructions: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Instructions to test the implementation"
    )
    
    # Impact assessment
    impact_assessment: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Assessment of potential impact"
    )
    
    risk_reduction: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Estimated risk reduction percentage"
    )
    
    implementation_effort: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Estimated implementation effort (low/medium/high)"
    )
    
    implementation_cost: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Estimated implementation cost (low/medium/high)"
    )
    
    # Status tracking
    implementation_status: Mapped[ImplementationStatus] = mapped_column(
        SQLEnum(ImplementationStatus),
        default=ImplementationStatus.PENDING,
        nullable=False,
        index=True,
        comment="Current implementation status"
    )
    
    assigned_to: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        index=True,
        comment="Person or team assigned for implementation"
    )
    
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Due date for implementation"
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp when implementation was completed"
    )
    
    # Rejection and deferral
    rejection_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Reason for rejecting the recommendation"
    )
    
    deferral_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Reason for deferring the recommendation"
    )
    
    deferred_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date when deferred recommendation should be revisited"
    )
    
    # External references
    external_reference: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="External reference or documentation link"
    )
    
    cve_id: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        index=True,
        comment="Related CVE identifier if applicable"
    )
    
    # Business context
    business_impact: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Business impact description"
    )
    
    business_justification: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Business justification for implementation"
    )
    
    # Monitoring and verification
    verification_method: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Method to verify implementation"
    )
    
    monitoring_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether ongoing monitoring is required"
    )
    
    success_criteria: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Success criteria for implementation"
    )
    
    # Additional metadata
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional metadata in JSON format"
    )
    
    # Relationships
    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scan.id"),
        nullable=False,
        index=True,
        comment="ID of the scan that generated this recommendation"
    )
    
    policy_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policy.id"),
        nullable=True,
        index=True,
        comment="ID of the related policy (if applicable)"
    )
    
    scan: Mapped["Scan"] = relationship(
        "Scan",
        back_populates="recommendations"
    )
    
    policy: Mapped[Optional["Policy"]] = relationship(
        "Policy",
        back_populates="recommendations"
    )
    
    @property
    def is_critical(self) -> bool:
        """Check if recommendation is critical."""
        return self.severity == Severity.CRITICAL or self.priority == Priority.URGENT
    
    @property
    def is_overdue(self) -> bool:
        """Check if recommendation is overdue."""
        if not self.due_date:
            return False
        return self.due_date < datetime.utcnow() and self.implementation_status not in [
            ImplementationStatus.COMPLETED,
            ImplementationStatus.REJECTED,
            ImplementationStatus.NOT_APPLICABLE
        ]
    
    @property
    def can_implement(self) -> bool:
        """Check if recommendation can be implemented."""
        return self.implementation_status in [
            ImplementationStatus.PENDING,
            ImplementationStatus.DEFERRED
        ]
    
    @property
    def is_completed(self) -> bool:
        """Check if recommendation is completed."""
        return self.implementation_status == ImplementationStatus.COMPLETED
    
    @property
    def days_overdue(self) -> Optional[int]:
        """Calculate days overdue if past due date."""
        if not self.due_date or not self.is_overdue:
            return None
        
        delta = datetime.utcnow() - self.due_date
        return delta.days
    
    def implement(self, implemented_by: str = None) -> None:
        """
        Mark recommendation as implemented.
        
        Args:
            implemented_by: Person who implemented the recommendation
        """
        self.implementation_status = ImplementationStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        
        if implemented_by:
            self.assigned_to = implemented_by
    
    def reject(self, reason: str) -> None:
        """
        Reject the recommendation.
        
        Args:
            reason: Reason for rejection
        """
        self.implementation_status = ImplementationStatus.REJECTED
        self.rejection_reason = reason
    
    def defer(self, reason: str, defer_until: datetime = None) -> None:
        """
        Defer the recommendation.
        
        Args:
            reason: Reason for deferral
            defer_until: Date to revisit the recommendation
        """
        self.implementation_status = ImplementationStatus.DEFERRED
        self.deferral_reason = reason
        
        if defer_until:
            self.deferred_until = defer_until
        else:
            # Default defer for 30 days
            from datetime import timedelta
            self.deferred_until = datetime.utcnow() + timedelta(days=30)
    
    def start_implementation(self, assigned_to: str = None, due_date: datetime = None) -> None:
        """
        Start implementation of the recommendation.
        
        Args:
            assigned_to: Person or team assigned for implementation
            due_date: Due date for implementation
        """
        self.implementation_status = ImplementationStatus.IN_PROGRESS
        
        if assigned_to:
            self.assigned_to = assigned_to
        
        if due_date:
            self.due_date = due_date
    
    def update_priority(self, new_priority: Priority) -> None:
        """
        Update the priority of the recommendation.
        
        Args:
            new_priority: New priority level
        """
        self.priority = new_priority
    
    def extend_due_date(self, days: int) -> None:
        """
        Extend the due date by specified number of days.
        
        Args:
            days: Number of days to extend
        """
        if self.due_date:
            from datetime import timedelta
            self.due_date = self.due_date + timedelta(days=days)
        else:
            from datetime import timedelta
            self.due_date = datetime.utcnow() + timedelta(days=days)
    
    def add_implementation_step(self, step: Dict[str, Any]) -> None:
        """
        Add an implementation step to the recommendation.
        
        Args:
            step: Implementation step dictionary
        """
        if self.implementation_steps is None:
            self.implementation_steps = []
        
        self.implementation_steps.append(step)
    
    def calculate_risk_reduction(self, current_risk_score: float, target_risk_score: float) -> None:
        """
        Calculate and set the risk reduction percentage.
        
        Args:
            current_risk_score: Current risk score (0-100)
            target_risk_score: Target risk score after implementation (0-100)
        """
        if current_risk_score > 0:
            reduction = ((current_risk_score - target_risk_score) / current_risk_score) * 100
            self.risk_reduction = max(0.0, min(100.0, reduction))
    
    def __repr__(self) -> str:
        """String representation of the Recommendation model."""
        return f"<Recommendation(id={self.id}, title={self.title}, severity={self.severity}, status={self.implementation_status})>"