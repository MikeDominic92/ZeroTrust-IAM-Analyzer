# Changelog

All notable changes to the ZeroTrust IAM Analyzer project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-12-04

### Added - AWS IAM Access Analyzer Integration

This release extends ZeroTrust IAM Analyzer with comprehensive AWS cloud provider support, enabling true multi-cloud CIEM (Cloud Infrastructure Entitlement Management) capabilities.

#### New Integrations Module

- **AWS Access Analyzer Connector** (`aws_access_analyzer.py`)
  - Direct integration with AWS IAM Access Analyzer API via boto3
  - Support for listing and retrieving Access Analyzer findings
  - Multi-region and multi-account support
  - Mock mode for demonstrations without AWS credentials
  - Comprehensive error handling and logging
  - Support for both v1 and v2 AWS Access Analyzer APIs

- **Finding Processor** (`finding_processor.py`)
  - Normalize AWS findings into platform-standard format
  - Calculate severity scores (0-100) based on risk factors
  - Identify risk factors including public access, privilege escalation, excessive permissions
  - Generate actionable remediation recommendations
  - Aggregate findings by severity, resource type, and exposure type
  - Summary statistics generation for dashboard integration

- **Policy Validator** (`policy_validator.py`)
  - Validate IAM policies against CIS AWS Foundations Benchmark
  - Detect privilege escalation paths and dangerous permission combinations
  - Identify wildcard principals, actions, and resources
  - Check for missing security conditions (MFA, IP restrictions, time-based)
  - Calculate least privilege compliance scores
  - Support for multiple compliance frameworks (CIS AWS, NIST 800-53, PCI DSS, Zero Trust)
  - Batch policy validation capabilities

#### External Access Detection

New capabilities for identifying exposed AWS resources:

- **S3 Buckets**: Detect publicly accessible buckets and cross-account access
- **IAM Roles**: Identify roles with cross-account assume role permissions
- **KMS Keys**: Find encryption keys shared with external accounts
- **Lambda Functions**: Discover functions with public invocation permissions
- **RDS Snapshots**: Detect database snapshots shared externally
- **ECR Repositories**: Identify container registries with external access
- **Secrets Manager**: Find secrets accessible to external principals
- **SNS Topics**: Detect topics with cross-account subscriptions
- **SQS Queues**: Identify queues with external send/receive permissions

#### Security & Compliance

- **CIS AWS Foundations Benchmark**: Automated validation of IAM policies against CIS controls
- **Privilege Escalation Detection**: Identify permission combinations that enable privilege escalation
- **Least Privilege Scoring**: Calculate compliance scores (0-100) for IAM policies
- **Risk Assessment**: Multi-factor severity scoring system considering:
  - Public vs. cross-account access
  - Presence of security conditions
  - Dangerous action combinations
  - Resource sensitivity levels
  - Administrative permission grants

#### Integration Features

- **Unified Finding Format**: Consistent data structure across GCP and AWS findings
- **Severity Levels**: Standardized CRITICAL, HIGH, MEDIUM, LOW, INFO classifications
- **Compliance Mapping**: Map findings to specific compliance framework controls
- **Risk Factors**: Detailed identification of security risk contributors
- **Remediation Guidance**: Actionable recommendations for each finding type

#### Developer Experience

- **Type Hints**: Full type annotation for better IDE support and code quality
- **Docstrings**: Comprehensive documentation for all classes and methods
- **Error Handling**: Graceful degradation and informative error messages
- **Mock Mode**: Demo capabilities without AWS credentials or live environment
- **Extensibility**: Clean architecture for adding additional cloud providers

### Changed

- **README.md**: Added comprehensive v1.1 section documenting AWS integration
  - Usage examples and code snippets
  - Configuration instructions
  - Required IAM permissions
  - Architecture overview
  - Mock mode documentation

- **requirements.txt**: Added AWS SDK dependencies
  - `boto3>=1.35.0` - AWS SDK for Python
  - `botocore>=1.35.0` - Low-level AWS service access

- **Cross-Cloud Visibility**: Updated status from "Planned" to "Active (v1.1)" for AWS integration

### Technical Details

#### New Files Created

```
backend/app/src/integrations/
├── __init__.py                 # Module initialization with version info
├── aws_access_analyzer.py      # 600+ lines - AWS API connector
├── finding_processor.py        # 700+ lines - Finding normalization
└── policy_validator.py         # 800+ lines - Policy validation engine
```

#### Key Classes

- `AWSAccessAnalyzer`: Main connector class for AWS Access Analyzer API
  - Methods: `list_analyzers()`, `list_findings()`, `get_finding()`, `list_findings_v2()`
  - Support for filtering by status, resource type, and pagination
  - Comprehensive statistics generation

