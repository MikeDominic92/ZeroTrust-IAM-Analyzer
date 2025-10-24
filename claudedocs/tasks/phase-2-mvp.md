# Phase 2: MVP - Azure-Only Zero Trust Analysis

**Phase Duration**: 5-7 days (full-time) or 2-3 weeks (part-time)
**Priority**: HIGH - Core business value delivery
**Dependencies**: Phase 1 (Foundation) must be complete

---

## Phase Overview

Phase 2 implements the core business logic of the ZeroTrust IAM Analyzer: analyzing Azure AD conditional access policies and providing Zero Trust security scoring. This MVP focuses exclusively on Azure (Microsoft Entra ID) to prove the concept before expanding to other cloud providers.

**Success Criteria**:
- Users can connect Azure AD tenant with service principal
- System fetches Conditional Access and RBAC policies from Azure
- Zero Trust scoring engine analyzes 4 core tenets (0-100 scale)
- Recommendation engine generates actionable security improvements
- Dashboard displays scores, policies, and recommendations
- Scan results stored with full history and audit trail

**Out of Scope for MVP**:
- Google Cloud Platform integration (Phase 5)
- AWS integration (Phase 5)
- Google Workspace integration (Phase 5)
- Advanced analytics and trends (Phase 4)
- Automated remediation (future enhancement)

---

## Task 2.1: Configure Azure SDK Authentication with Service Principal

**User Story**: As a system admin, I want to configure Azure authentication so the analyzer can access my tenant policies.

**Time Estimate**: 2-3 hours

**Acceptance Criteria**:
- [ ] Azure SDK installed (`azure-identity`, `azure-mgmt-authorization`, `msgraph-core`)
- [ ] Service principal authentication configured
- [ ] Environment variables for Azure credentials validated
- [ ] `AzureAuthService` class created in `services/azure/auth.py`
- [ ] Credential validation endpoint implemented
- [ ] Error handling for invalid credentials
- [ ] Unit tests verify credential creation
- [ ] Integration tests verify Azure AD connection

**Azure Prerequisites** (User must complete):
1. Create Azure AD app registration
2. Create client secret
3. Grant API permissions:
   - `Policy.Read.All` (Conditional Access)
   - `Directory.Read.All` (Users, Groups)
   - `RoleManagement.Read.All` (RBAC)
   - `Application.Read.All` (App registrations)

**Implementation Steps**:
1. Install Azure SDK dependencies:
   ```bash
   pip install azure-identity>=1.15.0 \
               azure-mgmt-authorization>=4.0.0 \
               msgraph-core>=1.0.0
   ```
2. Create `services/azure/auth.py`
3. Implement `AzureAuthService` class
4. Use `ClientSecretCredential` for authentication
5. Implement credential validation method
6. Create configuration schema for Azure credentials
7. Add credential encryption for storage (using app SECRET_KEY)
8. Write tests for credential management

**Code Structure**:
```python
from azure.identity import ClientSecretCredential

class AzureAuthService:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

    async def validate_credentials(self) -> bool:
        """Test connection to Azure AD"""
        pass

    async def get_access_token(self, scope: str) -> str:
        """Get access token for API calls"""
        pass
```

**Environment Variables**:
```bash
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

---

## Task 2.2: Implement Azure Credential Management Service

**User Story**: As a user, I want to securely store Azure credentials so I don't have to re-enter them for each scan.

**Time Estimate**: 3-4 hours

**Acceptance Criteria**:
- [ ] `CloudProviderCredential` model created for storing encrypted credentials
- [ ] Credentials encrypted before database storage (AES-256)
- [ ] Credentials decrypted only when needed
- [ ] POST `/api/v1/credentials/azure` endpoint for adding credentials
- [ ] GET `/api/v1/credentials` endpoint for listing credentials (masked)
- [ ] DELETE `/api/v1/credentials/{id}` endpoint for removing credentials
- [ ] Credentials tied to user account (multi-tenancy support)
- [ ] Unit tests verify encryption/decryption
- [ ] Integration tests verify CRUD operations

**Database Schema** (Alembic migration required):
```sql
CREATE TABLE cloud_provider_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- 'azure', 'gcp', 'aws'
    name VARCHAR(255) NOT NULL, -- User-friendly label
    encrypted_credentials TEXT NOT NULL, -- AES-256 encrypted JSON
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_validated_at TIMESTAMP
);
```

**API Specification**:
```
POST /api/v1/credentials/azure
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
  "name": "Production Azure Tenant",
  "tenant_id": "tenant-uuid",
  "client_id": "client-uuid",
  "client_secret": "secret-value"
}

