# Audit Evidence Module

> **Chainguard Relevance:** This module demonstrates "preparing evidence for SOC 2, ISO27001, and other regulatory audits" - a key requirement for IT Engineer (Identity/IAM) roles.

## Overview

The Audit Evidence Module generates compliance-ready audit evidence packages from CIEM platform findings. It maps cloud IAM findings to compliance framework controls and produces auditor-friendly documentation.

## Features

- **Multi-Framework Support:** SOC 2, ISO 27001, NIST 800-53, CIS, PCI-DSS
- **Multi-Cloud Coverage:** AWS, GCP, Azure
- **Evidence Types:** Entitlements, risks, privilege escalation, external access, compliance scans
- **Export Formats:** JSON, Markdown, PDF
- **Integrity Verification:** SHA256 hashing for evidence packages

## Quick Start

```python
from audit import AuditEvidenceGenerator, ComplianceFramework
from datetime import date

# Initialize generator
generator = AuditEvidenceGenerator(generated_by="iam-team@example.com")

# Generate evidence from findings
entitlement_evidence = generator.generate_entitlement_evidence(
    cloud_provider="aws",
    findings=[
        {
            "resource_type": "iam_user",
            "resource_id": "arn:aws:iam::123456789012:user/admin",
            "description": "User with excessive permissions",
            "finding": "AdministratorAccess policy attached",
            "severity": "critical",
            "risk_score": 95.0
        }
    ]
)

# Create evidence package
package = generator.create_evidence_package(
    framework=ComplianceFramework.SOC2,
    evidence_items=entitlement_evidence,
    audit_period_start=date(2025, 1, 1),
    audit_period_end=date(2025, 12, 31)
)

# Export to JSON
generator.export_package_to_json(package, "./soc2-evidence.json")

# Export to Markdown
markdown = generator.export_package_to_markdown(package)
```

## Evidence Types

| Type | Description | Controls Mapped |
|------|-------------|-----------------|
| `ENTITLEMENT_ANALYSIS` | IAM policy and permission analysis | SOC2:CC6.1, ISO:A.5.15, NIST:AC-2 |
| `RISK_ASSESSMENT` | Risk scoring and severity assessment | SOC2:CC6.3, ISO:A.8.2, NIST:AC-6 |
| `PRIVILEGE_ESCALATION` | Potential privilege escalation paths | SOC2:CC6.8, ISO:A.8.2 |
| `EXTERNAL_ACCESS` | External entity access exposure | SOC2:CC6.6, ISO:A.5.18 |
| `POLICY_VALIDATION` | IAM policy validation checks | SOC2:CC6.1, ISO:A.5.15, CIS:1.1 |
| `COMPLIANCE_SCAN` | CIS/NIST benchmark scan results | CIS:*, NIST:* |

## Control Mappings

### SOC 2 Trust Services Criteria

| Control | Name | Evidence Types |
|---------|------|----------------|
| CC6.1 | Logical Access Security | Entitlements, Policy Validation |
| CC6.3 | Role-Based Access | Entitlements, Risk Assessment |
| CC6.6 | Access Monitoring | Access Review, External Access |
| CC6.8 | Privileged Access | Privilege Escalation, Risk Assessment |

### ISO 27001:2022 Annex A

| Control | Name | Evidence Types |
|---------|------|----------------|
| A.5.15 | Access Control | Entitlements, Policy Validation |
| A.5.18 | Access Rights | Access Review, Entitlements |
| A.8.2 | Privileged Access Rights | Privilege Escalation, Risk Assessment |

### NIST 800-53

| Control | Name | Evidence Types |
|---------|------|----------------|
| AC-2 | Account Management | Entitlements, Access Review |
| AC-6 | Least Privilege | Risk Assessment, Entitlements |

## Evidence Package Structure

```json
{
  "package_id": "EVP-20251205120000",
  "framework": "SOC2",
  "generated_at": "2025-12-05T12:00:00Z",
  "generated_by": "iam-team@example.com",
  "audit_period_start": "2025-01-01",
  "audit_period_end": "2025-12-31",
  "total_findings": 25,
  "critical_findings": 3,
  "high_findings": 8,
  "medium_findings": 10,
  "low_findings": 4,
  "resolved_findings": 15,
  "sha256_hash": "abc123...",
  "evidence_items": [
    {
      "id": "uuid",
      "evidence_type": "entitlement_analysis",
      "title": "Finding title",
      "description": "Finding description",
      "cloud_provider": "aws",
      "resource_type": "iam_user",
      "resource_id": "arn:aws:iam::...",
      "severity": "critical",
      "risk_score": 95.0,
      "remediation_status": "resolved",
      "control_mappings": ["SOC2:CC6.1", "ISO27001:A.5.15"]
    }
  ]
}
```

## Integration with CIEM Platform

### Generate Evidence from Analysis

```python
from app.analyzers import EntitlementAnalyzer, RiskAnalyzer
from audit import AuditEvidenceGenerator

# Run CIEM analysis
entitlement_analyzer = EntitlementAnalyzer()
risk_analyzer = RiskAnalyzer()

aws_entitlements = entitlement_analyzer.analyze_aws()
aws_risks = risk_analyzer.assess_aws()

# Generate evidence
generator = AuditEvidenceGenerator()
evidence_items = []

evidence_items.extend(
    generator.generate_entitlement_evidence("aws", aws_entitlements)
)
evidence_items.extend(
    generator.generate_risk_evidence("aws", aws_risks)
)

# Package for auditors
package = generator.create_evidence_package(
    framework=ComplianceFramework.SOC2,
    evidence_items=evidence_items,
    audit_period_start=date(2025, 1, 1),
    audit_period_end=date(2025, 12, 31)
)
```

### API Endpoints

```python
# FastAPI endpoint for evidence generation
@router.post("/api/v1/audit/evidence")
async def generate_evidence(
    framework: ComplianceFramework,
    start_date: date,
    end_date: date,
    cloud_providers: List[str] = ["aws", "gcp"]
):
    generator = AuditEvidenceGenerator()
    # ... generate and return package
```

## Best Practices

1. **Regular Generation:** Generate evidence continuously, not just before audits
2. **Include Context:** Raw findings plus explanatory summaries
3. **Track Remediation:** Update remediation status as findings are addressed
4. **Maintain Integrity:** Use SHA256 hashes for tamper detection
5. **Retain Evidence:** Keep packages for 7+ years per compliance requirements

## Files

| File | Description |
|------|-------------|
| `evidence_generator.py` | Main evidence generation logic |
| `__init__.py` | Module exports |
| `README.md` | This documentation |

## Author

**Mike Dominic** - December 2025

This module demonstrates audit evidence generation capabilities aligned with Chainguard IT Engineer (Identity/IAM) requirements for compliance audit preparation.
