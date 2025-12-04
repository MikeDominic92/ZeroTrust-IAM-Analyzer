"""
IAM Policy Validator for AWS Policies.

This module validates AWS IAM policies against security best practices and
compliance frameworks including CIS AWS Foundations Benchmark, least privilege
principles, and Zero Trust security guidelines.

v1.1 Enhancement - December 2025
Provides policy validation capabilities for AWS IAM policies to ensure
compliance with security standards and identify privilege escalation risks.

Key Features:
- Validate IAM policies against CIS AWS Foundations Benchmark
- Detect overly permissive policies and wildcard usage
- Identify privilege escalation paths
- Check for missing conditions and security controls
- Generate scored recommendations for policy improvements
- Support for both resource-based and identity-based policies
"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class ValidationSeverity(str, Enum):
    """Severity levels for policy validation issues."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    CIS_AWS = "CIS_AWS_FOUNDATIONS"
    NIST_800_53 = "NIST_800_53"
    PCI_DSS = "PCI_DSS"
    ZERO_TRUST = "ZERO_TRUST"


@dataclass
class PolicyIssue:
    """
    Represents a policy validation issue.

    Attributes:
        issue_id: Unique identifier for the issue type
        title: Short description of the issue
        description: Detailed explanation
        severity: Issue severity level
        recommendation: Suggested remediation
        compliance_violations: List of violated compliance controls
        affected_statements: Statement IDs or indices with the issue
        risk_score: Numeric risk score (0-100)
    """
    issue_id: str
    title: str
    description: str
    severity: ValidationSeverity
    recommendation: str
    compliance_violations: List[str] = field(default_factory=list)
    affected_statements: List[str] = field(default_factory=list)
    risk_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            "issue_id": self.issue_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "recommendation": self.recommendation,
            "compliance_violations": self.compliance_violations,
            "affected_statements": self.affected_statements,
            "risk_score": self.risk_score,
        }


@dataclass
class ValidationResult:
    """
    Result of policy validation.

    Attributes:
        policy_name: Name or identifier of the policy
        is_valid: Whether policy passes all critical checks
        issues: List of identified issues
        overall_risk_score: Aggregate risk score (0-100)
        least_privilege_score: Least privilege compliance score (0-100)
        compliance_status: Status by framework
    """
    policy_name: str
    is_valid: bool = True
    issues: List[PolicyIssue] = field(default_factory=list)
    overall_risk_score: float = 0.0
    least_privilege_score: float = 100.0
    compliance_status: Dict[str, bool] = field(default_factory=dict)
    recommendations_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "policy_name": self.policy_name,
            "is_valid": self.is_valid,
            "issues": [issue.to_dict() for issue in self.issues],
            "overall_risk_score": self.overall_risk_score,
            "least_privilege_score": self.least_privilege_score,
            "compliance_status": self.compliance_status,
            "recommendations_count": self.recommendations_count,
            "summary": {
                "total_issues": len(self.issues),
                "by_severity": self._count_by_severity(),
            },
        }

    def _count_by_severity(self) -> Dict[str, int]:
        """Count issues by severity."""
        counts = {severity.value: 0 for severity in ValidationSeverity}
        for issue in self.issues:
            counts[issue.severity.value] += 1
        return counts


