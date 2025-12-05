"""
Audit Evidence Module

Provides compliance audit evidence generation for CIEM platform findings.
Supports SOC 2, ISO 27001, NIST, CIS, and other regulatory frameworks.

Chainguard Relevance: Demonstrates "preparing evidence for SOC 2, ISO27001,
and other regulatory audits" - key requirement for IT Engineer (Identity/IAM) role.
"""

from .evidence_generator import (
    AuditEvidenceGenerator,
    EvidencePackage,
    EvidenceItem,
    EvidenceType,
    ComplianceFramework,
    RiskSeverity,
    CONTROL_MAPPINGS,
    generate_sample_evidence
)

__all__ = [
    "AuditEvidenceGenerator",
    "EvidencePackage",
    "EvidenceItem",
    "EvidenceType",
    "ComplianceFramework",
    "RiskSeverity",
    "CONTROL_MAPPINGS",
    "generate_sample_evidence"
]
