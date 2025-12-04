"""
Finding Processor for AWS IAM Access Analyzer.

This module processes and normalizes AWS Access Analyzer findings into a unified
format compatible with the ZeroTrust IAM Analyzer CIEM platform. It calculates
severity scores, enriches finding metadata, and provides risk assessment capabilities.

v1.1 Enhancement - December 2025
Enables seamless integration of AWS findings with existing GCP and Workspace
analysis in the unified CIEM dashboard.

Key Features:
- Normalize AWS findings to platform-standard format
- Calculate severity scores based on exposure type and risk factors
- Enrich findings with contextual metadata
- Aggregate findings by resource, account, and risk level
- Generate actionable remediation recommendations
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field


class SeverityLevel(str, Enum):
    """Severity level enumeration for normalized findings."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ExposureType(str, Enum):
    """Type of access exposure detected."""
    PUBLIC_INTERNET = "PUBLIC_INTERNET"
    CROSS_ACCOUNT = "CROSS_ACCOUNT"
    CROSS_ORG = "CROSS_ORG"
    SERVICE_ACCESS = "SERVICE_ACCESS"
    ANONYMOUS = "ANONYMOUS"


@dataclass
class NormalizedFinding:
    """
    Normalized finding structure for unified CIEM platform.

    This data class represents a finding in the standard format used across
    all cloud providers in the ZeroTrust IAM Analyzer platform.
    """
    # Core identification
    finding_id: str
    cloud_provider: str = "AWS"
    analyzer_id: str = ""

    # Resource information
    resource_arn: str = ""
    resource_type: str = ""
    resource_name: str = ""
    resource_account: str = ""
    resource_region: str = ""

    # Finding details
    status: str = "ACTIVE"
    severity: SeverityLevel = SeverityLevel.MEDIUM
    severity_score: float = 50.0  # 0-100 scale

    # Access details
    exposure_type: ExposureType = ExposureType.CROSS_ACCOUNT
    is_public: bool = False
    principal: Dict[str, Any] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    title: str = ""
    description: str = ""
    recommendation: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None

    # Risk factors
    risk_factors: List[str] = field(default_factory=list)
    compliance_violations: List[str] = field(default_factory=list)

    # Additional context
    tags: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None
    raw_finding: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary format."""
        return {
            "finding_id": self.finding_id,
            "cloud_provider": self.cloud_provider,
            "analyzer_id": self.analyzer_id,
            "resource": {
                "arn": self.resource_arn,
                "type": self.resource_type,
                "name": self.resource_name,
                "account": self.resource_account,
                "region": self.resource_region,
            },
            "status": self.status,
            "severity": self.severity.value,
            "severity_score": self.severity_score,
            "exposure": {
                "type": self.exposure_type.value,
                "is_public": self.is_public,
                "principal": self.principal,
                "actions": self.actions,
                "conditions": self.conditions,
            },
            "title": self.title,
            "description": self.description,
            "recommendation": self.recommendation,
            "timestamps": {
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
                "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            },
            "risk_factors": self.risk_factors,
            "compliance_violations": self.compliance_violations,
            "tags": self.tags,
            "error": self.error,
        }


class FindingProcessor:
    """
    Process and normalize AWS Access Analyzer findings.

    This class transforms raw AWS Access Analyzer findings into the standardized
    format used by ZeroTrust IAM Analyzer, calculates severity scores, and
    generates remediation recommendations.

    Example:
        >>> processor = FindingProcessor()
        >>> raw_finding = aws_analyzer.get_finding("finding-001")
        >>> normalized = processor.process_finding(raw_finding)
        >>> print(f"Severity: {normalized.severity} ({normalized.severity_score}/100)")
    """

    # Severity weights for different risk factors
    RISK_WEIGHTS = {
        "public_access": 40.0,
        "admin_permissions": 30.0,
        "data_access": 25.0,
        "destructive_actions": 25.0,
        "encryption_access": 20.0,
        "cross_account": 15.0,
        "no_conditions": 10.0,
    }

    # Resource type severity baseline
    RESOURCE_SEVERITY = {
        "AWS::S3::Bucket": 30.0,
        "AWS::IAM::Role": 40.0,
        "AWS::KMS::Key": 35.0,
        "AWS::Lambda::Function": 25.0,
        "AWS::SecretsManager::Secret": 45.0,
        "AWS::RDS::DBSnapshot": 40.0,
        "AWS::ECR::Repository": 30.0,
    }

    def __init__(self) -> None:
        """Initialize the finding processor."""
        pass

    def process_finding(
        self,
        raw_finding: Dict[str, Any],
        analyzer_arn: Optional[str] = None,
    ) -> NormalizedFinding:
        """
        Process and normalize a single AWS Access Analyzer finding.

        Args:
            raw_finding: Raw finding from AWS Access Analyzer API
            analyzer_arn: ARN of the analyzer (optional)

        Returns:
            Normalized finding with severity score and enriched metadata
        """
        # Extract core fields
        finding_id = raw_finding.get("id", "unknown")
        resource_arn = raw_finding.get("resource", "")
        resource_type = raw_finding.get("resourceType", "")
        status = raw_finding.get("status", "ACTIVE")

        # Parse resource details
        resource_name = self._extract_resource_name(resource_arn)
        resource_account = raw_finding.get("resourceOwnerAccount", "")
        resource_region = self._extract_region(resource_arn)

        # Extract access details
        principal = raw_finding.get("principal", {})
        actions = raw_finding.get("action", [])
        conditions = raw_finding.get("condition", {})
        is_public = raw_finding.get("isPublic", False)

        # Determine exposure type
        exposure_type = self._determine_exposure_type(principal, is_public)

        # Parse timestamps
        created_at = self._parse_timestamp(raw_finding.get("createdAt"))
        updated_at = self._parse_timestamp(raw_finding.get("updatedAt"))
        analyzed_at = self._parse_timestamp(raw_finding.get("analyzedAt"))

        # Calculate severity
        risk_factors = self._identify_risk_factors(
            raw_finding, principal, actions, conditions, is_public
        )
        severity_score = self._calculate_severity_score(
            resource_type, principal, actions, is_public, risk_factors
        )
        severity = self._score_to_severity(severity_score)

        # Generate title and description
        title = self._generate_title(resource_type, exposure_type, is_public)
        description = self._generate_description(
            resource_name, resource_type, principal, actions
        )

        # Generate recommendation
        recommendation = self._generate_recommendation(
            resource_type, exposure_type, is_public, actions
        )

        # Identify compliance violations
        compliance_violations = self._check_compliance_violations(
            resource_type, is_public, actions, risk_factors
        )

        # Build normalized finding
        return NormalizedFinding(
            finding_id=finding_id,
            cloud_provider="AWS",
            analyzer_id=analyzer_arn or "",
            resource_arn=resource_arn,
            resource_type=resource_type,
            resource_name=resource_name,
            resource_account=resource_account,
            resource_region=resource_region,
            status=status,
            severity=severity,
            severity_score=severity_score,
            exposure_type=exposure_type,
            is_public=is_public,
            principal=principal,
            actions=actions,
            conditions=conditions,
            title=title,
            description=description,
            recommendation=recommendation,
            created_at=created_at,
            updated_at=updated_at,
            analyzed_at=analyzed_at,
            risk_factors=risk_factors,
            compliance_violations=compliance_violations,
            error=raw_finding.get("error"),
            raw_finding=raw_finding,
        )

    def process_findings_batch(
        self,
        raw_findings: List[Dict[str, Any]],
        analyzer_arn: Optional[str] = None,
    ) -> List[NormalizedFinding]:
        """
        Process multiple findings in batch.

        Args:
            raw_findings: List of raw findings from AWS
            analyzer_arn: ARN of the analyzer

        Returns:
            List of normalized findings
        """
        return [
            self.process_finding(finding, analyzer_arn)
            for finding in raw_findings
        ]

    def aggregate_by_severity(
        self,
        findings: List[NormalizedFinding],
    ) -> Dict[str, List[NormalizedFinding]]:
        """
        Aggregate findings by severity level.

        Args:
            findings: List of normalized findings

        Returns:
            Dictionary mapping severity to list of findings
        """
        aggregated: Dict[str, List[NormalizedFinding]] = {
            severity.value: [] for severity in SeverityLevel
        }

        for finding in findings:
            aggregated[finding.severity.value].append(finding)

        return aggregated

    def aggregate_by_resource_type(
        self,
        findings: List[NormalizedFinding],
    ) -> Dict[str, List[NormalizedFinding]]:
        """
        Aggregate findings by resource type.

        Args:
            findings: List of normalized findings

        Returns:
            Dictionary mapping resource type to list of findings
        """
        aggregated: Dict[str, List[NormalizedFinding]] = {}

        for finding in findings:
            resource_type = finding.resource_type
            if resource_type not in aggregated:
                aggregated[resource_type] = []
            aggregated[resource_type].append(finding)

        return aggregated

    def get_summary_statistics(
        self,
        findings: List[NormalizedFinding],
    ) -> Dict[str, Any]:
        """
        Generate summary statistics for findings.

        Args:
            findings: List of normalized findings

        Returns:
            Dictionary with statistical summary
        """
        if not findings:
            return {
                "total_findings": 0,
                "by_severity": {},
                "by_resource_type": {},
                "by_exposure_type": {},
                "average_severity_score": 0.0,
                "public_exposures": 0,
            }

        severity_counts = {}
        resource_type_counts = {}
        exposure_type_counts = {}
        public_count = 0
        total_score = 0.0

        for finding in findings:
            # Count by severity
            severity = finding.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

            # Count by resource type
            resource_type = finding.resource_type
            resource_type_counts[resource_type] = \
                resource_type_counts.get(resource_type, 0) + 1

            # Count by exposure type
            exposure_type = finding.exposure_type.value
            exposure_type_counts[exposure_type] = \
                exposure_type_counts.get(exposure_type, 0) + 1

            # Count public exposures
            if finding.is_public:
                public_count += 1

            # Sum severity scores
            total_score += finding.severity_score

        return {
            "total_findings": len(findings),
            "by_severity": severity_counts,
            "by_resource_type": resource_type_counts,
            "by_exposure_type": exposure_type_counts,
            "average_severity_score": total_score / len(findings),
            "public_exposures": public_count,
        }

    # Internal helper methods

    def _extract_resource_name(self, resource_arn: str) -> str:
        """Extract resource name from ARN."""
        if not resource_arn:
            return ""
        parts = resource_arn.split(":")
        if len(parts) >= 6:
            # Handle different ARN formats
            resource_part = parts[-1]
            if "/" in resource_part:
                return resource_part.split("/")[-1]
            return resource_part
        return resource_arn

    def _extract_region(self, resource_arn: str) -> str:
        """Extract AWS region from ARN."""
        if not resource_arn:
            return ""
        parts = resource_arn.split(":")
        if len(parts) >= 4:
            return parts[3]
        return ""

    def _determine_exposure_type(
        self,
        principal: Dict[str, Any],
        is_public: bool,
    ) -> ExposureType:
        """Determine the type of access exposure."""
        if is_public:
            # Check for anonymous access
            if principal.get("AWS") == "*":
                return ExposureType.ANONYMOUS
            return ExposureType.PUBLIC_INTERNET

        # Check principal type
        if "AWS" in principal:
            aws_principal = principal["AWS"]
            if isinstance(aws_principal, str):
                if ":root" in aws_principal or "arn:aws:iam" in aws_principal:
                    return ExposureType.CROSS_ACCOUNT
                if ":organization" in aws_principal:
                    return ExposureType.CROSS_ORG

        if "Service" in principal:
            return ExposureType.SERVICE_ACCESS

        return ExposureType.CROSS_ACCOUNT

    def _parse_timestamp(self, timestamp: Optional[str]) -> Optional[datetime]:
        """Parse ISO 8601 timestamp string."""
        if not timestamp:
            return None
        try:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    def _identify_risk_factors(
        self,
        raw_finding: Dict[str, Any],
        principal: Dict[str, Any],
        actions: List[str],
        conditions: Dict[str, Any],
        is_public: bool,
    ) -> List[str]:
        """Identify risk factors for the finding."""
        risk_factors = []

        if is_public:
            risk_factors.append("Public internet access")

        if principal.get("AWS") == "*":
            risk_factors.append("Anonymous access allowed")

        if not conditions:
            risk_factors.append("No conditions restricting access")

        # Check for dangerous actions
        dangerous_actions = self._check_dangerous_actions(actions)
        risk_factors.extend(dangerous_actions)

        # Check for admin-level permissions
        if self._has_admin_permissions(actions):
            risk_factors.append("Administrative permissions granted")

        return risk_factors

    def _check_dangerous_actions(self, actions: List[str]) -> List[str]:
        """Check for dangerous or destructive actions."""
        dangerous = []

        destructive_keywords = ["Delete", "Remove", "Terminate", "Destroy"]
        data_keywords = ["GetObject", "GetSecretValue", "Decrypt"]

        for action in actions:
            if any(keyword in action for keyword in destructive_keywords):
                dangerous.append(f"Destructive action: {action}")
            elif any(keyword in action for keyword in data_keywords):
                dangerous.append(f"Data access: {action}")

        return dangerous

    def _has_admin_permissions(self, actions: List[str]) -> bool:
        """Check if actions include administrative permissions."""
        admin_keywords = ["*", "Admin", "FullAccess", "AssumeRole"]
        return any(
            keyword in action for action in actions for keyword in admin_keywords
        )

    def _calculate_severity_score(
        self,
        resource_type: str,
        principal: Dict[str, Any],
        actions: List[str],
        is_public: bool,
        risk_factors: List[str],
    ) -> float:
        """
        Calculate severity score (0-100) based on multiple factors.

        Higher scores indicate more severe security risks.
        """
        # Start with resource type baseline
        score = self.RESOURCE_SEVERITY.get(resource_type, 25.0)

        # Add weight for public access
        if is_public:
            score += self.RISK_WEIGHTS["public_access"]

        # Add weight for anonymous access
        if principal.get("AWS") == "*":
            score += 15.0

        # Add weight for admin permissions
        if self._has_admin_permissions(actions):
            score += self.RISK_WEIGHTS["admin_permissions"]

        # Add weight for each risk factor (capped)
        score += min(len(risk_factors) * 5.0, 25.0)

        # Cap at 100
        return min(score, 100.0)

    def _score_to_severity(self, score: float) -> SeverityLevel:
        """Convert numeric score to severity level."""
        if score >= 80:
            return SeverityLevel.CRITICAL
        elif score >= 60:
            return SeverityLevel.HIGH
        elif score >= 40:
            return SeverityLevel.MEDIUM
        elif score >= 20:
            return SeverityLevel.LOW
        else:
            return SeverityLevel.INFO

    def _generate_title(
        self,
        resource_type: str,
        exposure_type: ExposureType,
        is_public: bool,
    ) -> str:
        """Generate human-readable finding title."""
        resource_name = resource_type.split("::")[-1]

        if is_public:
            return f"Public {resource_name} with external access"
        elif exposure_type == ExposureType.CROSS_ACCOUNT:
            return f"{resource_name} shared with external AWS account"
        elif exposure_type == ExposureType.SERVICE_ACCESS:
            return f"{resource_name} accessible by AWS service"
        else:
            return f"{resource_name} with external access"

    def _generate_description(
        self,
        resource_name: str,
        resource_type: str,
        principal: Dict[str, Any],
        actions: List[str],
    ) -> str:
        """Generate detailed finding description."""
        principal_str = self._format_principal(principal)
        actions_str = ", ".join(actions[:3])
        if len(actions) > 3:
            actions_str += f" (+{len(actions) - 3} more)"

        return (
            f"Resource '{resource_name}' ({resource_type}) grants access to "
            f"{principal_str} with permissions: {actions_str}."
        )

    def _format_principal(self, principal: Dict[str, Any]) -> str:
        """Format principal for display."""
        if "AWS" in principal:
            aws = principal["AWS"]
            if aws == "*":
                return "anyone (public)"
            return f"AWS principal {aws}"
        elif "Service" in principal:
            return f"AWS service {principal['Service']}"
        else:
            return "external principal"

    def _generate_recommendation(
        self,
        resource_type: str,
        exposure_type: ExposureType,
        is_public: bool,
        actions: List[str],
    ) -> str:
        """Generate remediation recommendation."""
        if is_public:
            return (
                "Review and restrict public access. Consider using VPC endpoints "
                "or private networking. Apply least privilege access controls."
            )
        elif exposure_type == ExposureType.CROSS_ACCOUNT:
            return (
                "Verify that cross-account access is required. Use AWS Organizations "
                "for trusted access. Apply IAM conditions to restrict access scope."
            )
        else:
            return (
                "Review external access permissions. Ensure principle of least "
                "privilege is applied. Add conditions to restrict access context."
            )

    def _check_compliance_violations(
        self,
        resource_type: str,
        is_public: bool,
        actions: List[str],
        risk_factors: List[str],
    ) -> List[str]:
        """Check for compliance framework violations."""
        violations = []

        # CIS AWS Foundations Benchmark checks
        if is_public and "S3::Bucket" in resource_type:
            violations.append("CIS AWS 2.1.5 - S3 bucket should not be publicly accessible")

        if is_public:
            violations.append("CIS AWS - Resource should not be publicly accessible")

        if "Administrative permissions granted" in risk_factors:
            violations.append("CIS AWS - Excessive IAM permissions granted")

        if "No conditions restricting access" in risk_factors:
            violations.append("CIS AWS - IAM policy lacks conditional restrictions")

        return violations