- `FindingProcessor`: Process and normalize AWS findings
  - `NormalizedFinding` dataclass for unified finding structure
  - Severity calculation with configurable risk weights
  - Compliance violation mapping
  - Aggregation and statistics methods

- `PolicyValidator`: Validate IAM policies
  - `ValidationResult` dataclass for validation outcomes
  - `PolicyIssue` dataclass for specific policy problems
  - Multiple validation checks (wildcards, privilege escalation, conditions)
  - Scoring algorithms for risk and least privilege compliance

#### Enumerations

- `FindingStatus`: ACTIVE, ARCHIVED, RESOLVED
- `ResourceType`: 13 AWS resource types supported
- `SeverityLevel`: CRITICAL, HIGH, MEDIUM, LOW, INFO
- `ExposureType`: PUBLIC_INTERNET, CROSS_ACCOUNT, CROSS_ORG, SERVICE_ACCESS, ANONYMOUS
- `ValidationSeverity`: Severity levels for policy issues
- `ComplianceFramework`: CIS_AWS, NIST_800_53, PCI_DSS, ZERO_TRUST

### Integration Examples

#### List Active Findings
```python
from app.src.integrations import AWSAccessAnalyzer

analyzer = AWSAccessAnalyzer(region="us-east-1", profile_name="prod")
findings = analyzer.list_findings(status=FindingStatus.ACTIVE, max_results=50)
```

#### Process and Analyze
```python
from app.src.integrations import FindingProcessor

processor = FindingProcessor()
normalized = processor.process_findings_batch(findings)
stats = processor.get_summary_statistics(normalized)

# Aggregate by severity
by_severity = processor.aggregate_by_severity(normalized)
critical = by_severity['CRITICAL']
```

#### Validate IAM Policy
```python
from app.src.integrations import PolicyValidator

validator = PolicyValidator()
result = validator.validate_policy(policy_doc, policy_name="AdminPolicy")

for issue in result.issues:
    print(f"{issue.severity}: {issue.title}")
    print(f"Recommendation: {issue.recommendation}")
    print(f"Risk Score: {issue.risk_score}/100")
```

### Dependencies

- Python 3.11+
- boto3 >= 1.35.0
- botocore >= 1.35.0

### Compatibility

- Backward compatible with existing GCP and Google Workspace integrations
- No breaking changes to existing APIs or data structures
- New integrations module is optional and can be used independently

### Future Roadmap

- Azure Entra ID and Azure RBAC support (v1.2)
- Multi-cloud unified entitlement dashboard (v1.3)
- Automated remediation workflows (v1.4)
- Real-time alerting and notifications (v1.5)

---

## [1.0.0] - 2024-11-30

### Added

- Initial release of ZeroTrust IAM Analyzer
- Google Cloud Platform IAM analysis
- Google Workspace identity management integration
- Zero Trust security scoring system
- FastAPI backend with PostgreSQL database
- React TypeScript frontend with Material-UI
- Docker containerization support
- Interactive dashboard with visualizations
- Policy analysis and recommendations engine
- User authentication and authorization
- Health check endpoints
- Comprehensive logging and monitoring
- Database migrations with Alembic
- CORS middleware configuration

### Features

- **CIEM Core Capabilities**
  - Excessive permissions detection
  - Least-privilege scoring
  - Entitlement risk analysis
  - Identity-to-resource mapping
  - Policy drift detection

- **GCP Integration**
  - IAM roles and service accounts analysis
  - Resource Manager integration
  - Cloud Identity groups
  - Security Center findings

- **Google Workspace Integration**
  - Directory user and group management
  - Device inventory
  - Admin SDK integration

- **Dashboard & Reporting**
  - Real-time security metrics
  - Historical trend analysis
  - Export capabilities
  - Actionable recommendations

### Documentation

- README.md with comprehensive project overview
- Architecture documentation
- API documentation
- Deployment guides
- Frontend walkthrough
- CIEM capabilities guide

---

## Release Notes

### Version Numbering

- **Major version (X.0.0)**: Breaking changes, major new features, architectural changes
- **Minor version (1.X.0)**: New features, enhancements, backward-compatible changes
- **Patch version (1.0.X)**: Bug fixes, minor improvements, documentation updates

### Contribution Guidelines

Changes should be documented in this changelog following the format:
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes

[1.1.0]: https://github.com/your-repo/ZeroTrust-IAM-Analyzer/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/your-repo/ZeroTrust-IAM-Analyzer/releases/tag/v1.0.0