Success Response (201):
{
  "id": "credential-uuid",
  "provider": "azure",
  "name": "Production Azure Tenant",
  "tenant_id": "tenant-uuid",
  "is_active": true,
  "created_at": "2025-10-24T10:30:00Z",
  "last_validated_at": "2025-10-24T10:30:00Z"
}
```

**Implementation Steps**:
1. Create Alembic migration for credentials table
2. Create `CloudProviderCredential` model
3. Implement encryption service using `cryptography.fernet`
4. Create CRUD endpoints in `api/v1/credentials.py`
5. Implement credential validation on creation
6. Mask sensitive data in responses (show only last 4 chars of secrets)
7. Write tests for encryption security
8. Test multi-user isolation

**Security Notes**:
- Use Fernet symmetric encryption (AES-128-CBC)
- Derive encryption key from app SECRET_KEY + user-specific salt
- Never log or return decrypted credentials
- Implement credential rotation reminder (90 days)

---

## Task 2.3: Implement Azure AD Tenant Connection Validation

**User Story**: As a user, I want to test my Azure connection so I know the credentials work before running scans.

**Time Estimate**: 2 hours

**Acceptance Criteria**:
- [ ] POST `/api/v1/credentials/{id}/validate` endpoint created
- [ ] Endpoint tests connection to Azure AD
- [ ] Verifies required API permissions granted
- [ ] Returns list of available permissions
- [ ] Returns tenant information (name, domain)
- [ ] Updates `last_validated_at` timestamp on success
- [ ] Returns detailed error messages on failure
- [ ] Unit tests verify validation logic
- [ ] Integration tests verify Azure API calls

**API Specification**:
```
POST /api/v1/credentials/{credential_id}/validate
Authorization: Bearer <access_token>

Success Response (200):
{
  "valid": true,
  "tenant_name": "Contoso Corp",
  "tenant_domain": "contoso.onmicrosoft.com",
  "permissions": [
    "Policy.Read.All",
    "Directory.Read.All",
    "RoleManagement.Read.All"
  ],
  "validated_at": "2025-10-24T10:30:00Z"
}

