"""
Audit Evidence Generator for CIEM Platform

Generates compliance-ready audit evidence packages for SOC 2, ISO 27001,
NIST, and other regulatory frameworks.

Chainguard Relevance: Demonstrates "preparing evidence for SOC 2, ISO27001,
and other regulatory audits" - key requirement for IT Engineer (Identity/IAM) role.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
import json
import hashlib
import uuid


# =============================================================================
# ENUMS AND MODELS
# =============================================================================

class ComplianceFramework(str, Enum):
    """Supported compliance frameworks"""
    SOC2 = "SOC2"
    ISO27001 = "ISO27001"
    NIST_800_53 = "NIST_800_53"
    CIS = "CIS"
    PCI_DSS = "PCI_DSS"
    HIPAA = "HIPAA"


class EvidenceType(str, Enum):
    """Types of evidence that can be generated"""
    ENTITLEMENT_ANALYSIS = "entitlement_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    POLICY_VALIDATION = "policy_validation"
    ACCESS_REVIEW = "access_review"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    EXTERNAL_ACCESS = "external_access"
    COMPLIANCE_SCAN = "compliance_scan"


class RiskSeverity(str, Enum):
    """Risk severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class EvidenceItem(BaseModel):
    """Individual evidence item"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evidence_type: EvidenceType
    title: str
    description: str
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    collected_by: str

    # Cloud provider info
    cloud_provider: str  # "aws", "gcp", "azure"
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None

    # Finding details
    finding: Optional[str] = None
    severity: Optional[RiskSeverity] = None
    risk_score: Optional[float] = None

    # Remediation
    remediation_status: str = "open"  # "open", "in_progress", "resolved", "accepted"
    remediation_notes: Optional[str] = None

    # Evidence data
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    screenshot_path: Optional[str] = None

    # Compliance mapping
    control_mappings: List[str] = Field(default_factory=list)


class EvidencePackage(BaseModel):
    """Complete evidence package for auditors"""
    package_id: str = Field(default_factory=lambda: f"EVP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
    framework: ComplianceFramework
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str

    # Audit period
    audit_period_start: date
    audit_period_end: date

    # Contents
    evidence_items: List[EvidenceItem] = Field(default_factory=list)

    # Summary
    total_findings: int = 0
    critical_findings: int = 0
    high_findings: int = 0
    medium_findings: int = 0
    low_findings: int = 0
    resolved_findings: int = 0

    # Integrity
    sha256_hash: Optional[str] = None

    def calculate_hash(self) -> str:
        """Calculate SHA256 hash of package contents"""
        content = json.dumps(
            [item.dict() for item in self.evidence_items],
            sort_keys=True,
            default=str
        )
        self.sha256_hash = hashlib.sha256(content.encode()).hexdigest()
        return self.sha256_hash


# =============================================================================
# CONTROL MAPPINGS
# =============================================================================

CONTROL_MAPPINGS = {
    ComplianceFramework.SOC2: {
        "CC6.1": {
            "name": "Logical Access Security",
            "evidence_types": [
                EvidenceType.ENTITLEMENT_ANALYSIS,
                EvidenceType.POLICY_VALIDATION
            ]
        },
        "CC6.3": {
            "name": "Role-Based Access",
            "evidence_types": [
                EvidenceType.ENTITLEMENT_ANALYSIS,
                EvidenceType.RISK_ASSESSMENT
            ]
        },
        "CC6.6": {
            "name": "Access Monitoring",
            "evidence_types": [
                EvidenceType.ACCESS_REVIEW,
                EvidenceType.EXTERNAL_ACCESS
            ]
        },
        "CC6.8": {
            "name": "Privileged Access",
            "evidence_types": [
                EvidenceType.PRIVILEGE_ESCALATION,
                EvidenceType.RISK_ASSESSMENT
            ]
        },
    },
    ComplianceFramework.ISO27001: {
        "A.5.15": {
            "name": "Access Control",
            "evidence_types": [
                EvidenceType.ENTITLEMENT_ANALYSIS,
                EvidenceType.POLICY_VALIDATION
            ]
        },
        "A.5.18": {
            "name": "Access Rights",
            "evidence_types": [
                EvidenceType.ACCESS_REVIEW,
                EvidenceType.ENTITLEMENT_ANALYSIS
            ]
        },
        "A.8.2": {
            "name": "Privileged Access Rights",
            "evidence_types": [
                EvidenceType.PRIVILEGE_ESCALATION,
                EvidenceType.RISK_ASSESSMENT
            ]
        },
    },
    ComplianceFramework.NIST_800_53: {
        "AC-2": {
            "name": "Account Management",
            "evidence_types": [
                EvidenceType.ENTITLEMENT_ANALYSIS,
                EvidenceType.ACCESS_REVIEW
            ]
        },
        "AC-6": {
            "name": "Least Privilege",
            "evidence_types": [
                EvidenceType.RISK_ASSESSMENT,
                EvidenceType.ENTITLEMENT_ANALYSIS
            ]
        },
    },
    ComplianceFramework.CIS: {
        "1.1": {
            "name": "IAM Policies",
            "evidence_types": [
                EvidenceType.POLICY_VALIDATION,
                EvidenceType.COMPLIANCE_SCAN
            ]
        },
        "1.4": {
            "name": "Access Keys",
            "evidence_types": [
                EvidenceType.RISK_ASSESSMENT,
                EvidenceType.EXTERNAL_ACCESS
            ]
        },
    },
}


# =============================================================================
# EVIDENCE GENERATOR
# =============================================================================

class AuditEvidenceGenerator:
    """Generates audit evidence for CIEM findings"""

    def __init__(self, generated_by: str = "system"):
        self.generated_by = generated_by

    def generate_entitlement_evidence(
        self,
        cloud_provider: str,
        findings: List[Dict[str, Any]]
    ) -> List[EvidenceItem]:
        """Generate evidence from entitlement analysis"""

        evidence_items = []

        for finding in findings:
            item = EvidenceItem(
                evidence_type=EvidenceType.ENTITLEMENT_ANALYSIS,
                title=f"Entitlement Finding: {finding.get('resource_type', 'Unknown')}",
                description=finding.get("description", "Entitlement analysis finding"),
                collected_by=self.generated_by,
                cloud_provider=cloud_provider,
                resource_type=finding.get("resource_type"),
                resource_id=finding.get("resource_id"),
                finding=finding.get("finding"),
                severity=RiskSeverity(finding.get("severity", "medium")),
                risk_score=finding.get("risk_score", 50.0),
                raw_data=finding,
                control_mappings=self._map_to_controls(
                    EvidenceType.ENTITLEMENT_ANALYSIS
                )
            )
            evidence_items.append(item)

        return evidence_items

    def generate_risk_evidence(
        self,
        cloud_provider: str,
        risk_findings: List[Dict[str, Any]]
    ) -> List[EvidenceItem]:
        """Generate evidence from risk assessment"""

        evidence_items = []

        for finding in risk_findings:
            item = EvidenceItem(
                evidence_type=EvidenceType.RISK_ASSESSMENT,
                title=f"Risk Finding: {finding.get('title', 'Unknown')}",
                description=finding.get("description", "Risk assessment finding"),
                collected_by=self.generated_by,
                cloud_provider=cloud_provider,
                resource_type=finding.get("resource_type"),
                resource_id=finding.get("resource_id"),
                finding=finding.get("finding"),
                severity=RiskSeverity(finding.get("severity", "high")),
                risk_score=finding.get("risk_score", 75.0),
                raw_data=finding,
                control_mappings=self._map_to_controls(
                    EvidenceType.RISK_ASSESSMENT
                )
            )
            evidence_items.append(item)

        return evidence_items

    def generate_privilege_escalation_evidence(
        self,
        cloud_provider: str,
        escalation_paths: List[Dict[str, Any]]
    ) -> List[EvidenceItem]:
        """Generate evidence from privilege escalation analysis"""

        evidence_items = []

        for path in escalation_paths:
            item = EvidenceItem(
                evidence_type=EvidenceType.PRIVILEGE_ESCALATION,
                title=f"Privilege Escalation Path: {path.get('source', 'Unknown')} → {path.get('target', 'Unknown')}",
                description=f"Potential privilege escalation from {path.get('source')} to {path.get('target')}",
                collected_by=self.generated_by,
                cloud_provider=cloud_provider,
                resource_type="iam_role",
                resource_id=path.get("source_id"),
                finding=path.get("description"),
                severity=RiskSeverity.CRITICAL,
                risk_score=95.0,
                raw_data=path,
                control_mappings=self._map_to_controls(
                    EvidenceType.PRIVILEGE_ESCALATION
                )
            )
            evidence_items.append(item)

        return evidence_items

    def generate_external_access_evidence(
        self,
        cloud_provider: str,
        external_findings: List[Dict[str, Any]]
    ) -> List[EvidenceItem]:
        """Generate evidence from external access analysis"""

        evidence_items = []

        for finding in external_findings:
            item = EvidenceItem(
                evidence_type=EvidenceType.EXTERNAL_ACCESS,
                title=f"External Access: {finding.get('resource_type', 'Unknown')}",
                description=finding.get("description", "External access finding"),
                collected_by=self.generated_by,
                cloud_provider=cloud_provider,
                resource_type=finding.get("resource_type"),
                resource_id=finding.get("resource_id"),
                finding=finding.get("finding"),
                severity=RiskSeverity(finding.get("severity", "high")),
                risk_score=finding.get("risk_score", 80.0),
                raw_data=finding,
                control_mappings=self._map_to_controls(
                    EvidenceType.EXTERNAL_ACCESS
                )
            )
            evidence_items.append(item)

        return evidence_items

    def generate_compliance_scan_evidence(
        self,
        cloud_provider: str,
        benchmark: str,
        scan_results: List[Dict[str, Any]]
    ) -> List[EvidenceItem]:
        """Generate evidence from compliance benchmark scan"""

        evidence_items = []

        for result in scan_results:
            item = EvidenceItem(
                evidence_type=EvidenceType.COMPLIANCE_SCAN,
                title=f"{benchmark} Check: {result.get('check_id', 'Unknown')}",
                description=result.get("description", "Compliance check"),
                collected_by=self.generated_by,
                cloud_provider=cloud_provider,
                resource_type=result.get("resource_type"),
                resource_id=result.get("resource_id"),
                finding=result.get("finding"),
                severity=RiskSeverity(result.get("severity", "medium")),
                remediation_status="resolved" if result.get("passed") else "open",
                raw_data=result,
                control_mappings=[f"{benchmark}:{result.get('check_id', 'N/A')}"]
            )
            evidence_items.append(item)

        return evidence_items

    def _map_to_controls(self, evidence_type: EvidenceType) -> List[str]:
        """Map evidence type to compliance controls"""

        mappings = []

        for framework, controls in CONTROL_MAPPINGS.items():
            for control_id, control_info in controls.items():
                if evidence_type in control_info["evidence_types"]:
                    mappings.append(f"{framework.value}:{control_id}")

        return mappings

    def create_evidence_package(
        self,
        framework: ComplianceFramework,
        evidence_items: List[EvidenceItem],
        audit_period_start: date,
        audit_period_end: date
    ) -> EvidencePackage:
        """Create a complete evidence package for auditors"""

        # Calculate summary stats
        critical = sum(1 for i in evidence_items if i.severity == RiskSeverity.CRITICAL)
        high = sum(1 for i in evidence_items if i.severity == RiskSeverity.HIGH)
        medium = sum(1 for i in evidence_items if i.severity == RiskSeverity.MEDIUM)
        low = sum(1 for i in evidence_items if i.severity == RiskSeverity.LOW)
        resolved = sum(1 for i in evidence_items if i.remediation_status == "resolved")

        package = EvidencePackage(
            framework=framework,
            generated_by=self.generated_by,
            audit_period_start=audit_period_start,
            audit_period_end=audit_period_end,
            evidence_items=evidence_items,
            total_findings=len(evidence_items),
            critical_findings=critical,
            high_findings=high,
            medium_findings=medium,
            low_findings=low,
            resolved_findings=resolved
        )

        package.calculate_hash()

        return package

    def export_package_to_json(
        self,
        package: EvidencePackage,
        output_path: str
    ) -> str:
        """Export evidence package to JSON file"""

        with open(output_path, 'w') as f:
            f.write(package.json(indent=2))

        return output_path

    def export_package_to_markdown(
        self,
        package: EvidencePackage
    ) -> str:
        """Export evidence package to markdown format"""

        md = f"""# Audit Evidence Package

