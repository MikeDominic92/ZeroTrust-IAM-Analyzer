# Google Cloud Tools Integration Strategy

**Document Status**: Active
**Last Updated**: October 24, 2025
**Author**: Claude Code (B-MAD Analysis)

---

## Overview

This document outlines the integration strategy for the latest Google Cloud Platform security and IAM tools (2025 versions) for the ZeroTrust IAM Analyzer GCP-only MVP.

---

## Core GCP IAM API (v2.19.1+)

**Purpose**: Identity and Access Management policy analysis

**Key Features**:
- IAM API v1: Custom roles, service accounts, policy management
- IAM API v2: Deny policies, principal access boundary policies
- Real-time policy evaluation and permission testing
- Organization-level policy inheritance analysis

**Integration Points**:
- Fetch all IAM policies for projects and organizations
- Analyze role bindings and custom role definitions
- Test IAM policy permissions (testIamPermissions method)
- Monitor policy changes via Cloud Audit Logs

**SDK Package**: `google-cloud-iam>=2.19.1`

**Authentication**: Service account with roles:
- `roles/iam.securityReviewer`
- `roles/iam.roleViewer`
- `roles/resourcemanager.organizationViewer`

---

## Google Cloud Asset Inventory API (v3.26.0+)

**Purpose**: Comprehensive asset and policy metadata tracking

**Key Features**:
- Real-time asset inventory with 35-day history
- Policy Analyzer for access path analysis
- Cross-project policy aggregation
- IAM policy attachment tracking

**Integration Points**:
- `SearchAllResources`: Discover all GCP resources
- `SearchAllIamPolicies`: Aggregate IAM policies across organization
- `AnalyzeIamPolicy`: Identify who has access to what resources
- `AnalyzeIamPolicyLongrunning`: Async analysis for large organizations

**SDK Package**: `google-cloud-asset>=3.26.0`

**Authentication**: Service account with roles:
- `roles/cloudasset.viewer`
- `roles/cloudasset.owner` (for Policy Analyzer)

**Rate Limits**:
- 600 requests per minute per project
- 100 concurrent long-running operations

---

## IAM Recommender API (v2.18.2+)

**Purpose**: ML-based permission insights and least-privilege recommendations

**Key Features**:
- 90-day activity analysis window
- ML-powered over-privileged role detection
- Side-by-side permission comparison
- Automated remediation suggestions

**Integration Points**:
- `ListRecommendations`: Get over-privileged role insights
- `GetRecommendation`: Detailed permission analysis
- `MarkRecommendationClaimed`: Track remediation progress
- `MarkRecommendationSucceeded`: Close recommendations after fix

**SDK Package**: `google-cloud-recommender>=2.18.2`

**Authentication**: Service account with roles:
- `roles/recommender.iamViewer`
- `roles/recommender.iamAdmin` (for applying recommendations)

**Recommendation Types**:
- `google.iam.policy.Recommender`: IAM policy recommendations
- `google.iam.serviceAccount.Recommender`: Service account recommendations

---

## Security Command Center API (v1.31.0+)

**Purpose**: Unified security and risk management platform

**Key Features (Standard Tier)**:
- IAM anomaly detection
- Event Threat Detection (ETD)
- Cloud IDS integration
- Asset discovery and inventory

**Key Features (Premium Tier)**:
- CIEM (Cloud Infrastructure Entitlement Management)
- Container Threat Detection
- VM Threat Detection
- Security Health Analytics

**Integration Points**:
- `ListFindings`: Retrieve IAM-related security findings
- `GroupFindings`: Aggregate findings by category
- `SetFindingState`: Track remediation status
- `CreateSource`: Register ZeroTrust Analyzer as finding source

**SDK Package**: `google-cloud-securitycenter>=1.31.0`

**Authentication**: Service account with roles:
- `roles/securitycenter.findingsViewer`
- `roles/securitycenter.findingsEditor` (for creating findings)

**Finding Categories** (IAM-related):
- `IAM_ANOMALOUS_GRANT`
- `OVERLY_PERMISSIVE_SERVICE_ACCOUNT`
- `DORMANT_SERVICE_ACCOUNT`
- `PRIVILEGE_ESCALATION_RISK`

---

## Google Workspace Admin SDK

**Purpose**: Workspace identity and directory management

**Key Features**:
- User and group enumeration
- Organizational unit analysis
- 2FA/MFA enforcement status
- Workspace security settings audit

**Integration Points**:
- Directory API: List users, groups, org units
- Reports API: Login activity, admin actions
- Chrome Management API: Device security posture

**SDK Package**: `google-api-python-client>=2.123.0`

**Authentication**: Service account with domain-wide delegation

**Required Scopes**:
- `https://www.googleapis.com/auth/admin.directory.user.readonly`
- `https://www.googleapis.com/auth/admin.directory.group.readonly`
- `https://www.googleapis.com/auth/admin.reports.audit.readonly`

---

## BeyondCorp Enterprise (Access Context Manager)

**Purpose**: Context-aware access control and Zero Trust enforcement

**Key Features**:
- Access levels based on device security, location, IP ranges
- Access policies for granular resource protection
- Service perimeters for data exfiltration prevention
- Time-based and credential-strength conditions

**Integration Points**:
- Analyze access level configurations
- Audit service perimeter policies
- Identify resources without Zero Trust protection

**SDK Package**: `google-cloud-access-context-manager` (via `google-cloud-asset`)