Error Response (400):
{
  "valid": false,
  "error": "Invalid client secret",
  "error_code": "INVALID_CREDENTIALS"
}
```

**Validation Checks**:
1. Authenticate with Azure AD
2. Call Microsoft Graph API: `GET /v1.0/organization`
3. Verify required permissions in token claims
4. Check conditional access policy read permission
5. Check directory read permission
6. Check role management read permission

---

## Task 2.4: Create Alembic Migrations for CloudProvider and TenantConnection Models

**User Story**: As a developer, I need database tables for storing cloud provider connections and scan metadata.

**Time Estimate**: 1-2 hours

**Acceptance Criteria**:
- [ ] `cloud_provider_credentials` table created
- [ ] `tenant_connections` table created (if needed for additional metadata)
- [ ] Foreign keys to `users` table configured
- [ ] Indexes on frequently queried columns
- [ ] Migration applies successfully
- [ ] Migration rollback works correctly
- [ ] Database schema matches model definitions

**Implementation Steps**:
1. Create migration: `alembic revision --autogenerate -m "Add cloud provider credentials"`
2. Review generated SQL
3. Add indexes for performance
4. Apply migration: `alembic upgrade head`
5. Verify with SQL queries

---

## Task 2.5: Implement Azure Conditional Access Policy Fetching Service

**User Story**: As a security analyst, I want to fetch conditional access policies so I can analyze Zero Trust coverage.

**Time Estimate**: 4-5 hours

**Acceptance Criteria**:
- [ ] `AzurePolicyService` class created in `services/azure/policies.py`
- [ ] Fetches conditional access policies from Microsoft Graph API
- [ ] Parses policy JSON into normalized format
- [ ] Handles pagination for large policy sets
- [ ] Implements rate limiting and retry logic
- [ ] Caches policy data in Redis (15-minute TTL)
- [ ] Returns list of `Policy` objects
- [ ] Unit tests with mocked Azure responses
- [ ] Integration tests with real Azure tenant (optional)

**Microsoft Graph API Endpoint**:
```
GET https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies
```

**Policy Normalization**:
```python
{
  "id": "policy-uuid",
  "name": "Require MFA for admins",
  "state": "enabled",
  "conditions": {
    "users": {"includeUsers": ["All"]},
    "applications": {"includeApplications": ["All"]},
    "locations": {"includeLocations": ["All"]}
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["mfa"]
  },
  "sessionControls": {}
}
```

**Implementation Steps**:
1. Create `services/azure/policies.py`
2. Implement Microsoft Graph API client
3. Fetch conditional access policies
4. Parse policy structure
5. Handle pagination with `@odata.nextLink`
6. Implement exponential backoff for rate limits
7. Cache policies in Redis
8. Write comprehensive tests

---

## Task 2.6: Implement Azure RBAC Policy Fetching Service

**User Story**: As a security analyst, I want to fetch RBAC role assignments so I can analyze least privilege compliance.

**Time Estimate**: 4-5 hours

**Acceptance Criteria**:
- [ ] Extends `AzurePolicyService` class
- [ ] Fetches role assignments from Azure Management API
- [ ] Fetches role definitions for permission details
- [ ] Identifies over-privileged assignments
- [ ] Handles subscription-level and resource-group-level roles
- [ ] Normalizes role data into standard format
- [ ] Caches role data in Redis
- [ ] Unit tests with mocked responses
- [ ] Integration tests verify data accuracy

**Azure Management API Endpoints**:
```
GET https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Authorization/roleAssignments
GET https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Authorization/roleDefinitions
```

**Role Assignment Normalization**:
```python
{
  "id": "assignment-uuid",
  "role_name": "Contributor",
  "role_id": "b24988ac-6180-42a0-ab88-20f7382dd24c",
  "principal_id": "user-uuid",
  "principal_type": "User",
  "scope": "/subscriptions/{sub-id}",
  "permissions": [
    "*/read",
    "*/write",
    "Microsoft.Support/*"
  ]
}
```

---

## Task 2.7: Create Alembic Migrations for Policy and PolicyRule Models

**User Story**: As a developer, I need database tables for storing fetched policies and analysis results.

**Time Estimate**: 1-2 hours

**Acceptance Criteria**:
- [ ] `policies` table created with JSONB column for policy data
- [ ] `policy_rules` table created for normalized rule storage
- [ ] Foreign keys to `cloud_provider_credentials` table
- [ ] Indexes on policy type and provider
- [ ] JSONB GIN index for fast JSON queries
- [ ] Migration applies successfully

**Database Schema**:
```sql
CREATE TABLE policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    credential_id UUID NOT NULL REFERENCES cloud_provider_credentials(id),
    provider VARCHAR(50) NOT NULL,
    policy_type VARCHAR(100) NOT NULL, -- 'conditional_access', 'rbac', etc.
    external_id VARCHAR(255) NOT NULL, -- Policy ID from cloud provider
    name VARCHAR(500),
    policy_data JSONB NOT NULL,
    state VARCHAR(50), -- 'enabled', 'disabled', 'report_only'
    fetched_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_policies_jsonb ON policies USING GIN (policy_data);
