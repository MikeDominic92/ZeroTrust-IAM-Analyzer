"""
Policy model for ZeroTrust IAM Analyzer.

This module contains the Policy model for IAM policy data from different sources,
including policy metadata, classification, risk scoring, and relationships.
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


class PolicySource(str, Enum):
    """Policy source enumeration."""
    MICROSOFT_ENTRA = "microsoft_entra"
    GOOGLE_CLOUD_IAM = "google_cloud_iam"
    AWS_IAM = "aws_iam"
    AZURE_AD = "azure_ad"
    CUSTOM = "custom"


class PolicyType(str, Enum):
    """Policy type enumeration."""
    IDENTITY = "identity"
    ACCESS = "access"
    ROLE = "role"
    PERMISSION = "permission"
    CONDITION = "condition"
    RESOURCE_BASED = "resource_based"


class PolicyEffect(str, Enum):
    """Policy effect enumeration."""
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStatus(str, Enum):
    """Compliance status enumeration."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNKNOWN = "unknown"


class Policy(Base):
    """
    Policy model for IAM policy data.
    
    This model stores policy information from various cloud providers,
    including metadata, classification, risk scoring, and relationships.
    """
    
    # Basic policy information
    name: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True,
        comment="Policy name or identifier"
    )
    
    display_name: Mapped[Optional[str]] = mapped_column(
        String(300),
        nullable=True,
        comment="Human-readable display name"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Policy description"
    )
    
    # Source and type information
    source: Mapped[PolicySource] = mapped_column(
        SQLEnum(PolicySource),
        nullable=False,
        index=True,
        comment="Source system where the policy originates"
    )
    
    policy_type: Mapped[PolicyType] = mapped_column(
        SQLEnum(PolicyType),
        nullable=False,
        index=True,
        comment="Type of policy"
    )
    
    effect: Mapped[Optional[PolicyEffect]] = mapped_column(
        SQLEnum(PolicyEffect),
        nullable=True,
        index=True,
        comment="Effect of the policy (allow/deny)"
    )
    
    # Policy content
    policy_content: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Raw policy content in JSON format"
    )
    
    policy_document: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Policy document as text"
    )
    
    conditions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Policy conditions in JSON format"
    )
    
    # Resource and scope information
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        index=True,
        comment="Resource identifier this policy applies to"
    )
    
    resource_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Type of resource this policy applies to"
    )
    
    scope: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Scope of the policy (subscription, project, etc.)"
    )
    
    principal_id: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        index=True,
        comment="Principal identifier (user, group, service account)"
    )
    
    principal_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Type of principal (user, group, service account)"
    )
    
    # Risk and security assessment
    risk_level: Mapped[RiskLevel] = mapped_column(
        SQLEnum(RiskLevel),
        default=RiskLevel.MEDIUM,
        nullable=False,
        index=True,
        comment="Risk level assessment"
    )
    
    risk_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        index=True,
        comment="Risk score (0-100)"
    )
    
    compliance_status: Mapped[ComplianceStatus] = mapped_column(
        SQLEnum(ComplianceStatus),
        default=ComplianceStatus.UNKNOWN,
        nullable=False,
        index=True,
        comment="Compliance status"
    )
    
    compliance_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        index=True,
        comment="Compliance score (0-100)"
    )
    
    # Classification and categorization
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Policy category"
    )
    
    subcategory: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Policy subcategory"
    )
    
    tags: Mapped[Optional[Dict[str, str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Policy tags for categorization"
    )
    
    # Access and permissions
    permissions: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="List of permissions granted by this policy"
    )
    
    actions: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="List of actions allowed/denied by this policy"
    )
    
    resources: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="List of resources affected by this policy"
    )
    
    # Policy lifecycle
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether the policy is currently active"
    )
    
    is_enforced: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether the policy is enforced"
    )
    
    is_system_managed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the policy is system-managed"
    )
    
    is_inherited: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the policy is inherited from a parent scope"
    )
    
    # External references
    external_id: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        index=True,
        comment="External policy identifier from source system"
    )
    
    external_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="External policy version"
    )
    
    parent_policy_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID of parent policy if this is derived"
    )
    
    # Analysis metadata
    last_analyzed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp when policy was last analyzed"
    )
    
    analysis_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Version of analysis performed"
    )
    
    findings_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of findings associated with this policy"
    )
    
    recommendations_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of recommendations for this policy"
    )
    
    # Audit and governance
    created_by: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Creator of the policy"
    )
    
    approved_by: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Approver of the policy"
    )
    
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Approval timestamp"
    )
    
    review_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether policy requires review"
    )
    
    next_review_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Next scheduled review date"
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
        comment="ID of the scan that discovered this policy"
    )
    
    scan: Mapped["Scan"] = relationship(
        "Scan",
        back_populates="policies"
    )
    
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="policy",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    child_policies: Mapped[list["Policy"]] = relationship(
        "Policy",
        backref="parent_policy",
        remote_side=[id],
        cascade="all, delete-orphan"
    )
    
    @property
    def is_high_risk(self) -> bool:
        """Check if policy is high risk."""
        return self.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    @property
    def is_compliant(self) -> bool:
        """Check if policy is compliant."""
        return self.compliance_status == ComplianceStatus.COMPLIANT
    
    @property
    def requires_attention(self) -> bool:
        """Check if policy requires attention."""
        return (
            self.is_high_risk or
            not self.is_compliant or
            self.review_required or
            (self.next_review_date and self.next_review_date <= datetime.utcnow())
        )
    
    def update_risk_assessment(self, risk_score: float, risk_level: RiskLevel) -> None:
        """
        Update risk assessment for the policy.
        
        Args:
            risk_score: New risk score (0-100)
            risk_level: New risk level
        """
        self.risk_score = max(0.0, min(100.0, risk_score))
        self.risk_level = risk_level
        self.last_analyzed_at = datetime.utcnow()
    
    def update_compliance_status(self, status: ComplianceStatus, score: float = None) -> None:
        """
        Update compliance status for the policy.
        
        Args:
            status: New compliance status
            score: New compliance score (optional)
        """
        self.compliance_status = status
        if score is not None:
            self.compliance_score = max(0.0, min(100.0, score))
        self.last_analyzed_at = datetime.utcnow()
    
    def add_finding(self) -> None:
        """Increment findings count."""
        self.findings_count += 1
    
    def add_recommendation(self) -> None:
        """Increment recommendations count."""
        self.recommendations_count += 1
    
    def schedule_review(self, days_ahead: int = 30) -> None:
        """
        Schedule next review for the policy.
        
        Args:
            days_ahead: Number of days from now for the review
        """
        from datetime import timedelta
        
        self.next_review_date = datetime.utcnow() + timedelta(days=days_ahead)
        self.review_required = True
    
    def approve(self, approved_by: str) -> None:
        """
        Approve the policy.
        
        Args:
            approved_by: Name or identifier of the approver
        """
        self.approved_by = approved_by
        self.approved_at = datetime.utcnow()
        self.review_required = False
    
    def deactivate(self) -> None:
        """Deactivate the policy."""
        self.is_active = False
    
    def activate(self) -> None:
        """Activate the policy."""
        self.is_active = True
    
    def __repr__(self) -> str:
        """String representation of the Policy model."""
        return f"<Policy(id={self.id}, name={self.name}, source={self.source}, risk_level={self.risk_level})>"