class PolicyValidator:
    """
    Validator for AWS IAM policies against security best practices.

    This class analyzes IAM policy documents to identify security issues,
    compliance violations, and opportunities for least privilege enforcement.

    Example:
        >>> validator = PolicyValidator()
        >>> policy = {...}  # IAM policy document
        >>> result = validator.validate_policy(policy, policy_name="MyPolicy")
        >>> if not result.is_valid:
        ...     print(f"Found {len(result.issues)} issues")
        ...     for issue in result.issues:
        ...         print(f"- {issue.title} ({issue.severity})")
    """

    # Dangerous actions that can lead to privilege escalation
    PRIVILEGE_ESCALATION_ACTIONS = {
        "iam:CreateAccessKey",
        "iam:CreateLoginProfile",
        "iam:UpdateLoginProfile",
        "iam:AttachUserPolicy",
        "iam:AttachGroupPolicy",
        "iam:AttachRolePolicy",
        "iam:PutUserPolicy",
        "iam:PutGroupPolicy",
        "iam:PutRolePolicy",
        "iam:AddUserToGroup",
        "iam:UpdateAssumeRolePolicy",
        "iam:PassRole",
        "lambda:CreateFunction",
        "lambda:UpdateFunctionCode",
        "ec2:RunInstances",
        "sts:AssumeRole",
    }

    # Administrative actions
    ADMIN_ACTIONS = {
        "iam:*",
        "*:*",
        "iam:CreatePolicy",
        "iam:DeletePolicy",
        "organizations:*",
        "account:*",
    }

    # Data access actions
    DATA_ACCESS_ACTIONS = {
        "s3:GetObject",
        "s3:GetObjectVersion",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "rds:DownloadDBLogFilePortion",
        "secretsmanager:GetSecretValue",
        "kms:Decrypt",
        "ssm:GetParameter",
        "ssm:GetParameters",
    }

    def __init__(self) -> None:
        """Initialize the policy validator."""
        pass

    def validate_policy(
        self,
        policy_document: Dict[str, Any],
        policy_name: str = "UnnamedPolicy",
        frameworks: Optional[List[ComplianceFramework]] = None,
    ) -> ValidationResult:
        """
        Validate an IAM policy document against security standards.

        Args:
            policy_document: IAM policy document (JSON parsed to dict)
            policy_name: Name or identifier for the policy
            frameworks: List of compliance frameworks to check against

        Returns:
            ValidationResult with issues and scores
        """
        if frameworks is None:
            frameworks = [ComplianceFramework.CIS_AWS, ComplianceFramework.ZERO_TRUST]

        result = ValidationResult(policy_name=policy_name)

        # Validate policy structure
        if not self._validate_structure(policy_document):
            result.is_valid = False
            result.issues.append(PolicyIssue(
                issue_id="INVALID_STRUCTURE",
                title="Invalid policy structure",
                description="Policy document does not have valid IAM policy structure",
                severity=ValidationSeverity.CRITICAL,
                recommendation="Ensure policy has Version and Statement fields",
                risk_score=100.0,
            ))
            return result

        statements = policy_document.get("Statement", [])
        if not isinstance(statements, list):
            statements = [statements]

        # Run validation checks
        self._check_wildcard_principals(statements, result)
        self._check_wildcard_actions(statements, result)
        self._check_wildcard_resources(statements, result)
        self._check_privilege_escalation(statements, result)
        self._check_missing_conditions(statements, result)
        self._check_unrestricted_actions(statements, result)
        self._check_cis_compliance(statements, result)
        self._check_least_privilege(statements, result)

        # Calculate overall scores
        result.overall_risk_score = self._calculate_risk_score(result.issues)
        result.least_privilege_score = self._calculate_least_privilege_score(
            statements, result.issues
        )
        result.recommendations_count = len(result.issues)

        # Check compliance status
        result.compliance_status = self._check_compliance_status(
            result.issues, frameworks
        )

        # Mark as invalid if critical issues found
        if any(issue.severity == ValidationSeverity.CRITICAL for issue in result.issues):
            result.is_valid = False

        return result

    def validate_policy_string(
        self,
        policy_json: str,
        policy_name: str = "UnnamedPolicy",
        frameworks: Optional[List[ComplianceFramework]] = None,
    ) -> ValidationResult:
        """
        Validate a policy from JSON string.

        Args:
            policy_json: IAM policy as JSON string
            policy_name: Name of the policy
            frameworks: Compliance frameworks to check

        Returns:
            ValidationResult
        """
        try:
            policy_document = json.loads(policy_json)
            return self.validate_policy(policy_document, policy_name, frameworks)
        except json.JSONDecodeError as e:
            result = ValidationResult(policy_name=policy_name, is_valid=False)
            result.issues.append(PolicyIssue(
                issue_id="INVALID_JSON",
                title="Invalid JSON format",
                description=f"Policy is not valid JSON: {str(e)}",
                severity=ValidationSeverity.CRITICAL,
                recommendation="Fix JSON syntax errors",
                risk_score=100.0,
            ))
            return result

    def batch_validate(
        self,
        policies: List[Tuple[str, Dict[str, Any]]],
        frameworks: Optional[List[ComplianceFramework]] = None,
    ) -> List[ValidationResult]:
        """
        Validate multiple policies in batch.

        Args:
            policies: List of (policy_name, policy_document) tuples
            frameworks: Compliance frameworks to check

        Returns:
            List of ValidationResult objects
        """
        return [
            self.validate_policy(policy_doc, policy_name, frameworks)
            for policy_name, policy_doc in policies
        ]

    # Validation check methods

    def _validate_structure(self, policy_document: Dict[str, Any]) -> bool:
        """Validate basic IAM policy structure."""
        return (
            isinstance(policy_document, dict) and
            "Statement" in policy_document
        )

    def _check_wildcard_principals(
        self,
        statements: List[Dict[str, Any]],
        result: ValidationResult,
    ) -> None:
        """Check for wildcard principals allowing public access."""
        affected = []

        for idx, statement in enumerate(statements):
            effect = statement.get("Effect", "")
            if effect != "Allow":
                continue

            principal = statement.get("Principal", {})
            if isinstance(principal, str) and principal == "*":
                affected.append(str(idx))
            elif isinstance(principal, dict):
                if principal.get("AWS") == "*":
                    affected.append(str(idx))

        if affected:
            result.issues.append(PolicyIssue(
                issue_id="WILDCARD_PRINCIPAL",
                title="Wildcard principal allows public access",
                description=(
                    "Policy uses wildcard (*) in Principal, granting access to any AWS "
                    "account or identity. This creates a public access risk."
                ),
                severity=ValidationSeverity.CRITICAL,
                recommendation=(
                    "Replace wildcard principal with specific AWS account IDs, IAM roles, "
                    "or users. Use conditions to further restrict access."
                ),
                compliance_violations=["CIS AWS 1.16", "Zero Trust - Verify explicitly"],
                affected_statements=affected,
                risk_score=95.0,
            ))

    def _check_wildcard_actions(
        self,
        statements: List[Dict[str, Any]],
        result: ValidationResult,
    ) -> None:
        """Check for wildcard actions."""
        affected = []

        for idx, statement in enumerate(statements):
            effect = statement.get("Effect", "")
            if effect != "Allow":
                continue

            actions = statement.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]

            for action in actions:
                if action == "*" or action == "*:*":
                    affected.append(str(idx))
                    break

        if affected:
            result.issues.append(PolicyIssue(
                issue_id="WILDCARD_ACTIONS",
                title="Wildcard actions grant excessive permissions",
                description=(
                    "Policy uses wildcard (*) for actions, granting all possible "
                    "permissions. This violates least privilege principles."
                ),
                severity=ValidationSeverity.HIGH,
                recommendation=(
                    "Specify explicit actions needed. Use service-specific wildcards "
                    "(e.g., s3:Get*) only when necessary."
                ),
                compliance_violations=["CIS AWS 1.16", "Zero Trust - Least privilege"],
                affected_statements=affected,
                risk_score=85.0,
            ))

    def _check_wildcard_resources(
        self,
        statements: List[Dict[str, Any]],
        result: ValidationResult,
    ) -> None:
        """Check for wildcard resources."""
        affected = []

        for idx, statement in enumerate(statements):
            effect = statement.get("Effect", "")
            if effect != "Allow":
                continue

            resources = statement.get("Resource", [])
            if isinstance(resources, str):
                resources = [resources]

            actions = statement.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]

            # Check if wildcard resource with sensitive actions
            has_wildcard = any(res == "*" for res in resources)
            has_sensitive = any(
                action in self.PRIVILEGE_ESCALATION_ACTIONS or
                action in self.ADMIN_ACTIONS
                for action in actions
            )

            if has_wildcard and has_sensitive:
                affected.append(str(idx))

        if affected:
            result.issues.append(PolicyIssue(
                issue_id="WILDCARD_RESOURCES",
                title="Wildcard resources with sensitive actions",
                description=(
                    "Policy combines wildcard resources (*) with sensitive actions, "
                    "granting broad access across all resources."
                ),
                severity=ValidationSeverity.HIGH,
                recommendation=(
                    "Specify explicit resource ARNs. Use ARN patterns with specific "
                    "identifiers instead of wildcards."
                ),
                compliance_violations=["CIS AWS 1.16"],
                affected_statements=affected,
                risk_score=80.0,
            ))

    def _check_privilege_escalation(
        self,
        statements: List[Dict[str, Any]],
        result: ValidationResult,
    ) -> None:
        """Check for privilege escalation risks."""
        affected = []
        escalation_actions = []

        for idx, statement in enumerate(statements):
            effect = statement.get("Effect", "")
            if effect != "Allow":
                continue

            actions = statement.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]

            # Check for privilege escalation actions
            found_escalation = [
                action for action in actions
                if action in self.PRIVILEGE_ESCALATION_ACTIONS
            ]

            if found_escalation:
                affected.append(str(idx))
                escalation_actions.extend(found_escalation)

        if affected:
            result.issues.append(PolicyIssue(
                issue_id="PRIVILEGE_ESCALATION",
                title="Policy allows privilege escalation actions",
                description=(
                    f"Policy grants actions that can be used for privilege escalation: "
                    f"{', '.join(set(escalation_actions)[:5])}"
                ),
                severity=ValidationSeverity.HIGH,
                recommendation=(
                    "Remove or restrict privilege escalation actions. Add conditions "
                    "to limit scope. Use permission boundaries for delegated access."
                ),
                compliance_violations=["CIS AWS 1.16", "NIST AC-6"],
                affected_statements=affected,
                risk_score=85.0,
            ))

    def _check_missing_conditions(
        self,
        statements: List[Dict[str, Any]],
        result: ValidationResult,
    ) -> None:
        """Check for statements missing security conditions."""
        affected = []

        for idx, statement in enumerate(statements):
            effect = statement.get("Effect", "")
            if effect != "Allow":
                continue

            # Check if statement has any conditions
            if "Condition" not in statement:
                actions = statement.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]

                # Only flag if sensitive actions are present
                has_sensitive = any(
                    action in self.PRIVILEGE_ESCALATION_ACTIONS or
                    action in self.DATA_ACCESS_ACTIONS
                    for action in actions
                )

                if has_sensitive:
                    affected.append(str(idx))

        if affected:
            result.issues.append(PolicyIssue(
                issue_id="MISSING_CONDITIONS",
                title="Sensitive actions lack conditional restrictions",
                description=(
                    "Policy allows sensitive actions without conditions like MFA, "
                    "source IP, or time-based restrictions."
                ),
                severity=ValidationSeverity.MEDIUM,
                recommendation=(
                    "Add conditions to restrict access context. Consider: "
                    "aws:MultiFactorAuthPresent, aws:SourceIp, aws:RequestedRegion"
                ),
                compliance_violations=["Zero Trust - Verify explicitly"],
                affected_statements=affected,
                risk_score=60.0,
            ))

    def _check_unrestricted_actions(
        self,
        statements: List[Dict[str, Any]],
        result: ValidationResult,
    ) -> None:
        """Check for unrestricted administrative actions."""
        affected = []

        for idx, statement in enumerate(statements):
            effect = statement.get("Effect", "")
            if effect != "Allow":
                continue

            actions = statement.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]

            resources = statement.get("Resource", [])
            if isinstance(resources, str):
                resources = [resources]

            # Check for admin actions with wildcard resources
            has_admin = any(action in self.ADMIN_ACTIONS for action in actions)
            has_wildcard = any(res == "*" for res in resources)

            if has_admin and has_wildcard:
                affected.append(str(idx))

        if affected:
            result.issues.append(PolicyIssue(
                issue_id="UNRESTRICTED_ADMIN",
                title="Unrestricted administrative permissions",
                description=(
                    "Policy grants administrative actions on all resources without "
                    "restrictions, violating least privilege."
                ),
                severity=ValidationSeverity.CRITICAL,
                recommendation=(
                    "Remove full administrative access. Grant specific permissions "
                    "needed for job function. Use managed policies when appropriate."
                ),
                compliance_violations=["CIS AWS 1.16", "CIS AWS 1.22"],
                affected_statements=affected,
                risk_score=95.0,
            ))

    def _check_cis_compliance(
        self,
        statements: List[Dict[str, Any]],
        result: ValidationResult,
    ) -> None:
        """Check specific CIS AWS Foundations Benchmark controls."""
        # CIS 1.16 - Ensure IAM policies are attached only to groups or roles
        # This would be checked at the policy attachment level, not policy content

        # Additional CIS checks can be added here
        pass

    def _check_least_privilege(
        self,
        statements: List[Dict[str, Any]],
        result: ValidationResult,
    ) -> None:
        """Check overall least privilege compliance."""
        total_actions = 0
        wildcard_count = 0

        for statement in statements:
            effect = statement.get("Effect", "")
            if effect != "Allow":
                continue

            actions = statement.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]

            total_actions += len(actions)
            wildcard_count += sum(1 for a in actions if "*" in a)

        # If more than 30% of actions use wildcards, flag it
        if total_actions > 0 and (wildcard_count / total_actions) > 0.3:
            result.issues.append(PolicyIssue(
                issue_id="EXCESSIVE_WILDCARDS",
                title="Excessive use of wildcard actions",
                description=(
                    f"Policy uses wildcards in {wildcard_count}/{total_actions} actions "
                    f"({wildcard_count/total_actions*100:.1f}%), indicating overly broad permissions."
                ),
                severity=ValidationSeverity.MEDIUM,
                recommendation=(
                    "Review and specify exact actions needed. Wildcards should be used "
                    "sparingly and only for related action groups (e.g., s3:Get*)."
                ),
                compliance_violations=["Zero Trust - Least privilege"],
                affected_statements=[],
                risk_score=55.0,
            ))

    # Scoring methods

    def _calculate_risk_score(self, issues: List[PolicyIssue]) -> float:
        """Calculate overall risk score from issues."""
        if not issues:
            return 0.0

        # Weight issues by severity
        total_score = sum(issue.risk_score for issue in issues)
        max_score = max(issue.risk_score for issue in issues) if issues else 0

        # Weighted average with emphasis on highest risk
        return min((total_score / len(issues)) * 0.6 + max_score * 0.4, 100.0)

    def _calculate_least_privilege_score(
        self,
        statements: List[Dict[str, Any]],
        issues: List[PolicyIssue],
    ) -> float:
        """
        Calculate least privilege compliance score (0-100).

        Higher scores indicate better compliance with least privilege.
        """
        score = 100.0

        # Deduct points for each issue
        for issue in issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                score -= 30.0
            elif issue.severity == ValidationSeverity.HIGH:
                score -= 20.0
            elif issue.severity == ValidationSeverity.MEDIUM:
                score -= 10.0
            elif issue.severity == ValidationSeverity.LOW:
                score -= 5.0

        return max(score, 0.0)

    def _check_compliance_status(
        self,
        issues: List[PolicyIssue],
        frameworks: List[ComplianceFramework],
    ) -> Dict[str, bool]:
        """Check compliance status for each framework."""
        status = {}

        for framework in frameworks:
            # Check if any issues violate this framework
            violations = [
                issue for issue in issues
                if any(framework.value in cv for cv in issue.compliance_violations)
            ]
            status[framework.value] = len(violations) == 0

        return status