CREATE INDEX idx_policies_type ON policies(policy_type);
```

---

## Task 2.8: Implement Policy Parsing and Normalization Logic

**User Story**: As a developer, I need normalized policy data so the scoring engine can analyze policies consistently.

**Time Estimate**: 3-4 hours

**Acceptance Criteria**:
- [ ] `PolicyParser` class created in `services/azure/parser.py`
- [ ] Parses conditional access policies into standard format
- [ ] Parses RBAC policies into standard format
- [ ] Extracts key security attributes (MFA required, device compliance, etc.)
- [ ] Handles missing or null fields gracefully
- [ ] Returns structured `PolicyAnalysis` object
- [ ] Unit tests with real policy examples
- [ ] Handles edge cases (disabled policies, legacy formats)

**Normalized Policy Attributes**:
```python
class PolicyAnalysis:
    mfa_required: bool
    device_compliance_required: bool
    approved_apps_required: bool
    locations_restricted: bool
    sign_in_frequency_set: bool
    persistent_browser_blocked: bool
    legacy_auth_blocked: bool
    privileged_roles_covered: bool
```

---

## Task 2.9: Implement Tenet 1 Analysis - Verify Explicitly (Authentication Strength)

**User Story**: As a security analyst, I want to see authentication strength analysis so I can identify weak authentication policies.

**Time Estimate**: 3-4 hours

**Acceptance Criteria**:
- [ ] `ZeroTrustScorer` class created in `services/scoring/zerotrust.py`
- [ ] Implements Tenet 1 analysis: "Verify explicitly"
- [ ] Checks for MFA enforcement across all users
- [ ] Checks for phishing-resistant MFA methods (FIDO2, Windows Hello)
- [ ] Checks for legacy authentication blocking
- [ ] Checks for authentication strength policies
- [ ] Returns score 0-100 for this tenet
- [ ] Identifies specific gaps with recommendations
- [ ] Unit tests with various policy scenarios
- [ ] Integration tests verify scoring accuracy

**Scoring Logic**:
```python
def score_tenet_1_verify_explicitly(policies: List[Policy]) -> TenetScore:
    """
    Scoring criteria:
    - MFA for all users: 40 points
    - Phishing-resistant MFA available: 20 points
    - Legacy auth blocked: 20 points
    - Authentication strength policies: 20 points
    Total: 100 points
    """
    score = 0
    gaps = []

    # Check MFA enforcement
    if has_mfa_for_all_users(policies):
        score += 40
    else:
        gaps.append("MFA not enforced for all users")

    # More checks...

    return TenetScore(
        tenet_number=1,
        tenet_name="Verify explicitly",
        score=score,
        max_score=100,
        gaps=gaps,
        recommendations=generate_recommendations(gaps)
    )
```

---

## Task 2.10: Implement Tenet 2 Analysis - Use Least Privilege Access

**User Story**: As a security analyst, I want to see least privilege analysis so I can identify over-privileged accounts.

**Time Estimate**: 3-4 hours

**Acceptance Criteria**:
- [ ] Implements Tenet 2 analysis: "Use least privilege access"
- [ ] Checks for custom role definitions vs built-in roles
- [ ] Identifies users with Owner or Contributor at subscription level
- [ ] Checks for permanent vs time-bound role assignments (PIM)
- [ ] Identifies service principals with excessive permissions
- [ ] Returns score 0-100 for this tenet
- [ ] Provides list of over-privileged accounts
- [ ] Unit tests with various RBAC scenarios

**Scoring Logic**:
```python
def score_tenet_2_least_privilege(role_assignments: List[RoleAssignment]) -> TenetScore:
    """
    Scoring criteria:
    - No Owner at subscription level: 30 points
    - <10% accounts with Contributor: 25 points
    - PIM enabled for privileged roles: 25 points
    - Custom roles properly scoped: 20 points
    Total: 100 points
    """
    pass
```

---

## Task 2.11: Implement Tenet 3 Analysis - Assume Breach (Conditional Access)

**User Story**: As a security analyst, I want to see breach assumption analysis so I can identify gaps in conditional access controls.

**Time Estimate**: 3-4 hours

**Acceptance Criteria**:
- [ ] Implements Tenet 3 analysis: "Assume breach"
- [ ] Checks for device compliance requirements
- [ ] Checks for approved client apps requirements
- [ ] Checks for sign-in risk-based policies
- [ ] Checks for user risk-based policies
- [ ] Checks for location-based restrictions
- [ ] Returns score 0-100 for this tenet
- [ ] Unit tests with various policy configurations

**Scoring Logic**:
```python
def score_tenet_3_assume_breach(policies: List[Policy]) -> TenetScore:
    """
    Scoring criteria:
    - Device compliance required: 25 points
    - Approved client apps: 20 points
    - Sign-in risk policies: 25 points
    - User risk policies: 20 points
    - Location restrictions: 10 points
    Total: 100 points
    """
    pass