## Package Information

| Field | Value |
|-------|-------|
| Package ID | {package.package_id} |
| Framework | {package.framework.value} |
| Generated At | {package.generated_at.isoformat()} |
| Generated By | {package.generated_by} |
| Audit Period | {package.audit_period_start} to {package.audit_period_end} |
| SHA256 Hash | {package.sha256_hash} |

## Summary

| Severity | Count |
|----------|-------|
| Critical | {package.critical_findings} |
| High | {package.high_findings} |
| Medium | {package.medium_findings} |
| Low | {package.low_findings} |
| **Total** | **{package.total_findings}** |
| Resolved | {package.resolved_findings} |

## Evidence Items

"""
        for item in package.evidence_items:
            md += f"""### {item.title}

- **Type:** {item.evidence_type.value}
- **Severity:** {item.severity.value if item.severity else "N/A"}
- **Cloud Provider:** {item.cloud_provider}
- **Resource:** {item.resource_type} / {item.resource_id}
- **Status:** {item.remediation_status}
- **Controls:** {", ".join(item.control_mappings)}

{item.description}

---

"""

        md += """
*This evidence package was generated by ZeroTrust IAM Analyzer.*
*Chainguard IT Engineer (Identity/IAM) Portfolio - Mike Dominic*
"""

        return md


# =============================================================================
# SAMPLE DATA GENERATOR (for demo)
# =============================================================================

def generate_sample_evidence() -> EvidencePackage:
    """Generate sample evidence for demonstration"""

    generator = AuditEvidenceGenerator(generated_by="demo@example.com")

    # Sample AWS findings
    aws_entitlement_findings = [
        {
            "resource_type": "iam_user",
            "resource_id": "arn:aws:iam::123456789012:user/admin-user",
            "description": "IAM user with full administrator access",
            "finding": "User has AdministratorAccess policy attached directly",
            "severity": "critical",
            "risk_score": 95.0
        },
        {
            "resource_type": "iam_role",
            "resource_id": "arn:aws:iam::123456789012:role/lambda-role",
            "description": "Lambda role with excessive permissions",
            "finding": "Role has wildcard (*) permissions on S3",
            "severity": "high",
            "risk_score": 80.0
        },
    ]

    aws_escalation_paths = [
        {
            "source": "developer-role",
            "source_id": "arn:aws:iam::123456789012:role/developer",
            "target": "admin-role",
            "description": "Developer can escalate to admin via iam:PassRole and lambda:CreateFunction"
        }
    ]

    # Generate evidence items
    evidence_items = []
    evidence_items.extend(
        generator.generate_entitlement_evidence("aws", aws_entitlement_findings)
    )
    evidence_items.extend(
        generator.generate_privilege_escalation_evidence("aws", aws_escalation_paths)
    )

    # Create package
    package = generator.create_evidence_package(
        framework=ComplianceFramework.SOC2,
        evidence_items=evidence_items,
        audit_period_start=date(2025, 1, 1),
        audit_period_end=date(2025, 12, 31)
    )

    return package


if __name__ == "__main__":
    # Demo
    package = generate_sample_evidence()
    print(package.json(indent=2))