**Authentication**: Service account with roles:
- `roles/accesscontextmanager.policyReader`

---

## Cloud Audit Logs

**Purpose**: Real-time IAM change monitoring and compliance audit trail

**Key Features**:
- Admin Activity logs (IAM policy changes)
- Data Access logs (permission grants/checks)
- System Event logs (automated changes)
- Policy denied logs (authorization failures)

**Integration Points**:
- Monitor `SetIamPolicy` method calls
- Track service account key creation
- Alert on high-risk permission grants
- Analyze failed authorization attempts

**SDK Package**: `google-cloud-logging>=3.5.0`

**Authentication**: Service account with roles:
- `roles/logging.viewer`

**Log Filters** (IAM-specific):
```
resource.type="iam_role"
protoPayload.methodName="google.iam.admin.v1.SetIamPolicy"
```

---

## Integration Architecture

### Phase 1: Core IAM Analysis (MVP)
1. **IAM API**: Fetch policies, roles, bindings
2. **Asset Inventory**: Aggregate org-wide policies
3. **IAM Recommender**: Get ML-based insights
4. **Cloud Audit Logs**: Monitor policy changes

### Phase 2: Advanced Security Features
1. **Security Command Center**: IAM anomaly findings
2. **Policy Analyzer**: Access path analysis
3. **BeyondCorp**: Context-aware access audit

### Phase 3: Workspace Integration
1. **Workspace Admin SDK**: User/group analysis
2. **2FA/MFA enforcement audit**
3. **Cross-platform identity correlation**

---

## Authentication Strategy

### Development Environment
- **Method**: Service account JSON key file
- **Storage**: Local file, excluded from version control
- **Environment Variable**: `GCP_SERVICE_ACCOUNT_FILE`

### Production Environment (Recommended)
- **Method**: Workload Identity Federation
- **Benefit**: Short-lived tokens, no static credentials
- **Configuration**: Cloud Run service account with Workload Identity

### Service Account Permissions (Minimum)
```yaml
roles:
  - roles/iam.securityReviewer
  - roles/cloudasset.viewer
  - roles/recommender.iamViewer
  - roles/securitycenter.findingsViewer
  - roles/logging.viewer
```

---

## Rate Limiting and Quotas

### IAM API
- **Quota**: 1,500 read requests per minute per project
- **Strategy**: Batch policy fetching, cache for 5 minutes

### Cloud Asset Inventory
- **Quota**: 600 requests per minute per project
- **Strategy**: Use long-running operations for large orgs

### IAM Recommender
- **Quota**: 600 requests per minute per project
- **Strategy**: Fetch recommendations once per scan

### Security Command Center
- **Quota**: 4,000 read requests per minute (Premium tier)
- **Strategy**: Incremental finding sync every 15 minutes

---

## Zero Trust Mapping

### Tenet 1: Verify Explicitly
- **Tools**: BeyondCorp access levels, 2FA/MFA enforcement (Workspace)
- **Analysis**: Context-aware access coverage, authentication strength

### Tenet 2: Use Least Privilege
- **Tools**: IAM Recommender, Policy Analyzer
- **Analysis**: Over-privileged roles, unused permissions

### Tenet 3: Assume Breach
- **Tools**: Security Command Center, Cloud Audit Logs
- **Analysis**: Anomalous grants, privilege escalation paths

### Tenet 4: Segment Access
- **Tools**: BeyondCorp service perimeters, organization policies
- **Analysis**: Data exfiltration protection, network segmentation

---

## Monitoring and Alerting

### Real-Time Alerts (via Cloud Audit Logs)
- High-risk permission grants (e.g., `roles/owner`, `roles/iam.serviceAccountKeyAdmin`)
- Service account key creation
- IAM policy binding changes

### Scheduled Scans (Daily)
- IAM Recommender insights retrieval
- Security Command Center findings sync
- Policy Analyzer access path analysis

### Trend Analysis (Weekly)
- IAM policy drift detection
- Permission usage trends
- Zero Trust score progression

---

## Implementation Priorities (MVP)

### Week 1-2: Core IAM Integration
- Install SDKs (google-cloud-iam, google-cloud-asset, google-auth)
- Implement service account authentication
- Fetch IAM policies for projects
- Parse and normalize policy structure

### Week 3-4: Recommender and Scoring
- Integrate IAM Recommender API
- Implement Zero Trust scoring engine (4 tenets)
- Build recommendation prioritization logic
- Create basic dashboard

### Week 5-6: Monitoring and Polish
- Implement Cloud Audit Logs monitoring
- Add Security Command Center findings
- Build export/reporting capabilities
- End-to-end testing

---

## References

**Official Documentation**:
- IAM API: https://cloud.google.com/iam/docs/reference/rest
- Cloud Asset Inventory: https://cloud.google.com/asset-inventory/docs/reference/rest
- IAM Recommender: https://cloud.google.com/recommender/docs/recommenders
- Security Command Center: https://cloud.google.com/security-command-center/docs/reference/rest
- BeyondCorp: https://cloud.google.com/beyondcorp-enterprise/docs

**Python SDK Documentation**:
- google-cloud-iam: https://googleapis.dev/python/iam/latest/
- google-cloud-asset: https://googleapis.dev/python/cloudasset/latest/
- google-cloud-recommender: https://googleapis.dev/python/recommender/latest/
- google-cloud-securitycenter: https://googleapis.dev/python/securitycenter/latest/

---

**Document Version**: 1.0.0
**Next Review**: 2025-11-24