```

---

## Task 2.12: Implement Tenet 4 Analysis - Verify End-to-End Encryption (Session Policies)

**User Story**: As a security analyst, I want to see session security analysis so I can identify gaps in session protection.

**Time Estimate**: 2-3 hours

**Acceptance Criteria**:
- [ ] Implements Tenet 4 analysis: "Verify encryption"
- [ ] Checks for sign-in frequency policies
- [ ] Checks for persistent browser session blocking
- [ ] Checks for app enforced restrictions
- [ ] Checks for cloud app security integration
- [ ] Returns score 0-100 for this tenet
- [ ] Unit tests verify session policy analysis

**Scoring Logic**:
```python
def score_tenet_4_encryption(policies: List[Policy]) -> TenetScore:
    """
    Scoring criteria:
    - Sign-in frequency set (< 7 days): 40 points
    - Persistent browser blocked: 30 points
    - App restrictions enforced: 20 points
    - Cloud app security integration: 10 points
    Total: 100 points
    """
    pass
```

---

## Task 2.13: Implement Composite Zero Trust Score Calculation

**User Story**: As a security analyst, I want to see an overall Zero Trust score so I can quickly assess security posture.

**Time Estimate**: 2 hours

**Acceptance Criteria**:
- [ ] Combines scores from all 4 tenets
- [ ] Weighted average calculation (configurable weights)
- [ ] Returns overall score 0-100
- [ ] Categorizes score (Critical: 0-40, Poor: 41-60, Fair: 61-75, Good: 76-90, Excellent: 91-100)
- [ ] Stores score history for trend analysis
- [ ] Unit tests verify calculation accuracy

**Composite Score Formula**:
```python
def calculate_composite_score(tenet_scores: List[TenetScore]) -> float:
    """
    Default weights (equal):
    Tenet 1: 25%
    Tenet 2: 25%
    Tenet 3: 25%
    Tenet 4: 25%
    """
    weights = [0.25, 0.25, 0.25, 0.25]
    composite = sum(score.score * weight
                    for score, weight in zip(tenet_scores, weights))
    return round(composite, 2)
```

---

## Task 2.14: Implement Recommendation Generation Engine

**User Story**: As a security analyst, I want actionable recommendations so I can improve my security posture.

**Time Estimate**: 4-5 hours

**Acceptance Criteria**:
- [ ] `RecommendationEngine` class created in `services/scoring/recommendations.py`
- [ ] Generates recommendations based on policy gaps
- [ ] Prioritizes recommendations by severity (Critical, High, Medium, Low)
- [ ] Includes implementation guidance for each recommendation
- [ ] Links to Microsoft documentation for remediation steps
- [ ] Estimates effort (hours) for each recommendation
- [ ] Estimates impact (score increase) for each recommendation
- [ ] Unit tests verify recommendation generation

**Recommendation Structure**:
```python
class Recommendation:
    id: UUID
    tenet_number: int
    severity: str  # 'critical', 'high', 'medium', 'low'
    title: str
    description: str
    impact: str  # What happens if not addressed
    remediation: str  # Step-by-step fix
    effort_hours: int  # Estimated implementation time
    score_impact: int  # Potential score increase
    azure_doc_link: str
    priority: int  # 1-10 ranking
```

**Example Recommendations**:
1. **Enable MFA for all users** (Critical, +40 points)
2. **Block legacy authentication** (High, +20 points)
3. **Require device compliance** (High, +25 points)
4. **Implement sign-in frequency limits** (Medium, +10 points)

---

## Task 2.15: Create Alembic Migrations for Recommendation and Finding Models

**User Story**: As a developer, I need database tables for storing recommendations and security findings.

**Time Estimate**: 1 hour

**Acceptance Criteria**:
- [ ] `recommendations` table created
- [ ] `findings` table created (specific policy violations)
- [ ] Foreign keys to `scans` table
- [ ] Indexes on severity and priority
- [ ] Migration applies successfully

**Database Schema**:
```sql
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id UUID NOT NULL REFERENCES scans(id),
    tenet_number INTEGER,
    severity VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    remediation TEXT,
    effort_hours INTEGER,
    score_impact INTEGER,
    priority INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Task 2.16: Implement Scan Execution Endpoint

**User Story**: As a user, I want to initiate a security scan so I can analyze my Azure tenant policies.

**Time Estimate**: 4-5 hours

**Acceptance Criteria**:
- [ ] POST `/api/v1/scans` endpoint created
- [ ] Accepts credential ID and scan configuration
- [ ] Validates credential ownership
- [ ] Initiates background scan task
- [ ] Returns scan ID immediately (async execution)
- [ ] Updates scan status in database (pending, running, completed, failed)
- [ ] Sends webhook/email on completion (optional)
- [ ] Unit tests verify endpoint logic
- [ ] Integration tests verify full scan workflow

**API Specification**:
```
POST /api/v1/scans
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
  "credential_id": "credential-uuid",
  "scan_type": "full",  // 'full' or 'quick'
  "notify_on_completion": true
}

Success Response (202):
{
  "scan_id": "scan-uuid",
  "status": "pending",
  "created_at": "2025-10-24T10:30:00Z",
  "estimated_duration_minutes": 5
}
```

**Scan Workflow**:
1. Validate credential and user ownership
2. Create scan record with status "pending"
3. Queue background task (Celery or inline for MVP)
4. Fetch policies from Azure (Task 2.5, 2.6)
5. Parse policies (Task 2.8)
6. Run Zero Trust scoring (Tasks 2.9-2.13)
7. Generate recommendations (Task 2.14)
8. Update scan status to "completed"
9. Store results in database

---

## Task 2.17: Implement Scan Results Retrieval Endpoint

**User Story**: As a user, I want to retrieve scan results so I can view my security analysis.

**Time Estimate**: 2-3 hours

**Acceptance Criteria**:
- [ ] GET `/api/v1/scans/{scan_id}` endpoint created
- [ ] Returns full scan results including scores and recommendations
- [ ] Includes policy details and tenet breakdowns
- [ ] Handles in-progress scans (status updates)
- [ ] Returns 404 for non-existent scans
- [ ] Returns 403 if user doesn't own scan
- [ ] Unit tests verify response structure
- [ ] Integration tests verify data accuracy

**API Specification**:
```
GET /api/v1/scans/{scan_id}
Authorization: Bearer <access_token>

Success Response (200):
{
  "scan_id": "scan-uuid",
  "status": "completed",
  "credential": {
    "id": "credential-uuid",
    "name": "Production Azure Tenant"
  },
  "overall_score": 72.5,
  "score_category": "Fair",
  "tenet_scores": [
    {
      "tenet_number": 1,
      "tenet_name": "Verify explicitly",
      "score": 80,
      "max_score": 100,
      "gaps": ["MFA not enforced for guest users"]
    },
    // More tenets...
  ],
  "recommendations": [
    {
      "id": "rec-uuid",
      "severity": "critical",
      "title": "Enable MFA for all users",
      "score_impact": 20,
      "effort_hours": 2
    },
    // More recommendations...
  ],
  "policy_count": 12,
  "finding_count": 8,
  "started_at": "2025-10-24T10:30:00Z",
  "completed_at": "2025-10-24T10:35:00Z",
  "duration_seconds": 300
}
```

---

## Task 2.18: Implement Dashboard Overview Endpoint

**User Story**: As a user, I want to see a dashboard overview so I can quickly assess my security posture.

**Time Estimate**: 3-4 hours

**Acceptance Criteria**:
- [ ] GET `/api/v1/dashboard/overview` endpoint created
- [ ] Returns latest scan summary
- [ ] Shows score trend (if multiple scans)
- [ ] Highlights top recommendations
- [ ] Shows scan history summary
- [ ] Includes credential status
- [ ] Unit tests verify response structure
- [ ] Integration tests verify aggregation logic

**API Specification**:
```
GET /api/v1/dashboard/overview
Authorization: Bearer <access_token>

Success Response (200):
{
  "current_score": 72.5,
  "previous_score": 68.0,
  "score_change": +4.5,
  "score_category": "Fair",
  "last_scan": {
    "scan_id": "scan-uuid",
    "completed_at": "2025-10-24T10:35:00Z",
    "credential_name": "Production Azure Tenant"
  },
  "top_recommendations": [
    {
      "severity": "critical",
      "title": "Enable MFA for all users",
      "score_impact": 20
    },
    // Top 5 recommendations...
  ],
  "statistics": {
    "total_scans": 15,
    "total_policies_analyzed": 180,
    "critical_findings": 3,
    "high_findings": 8
  },
  "credentials": [
    {
      "id": "credential-uuid",
      "name": "Production Azure Tenant",
      "provider": "azure",
      "last_scan": "2025-10-24T10:35:00Z"
    }
  ]
}
```

---

## Task 2.19: Implement Recommendations List Endpoint

**User Story**: As a user, I want to filter and sort recommendations so I can prioritize security improvements.

**Time Estimate**: 2-3 hours

**Acceptance Criteria**:
- [ ] GET `/api/v1/recommendations` endpoint created
- [ ] Supports filtering by severity (critical, high, medium, low)
- [ ] Supports filtering by tenet
- [ ] Supports sorting by priority, score_impact, effort
- [ ] Supports pagination (limit, offset)
- [ ] Returns recommendations from latest scan
- [ ] Unit tests verify filtering and sorting
- [ ] Integration tests verify query performance

**API Specification**:
```
GET /api/v1/recommendations?severity=critical,high&sort=priority&limit=10
Authorization: Bearer <access_token>

Success Response (200):
{
  "total": 25,
  "limit": 10,
  "offset": 0,
  "recommendations": [
    {
      "id": "rec-uuid",
      "tenet_number": 1,
      "severity": "critical",
      "title": "Enable MFA for all users",
      "description": "Multi-factor authentication is not enforced...",
      "remediation": "1. Navigate to Azure AD...",
      "effort_hours": 2,
      "score_impact": 20,
      "priority": 1
    },
    // More recommendations...
  ]
}
```

---

## Phase 2 Completion Checklist

Before proceeding to Phase 3, verify:

- [ ] All 15 tasks completed and checked off
- [ ] Azure SDK integration functional
- [ ] Policy fetching from Azure AD works
- [ ] Zero Trust scoring engine produces accurate scores
- [ ] Recommendation engine generates actionable advice
- [ ] All API endpoints tested and documented
- [ ] Database migrations applied successfully
- [ ] Test coverage >80% for scoring logic
- [ ] Manual testing complete with real Azure tenant
- [ ] Code reviewed and merged to main branch

**Phase 2 Deliverables**:
1. Azure AD integration with credential management
2. Conditional Access and RBAC policy fetching
3. Zero Trust scoring engine (4 tenets)
4. Recommendation generation engine
5. Scan execution and results APIs
6. Dashboard overview API
7. Comprehensive test suite for core logic

**Ready for Phase 3**: Testing and quality assurance

---

## Common Issues and Solutions

**Issue**: Azure API rate limits causing scan failures
- **Solution**: Implement exponential backoff, cache policies in Redis, batch requests

**Issue**: Missing API permissions cause authorization errors
- **Solution**: Validate permissions during credential creation, provide clear error messages

**Issue**: Slow scan execution
- **Solution**: Parallelize policy fetching, optimize database queries, use Redis caching

**Issue**: Inaccurate scoring due to edge cases
- **Solution**: Comprehensive unit tests with real policy examples, regular score validation

**Issue**: Recommendations not actionable enough
- **Solution**: Add step-by-step remediation guides, link to Microsoft documentation

---

**Next Phase**: [Phase 3 - Testing and Production Readiness](./phase-3-production.md)
