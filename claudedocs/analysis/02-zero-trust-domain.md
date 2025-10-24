# Zero Trust Domain Knowledge

**Document Date**: October 24, 2025
**Repository**: [MikeDominic92/ZeroTrust-IAM-Analyzer](https://github.com/MikeDominic92/ZeroTrust-IAM-Analyzer)
**Purpose**: Comprehensive reference for Zero Trust Architecture principles and IAM security best practices

---

## Table of Contents

1. [NIST SP 800-207 Zero Trust Architecture](#nist-sp-800-207-zero-trust-architecture)
2. [Seven Zero Trust Tenets](#seven-zero-trust-tenets)
3. [OWASP IAM Security Best Practices](#owasp-iam-security-best-practices)
4. [Multi-Cloud IAM Considerations](#multi-cloud-iam-considerations)
5. [Industry Standards and Compliance Frameworks](#industry-standards-and-compliance-frameworks)
6. [Zero Trust Implementation Patterns](#zero-trust-implementation-patterns)
7. [Zero Trust Maturity Models](#zero-trust-maturity-models)

---

## NIST SP 800-207 Zero Trust Architecture

### Overview

**Publication**: NIST Special Publication 800-207
**Title**: Zero Trust Architecture
**Published**: August 2020
**Authority**: National Institute of Standards and Technology (NIST)

NIST SP 800-207 defines Zero Trust Architecture (ZTA) as a cybersecurity paradigm focused on resource protection based on the premise that trust is never granted implicitly but must be continually evaluated. The document provides a comprehensive framework for implementing Zero Trust principles across enterprise networks and cloud environments.

### Core Philosophy

**Traditional Perimeter Security**: Trust is determined by network location (inside vs. outside the firewall)
**Zero Trust Security**: No implicit trust, continuous verification of all access requests

**Key Principle**: "Never trust, always verify"

### Fundamental Concepts

**1. Zero Trust Network**
- Eliminates the concept of "trusted" vs. "untrusted" networks
- Treats all networks as potentially hostile
- Every access request requires authentication and authorization
- Network location is not a primary factor in security decisions

**2. Policy Enforcement Point (PEP)**
- Component that enables, monitors, and terminates connections
- Enforces access decisions made by the Policy Decision Point
- Examples: reverse proxies, API gateways, identity-aware proxies

**3. Policy Decision Point (PDP)**
- Makes and logs access decisions
- Evaluates multiple factors: identity, device, location, behavior
- Integrates with threat intelligence and security information
- Continuously reassesses trust

**4. Policy Engine**
- Core component that computes access decisions
- Evaluates trust algorithms using multiple data sources
- Considers dynamic context: time, location, device posture, behavioral analytics
- Maintains security policies and compliance requirements

**5. Trust Algorithm**
- Mathematical model that computes trust scores
- Inputs: user identity, device state, behavioral patterns, threat intelligence
- Output: allow/deny decision with conditions
- Continuously updated based on new information

### Architecture Components

**1. Subject (User or Service)**
- Human users with credentials
- Service accounts and workload identities
- IoT devices and automated systems

**2. Resource**
- Data assets (databases, files, APIs)
- Applications and services
- Infrastructure components
- Network segments

**3. Identity Provider (IdP)**
- Manages user identities and credentials
- Provides authentication services
- Examples: Azure AD, Google Workspace, Okta

**4. Device Identity and Posture Assessment**
- Validates device identity
- Assesses security posture (OS version, patches, malware presence)
- Continuous monitoring of device state

**5. Industry Compliance**
- Integration with compliance frameworks
- Audit logging and evidence collection
- Policy mapping to standards (NIST CSF, ISO 27001, SOC2)

### Deployment Models

**1. Device Agent/Gateway Based**
- Software agent on each device
- Enforces policies before network access
- Provides continuous device monitoring

**2. Enclave-Based**
- Micro-segmentation of resources
- Access control at resource boundaries
- Minimal trust zones

**3. Resource Portal-Based**
- Single access point (portal) for all resources
- Identity-aware proxy pattern
- Examples: Google BeyondCorp, Azure AD Application Proxy

**4. Hybrid ZTA**
- Combines multiple deployment models
- Gradual migration from perimeter security
- Supports legacy systems during transition

---

## Seven Zero Trust Tenets

NIST SP 800-207 defines seven core tenets that form the foundation of Zero Trust Architecture. These tenets guide implementation decisions and security policy design.

### Tenet 1: All Data Sources and Computing Services Are Resources

**Principle**: Treat all assets as resources requiring protection, regardless of location.

**Explanation**:
- No distinction between "internal" and "external" resources
- Cloud services, on-premises servers, SaaS applications all treated equally
- Data wherever it resides (at rest, in transit, in use) requires protection
- Compute resources (VMs, containers, serverless) are resources

**Implementation Considerations**:
- Comprehensive asset inventory across all environments
- Classification of data sensitivity levels
- Tagging and labeling of all resources
- Centralized identity and access management

**Example Policies**:
```
POLICY: All databases require authenticated access
CONDITION: Database location (cloud/on-prem) irrelevant
ENFORCEMENT: Same authentication/authorization regardless of network

POLICY: API endpoints are resources requiring protection
CONDITION: Internal APIs and external APIs treated equally
ENFORCEMENT: JWT tokens, OAuth 2.0, API keys with expiration
```

**ZeroTrust IAM Analyzer Implementation**:
- [+] Scan identifies all IAM policies across Azure, GCP, Workspace
- [+] No differentiation between cloud providers in security assessment
- [+] Recommendations apply consistently regardless of resource location

**Assessment Criteria**:
- Resource inventory completeness (100% coverage expected)
- Classification accuracy (data sensitivity labels)
- Access controls apply to all resources uniformly
- No exceptions for "internal" systems

**Common Violations**:
- [!] Internal APIs without authentication ("it's internal, so it's safe")
- [!] Development/staging environments with weaker security
- [!] Administrative interfaces accessible without MFA
- [!] Legacy systems excluded from access controls

---

### Tenet 2: All Communication Is Secured Regardless of Network Location

**Principle**: Encrypt and authenticate all network traffic, treating all networks as untrusted.

**Explanation**:
- TLS/SSL for all connections (no plaintext HTTP)
- Mutual TLS (mTLS) for service-to-service communication
- VPNs and secure tunnels do not replace encryption
- Network location provides no security benefit

**Implementation Considerations**:
- TLS 1.3 as minimum standard (deprecated: TLS 1.0, 1.1)
- Certificate management and rotation
- End-to-end encryption for sensitive data
- Service mesh for microservices (Istio, Linkerd)

**Example Policies**:
```
POLICY: All HTTP traffic redirects to HTTPS
CONDITION: No exceptions for "internal" traffic
ENFORCEMENT: TLS 1.3 with strong cipher suites

POLICY: Service-to-service calls use mTLS
CONDITION: Both client and server authenticate
ENFORCEMENT: Certificate-based authentication with short-lived certs
```

**ZeroTrust IAM Analyzer Implementation**:
- [!] TLS enforcement not yet implemented (0% complete)
- [!] No inspection of in-transit encryption policies
- [FUTURE] Azure Conditional Access policy analysis for encryption requirements
- [FUTURE] GCP VPC Service Controls verification

**Assessment Criteria**:
- TLS usage: 100% of connections encrypted
- Certificate validity: No expired or self-signed certs in production
- Cipher suite strength: Modern ciphers only (no deprecated algorithms)
- mTLS adoption for service mesh: 100% for sensitive services

**Common Violations**:
- [!] HTTP endpoints in production environments
- [!] Weak cipher suites (RC4, 3DES, CBC mode)
- [!] Long-lived certificates (>1 year validity)
- [!] Service accounts with permanent credentials (no rotation)

**Related Technologies**:
- **Azure**: Azure Front Door, Application Gateway with TLS termination
- **GCP**: Cloud Load Balancing with SSL policies, Certificate Manager
- **Service Mesh**: Istio, Linkerd, Consul Connect
- **Secrets Management**: HashiCorp Vault, Azure Key Vault, GCP Secret Manager

---

### Tenet 3: Access to Individual Resources Is Granted on a Per-Session Basis

**Principle**: Authenticate and authorize each session independently, no long-lived access grants.

**Explanation**:
- Short-lived access tokens (15-60 minutes)
- Re-authentication required for high-risk actions
- Session tokens invalidated after activity timeout
- No "remember me" for sensitive operations

**Implementation Considerations**:
- JWT tokens with short expiration (30 minutes standard)
- Refresh tokens with rotation mechanism
- Session invalidation on logout
- Context-aware session management (detect anomalies)

**Example Policies**:
```
POLICY: Access tokens expire after 30 minutes
CONDITION: User must re-authenticate for new session
ENFORCEMENT: Token expiration validated on every request

POLICY: High-risk actions require re-authentication
CONDITION: Actions include: delete data, change permissions, transfer funds
ENFORCEMENT: Step-up authentication (MFA prompt)
```

**ZeroTrust IAM Analyzer Implementation**:
- [+] JWT token infrastructure with 30-minute expiration (core/security.py)
- [+] Session schema defined in User model with session_token field
- [!] Session management logic not implemented (0% complete)
- [!] No token refresh endpoint
- [!] No step-up authentication for high-risk operations

**Assessment Criteria**:
- Token lifetime: <=60 minutes for access tokens
- Refresh token rotation: Every use generates new refresh token
- Session timeout: 15 minutes of inactivity
- Re-authentication for high-risk: Required for privileged operations

**Common Violations**:
- [!] API keys with unlimited lifetime
- [!] Long-lived service account credentials (years)
- [!] No session timeout implementation
- [!] Remember me functionality for admin panels

**Microsoft Entra ID (Azure AD) Features**:
- **Conditional Access**: Session controls (sign-in frequency, persistent browser session)
- **Continuous Access Evaluation (CAE)**: Real-time token revocation
- **Token Lifetime Policies**: Configurable access and refresh token expiration

**Google Cloud IAM Features**:
- **Service Account Short-Lived Tokens**: 1-hour maximum via workload identity
- **VPC Service Controls**: Context-aware access based on network perimeter
- **IAM Conditions**: Time-based and attribute-based access control

---

### Tenet 4: Access to Resources Is Determined by Dynamic Policy

**Principle**: Security policies adapt based on context, not static rules.

**Explanation**:
- Contextual access control: who, what, where, when, how, device state
- Risk-based authentication (adaptive MFA)
- Behavioral analysis (detect anomalies)
- Continuous policy evaluation (not just at login)

**Implementation Considerations**:
- Role-Based Access Control (RBAC) as baseline
- Attribute-Based Access Control (ABAC) for dynamic decisions
- Integration with threat intelligence feeds
- Real-time risk scoring

**Example Policies**:
```
POLICY: Admin access requires managed device + MFA + corporate network
CONDITION:
  - Device: Corporate-managed, compliant (OS patches, no malware)
  - Authentication: MFA with hardware token
  - Network: Corporate IP range or approved VPN
ENFORCEMENT: Any condition failure denies access

POLICY: Unusual login location triggers additional verification
CONDITION: User accessing from country different from last 90 days
ENFORCEMENT: Require additional MFA factor + security question
```

**ZeroTrust IAM Analyzer Implementation**:
- [+] RBAC defined in User model (admin, analyst, viewer, auditor roles)
- [+] has_permission() method for role-based authorization
- [!] Dynamic policy engine not implemented (0% complete)
- [!] No context-aware access decisions
- [!] No integration with threat intelligence
- [!] No behavioral analytics

**Assessment Criteria**:
- Context awareness: Policies consider >=5 factors (user, device, location, time, behavior)
- Dynamic adaptation: Policies automatically adjust based on risk score
- Continuous evaluation: Access re-assessed at regular intervals (not just login)
- ABAC adoption: >=30% of policies use attributes beyond roles

**Common Violations**:
- [!] Static role assignments (never reviewed)
- [!] No device posture checks
- [!] No geolocation or IP reputation checks
- [!] Administrator accounts with permanent privileges

**Microsoft Entra ID Conditional Access Examples**:
```
POLICY: Require MFA for risky sign-ins
CONDITIONS:
  - Sign-in risk: Medium or High (Azure AD Identity Protection)
  - User: All users
GRANTS:
  - Require MFA

POLICY: Block access from unmanaged devices
CONDITIONS:
  - Applications: Office 365
  - Device state: Not compliant or not hybrid Azure AD joined
GRANTS:
  - Block access
```

**GCP IAM Conditions Examples**:
```
POLICY: Allow BigQuery access only during business hours
CONDITION:
  resource.type == "bigquery.googleapis.com/Dataset" &&
  request.time.getHours("America/New_York") >= 9 &&
  request.time.getHours("America/New_York") <= 17
GRANTS:
  - roles/bigquery.dataViewer

POLICY: Restrict service account usage to specific GCE instances
CONDITION:
  resource.name.startsWith("projects/my-project/zones/us-central1-a/instances/prod-")
GRANTS:
  - roles/iam.serviceAccountUser
```

---

### Tenet 5: Organization Monitors and Measures Asset Integrity and Security Posture

**Principle**: Continuous monitoring of all assets with comprehensive security posture assessment.

**Explanation**:
- Real-time asset inventory and discovery
- Continuous vulnerability scanning
- Configuration drift detection
- Security posture scoring

**Implementation Considerations**:
- Asset management system (CMDB)
- Vulnerability management platform
- Configuration management database
- Automated compliance scanning

**Example Monitoring**:
```
ASSET INVENTORY:
  - All users, groups, roles, service accounts
  - All compute resources (VMs, containers, serverless)
  - All data stores (databases, object storage, file shares)
  - All network resources (VPCs, subnets, firewall rules)

SECURITY POSTURE METRICS:
  - OS patch level (% systems current on security patches)
  - Vulnerability count by severity (critical, high, medium, low)
  - Configuration compliance (% systems matching baseline)
  - Security control coverage (% assets with EDR, logging, encryption)
```

**ZeroTrust IAM Analyzer Implementation**:
- [+] Scan model for tracking security assessments
- [+] Zero Trust scoring fields (score, breakdown per tenet)
- [!] Asset inventory not implemented (0% complete)
- [!] No vulnerability scanning integration
- [!] No configuration baseline comparison
- [!] No continuous monitoring (only on-demand scans planned)

**Assessment Criteria**:
- Asset inventory completeness: 100% of resources discovered
- Inventory accuracy: >=95% accuracy verified quarterly
- Vulnerability remediation SLA: Critical <=7 days, High <=30 days
- Configuration drift detection: Real-time alerting on changes

**Common Violations**:
- [!] No asset inventory (unknown what exists)
- [!] Manual vulnerability tracking (spreadsheets)
- [!] No configuration baselines defined
- [!] Shadow IT (unmanaged cloud accounts)

**Azure Security Monitoring**:
- **Microsoft Defender for Cloud**: Continuous security posture assessment
- **Azure Policy**: Configuration compliance monitoring
- **Azure Security Benchmark**: Comprehensive security baseline
- **Azure Sentinel**: SIEM for centralized security monitoring

**GCP Security Monitoring**:
- **Security Command Center**: Asset discovery and vulnerability detection
- **Asset Inventory**: Real-time asset tracking across organization
- **Policy Intelligence**: IAM policy recommendations and insights
- **Cloud Monitoring**: Metrics, logs, and traces for all services

**Google Workspace Security Monitoring**:
- **Security Center**: Centralized security and compliance dashboard
- **Alert Center**: Real-time security alerts and recommendations
- **Audit Logs**: Comprehensive activity tracking
- **Investigation Tool**: Security event investigation and response

---

### Tenet 6: All Resource Authentication and Authorization Are Dynamic and Strictly Enforced

**Principle**: Strong authentication with dynamic authorization decisions, no exceptions.

**Explanation**:
- Multi-factor authentication (MFA) required
- Passwordless authentication preferred (FIDO2, biometrics)
- Least privilege access by default
- Just-in-time (JIT) access for administrative tasks

**Implementation Considerations**:
- MFA enforcement for all users (100% coverage)
- Phishing-resistant MFA preferred (hardware tokens, biometrics)
- Privileged Access Management (PAM) for administrative access
- Regular access reviews and recertification

**Example Policies**:
```
AUTHENTICATION:
  - MFA: Required for all user accounts
  - Method: FIDO2 hardware token (YubiKey, Titan) OR biometric
  - Backup: Time-based One-Time Password (TOTP) app
  - Prohibited: SMS-based MFA (vulnerable to SIM swapping)

AUTHORIZATION:
  - Default: No access (deny by default)
  - Grant: Least privilege (minimum permissions needed)
  - Duration: Time-limited for elevated permissions
  - Review: Quarterly access recertification
```

**ZeroTrust IAM Analyzer Implementation**:
- [+] Password hashing with bcrypt (12 rounds) in core/security.py
- [+] JWT token-based authentication infrastructure
- [+] 2FA schema fields in User model (two_factor_enabled, two_factor_secret)
- [!] 2FA enforcement not implemented (0% complete)
- [!] No MFA enrollment flow
- [!] No passwordless authentication support
- [!] No PAM integration

**Assessment Criteria**:
- MFA enrollment: 100% of users with MFA enabled
- MFA strength: >=80% using phishing-resistant methods (FIDO2, biometric)
- Privileged access: 100% of admin accounts require JIT access
- Access review completion: >=95% quarterly review completion rate

**Common Violations**:
- [!] Optional MFA (user choice to enable)
- [!] SMS-based MFA accepted
- [!] Shared administrative accounts
- [!] Permanent administrator privileges (no JIT)
- [!] No access reviews (users accumulate permissions)

**Microsoft Entra ID Authentication Features**:
- **Azure MFA**: Cloud-based MFA with multiple verification methods
- **Passwordless Authentication**: FIDO2, Microsoft Authenticator, Windows Hello
- **Conditional Access MFA**: Context-aware MFA enforcement
- **Privileged Identity Management (PIM)**: Just-in-time administrative access

**Google Cloud IAM Authentication Features**:
- **Google 2-Step Verification**: TOTP, security keys, Google prompts
- **Security Keys**: FIDO2 hardware token support (Titan Security Key)
- **Context-Aware Access**: Device and location-based access control
- **Workforce Identity Federation**: Workload identity for applications

**Best Practices**:
1. [+] Enforce MFA for all accounts (no exceptions)
2. [+] Prefer hardware security keys over software TOTP
3. [+] Implement JIT access for administrative privileges
4. [+] Rotate service account credentials regularly (90 days)
5. [+] Conduct quarterly access reviews and remove stale permissions
6. [+] Monitor for authentication anomalies (impossible travel, brute force)

---

### Tenet 7: Organization Collects Information About Assets, Network Infrastructure, and Communications

**Principle**: Comprehensive logging, monitoring, and analytics to inform security decisions.

**Explanation**:
- Centralized logging for all security events
- Network traffic analysis and monitoring
- User and entity behavior analytics (UEBA)
- Audit trail for compliance and forensics

**Implementation Considerations**:
- Security Information and Event Management (SIEM)
- Log aggregation and retention (minimum 90 days)
- Real-time alerting on security events
- Threat intelligence integration

**Example Logging Requirements**:
```
AUTHENTICATION LOGS:
  - All login attempts (success and failure)
  - MFA challenges and results
  - Password reset requests
  - Session creation and termination

AUTHORIZATION LOGS:
  - Access grant/deny decisions with context
  - Permission changes (RBAC/ABAC updates)
  - Privileged operations (admin actions)
  - Policy evaluations and outcomes

RESOURCE ACCESS LOGS:
  - Data access (read, write, delete)
  - API calls with request/response
  - Database queries
  - File system operations

NETWORK LOGS:
  - Firewall allow/deny decisions
  - VPN connections
  - DNS queries
  - TLS handshakes
```

**ZeroTrust IAM Analyzer Implementation**:
- [+] Structured logging with structlog (core/logging.py)
- [+] Request logging middleware
- [+] Database audit fields (created_at, updated_at, created_by)
- [+] User activity tracking (last_login_at, last_login_ip)
- [!] Centralized log aggregation not implemented (0% complete)
- [!] No SIEM integration
- [!] No real-time alerting
- [!] No analytics or dashboards for logs

**Assessment Criteria**:
- Log coverage: 100% of security-relevant events logged
- Log retention: Minimum 90 days (1 year for compliance)
- Log analysis: Real-time correlation and alerting
- Incident response: Mean time to detect (MTTD) <=1 hour for critical events

**Common Violations**:
- [!] No centralized logging (logs scattered across systems)
- [!] Insufficient log retention (7-30 days only)
- [!] No log analysis (logs collected but never reviewed)
- [!] Missing critical events (failed authentication not logged)
- [!] No audit trail for administrative actions

**Microsoft Azure Logging**:
- **Azure Monitor Logs**: Centralized log analytics platform
- **Azure Sentinel**: Cloud-native SIEM and SOAR
- **Azure Activity Log**: Subscription-level audit trail
- **Azure AD Audit Logs**: Identity and access audit events
- **Azure AD Sign-in Logs**: Authentication event tracking

**Google Cloud Logging**:
- **Cloud Logging**: Centralized log management (formerly Stackdriver)
- **Cloud Audit Logs**: Admin activity, data access, system events
- **VPC Flow Logs**: Network traffic logging
- **Security Command Center**: Aggregated security findings and insights

**Log Retention Recommendations**:
- **Authentication Events**: 1 year (compliance requirements)
- **Authorization Events**: 1 year (audit trail for access decisions)
- **Data Access Events**: 90 days minimum (1 year for sensitive data)
- **Network Traffic**: 30-90 days (high volume, selective retention)
- **Audit Logs**: 7 years (regulatory requirements for some industries)

**Threat Intelligence Integration**:
- [+] IP reputation services (detect access from known malicious IPs)
- [+] User behavior analytics (detect anomalies in access patterns)
- [+] Threat feeds (correlate events with known attack indicators)
- [+] Automated response (block, alert, or step-up authentication)

---

## OWASP IAM Security Best Practices

### Overview

The Open Web Application Security Project (OWASP) provides comprehensive guidance on Identity and Access Management security. While OWASP is best known for the Top 10 web application vulnerabilities, they also maintain detailed resources for IAM security.

### OWASP Top 10 IAM-Related Vulnerabilities

**A01:2021 - Broken Access Control**
- Violation of least privilege or deny by default
- Bypassing access control checks by modifying URL, state, or API request
- Allowing users to act as other users
- Missing access controls for API endpoints

**Mitigation**:
```
- Implement deny-by-default access control
- Enforce access control checks on every request (server-side)
- Use centralized access control mechanism (avoid duplicating logic)
- Log access control failures and alert administrators
- Rate limit API access to minimize automated attacks
```

**A02:2021 - Cryptographic Failures**
- Transmitting sensitive data in cleartext (HTTP, FTP, SMTP)
- Using weak or deprecated cryptographic algorithms
- Not enforcing encryption (TLS not required)
- Weak key generation or management

**Mitigation**:
```
- Encrypt all data in transit using TLS 1.3
- Encrypt sensitive data at rest using strong algorithms (AES-256)
- Don't cache sensitive data unnecessarily
- Use proper key management (rotate regularly, store securely)
- Hash passwords with adaptive algorithms (bcrypt, Argon2)
```

**A07:2021 - Identification and Authentication Failures**
- Permitting brute force attacks
- Allowing default or weak passwords
- Missing or ineffective multi-factor authentication
- Exposing session identifiers in URLs
- Not invalidating session tokens after logout

**Mitigation**:
```
- Implement multi-factor authentication for all users
- Enforce strong password policies (length, complexity, breached password checking)
- Implement account lockout after failed attempts
- Use server-side secure, random session tokens
- Invalidate tokens after logout and timeout
```

### IAM Security Principles

**1. Principle of Least Privilege**
- Grant minimum permissions necessary for task completion
- Default deny for all access requests
- Time-limited elevated permissions
- Regular access reviews to remove unnecessary permissions

**2. Separation of Duties**
- No single individual has complete control over critical functions
- Divide sensitive operations across multiple people
- Prevent fraud through collusion requirement
- Example: One person approves, another executes financial transactions

**3. Defense in Depth**
- Multiple layers of security controls
- Failure of one control doesn't compromise system
- Authentication + Authorization + Audit + Monitoring
- Network segmentation + Application security + Data encryption

**4. Fail-Safe Defaults**
- Base access decisions on permission (allowlist) rather than exclusion (denylist)
- Default to no access if determination cannot be made
- Explicit grant required for access
- Timeout sessions with no activity

### Password Security

**Password Policy Requirements**:
```
MINIMUM STANDARDS:
- Length: >=12 characters (preferably 16+)
- Complexity: Mix of uppercase, lowercase, numbers, special characters
- No common passwords (check against breached password database)
- No user personal information (name, email, birthdate)
- No password reuse (check last 10 passwords)
- Password expiration: 90 days for privileged accounts (optional for standard users with MFA)

STORAGE:
- Hash with bcrypt, Argon2, or scrypt (NOT MD5, SHA-1, or plain SHA-256)
- Salt: Unique per password, generated using secure random
- Work factor: bcrypt rounds=12 minimum (adjust based on computing power)
```

**Password Reset Security**:
```
PROCESS:
1. User requests password reset
2. System sends time-limited token via email (15-30 minute expiration)
3. Token is single-use (consumed on password reset)
4. New password must differ from old password
5. All active sessions invalidated on password change
6. User notified of password change via email

SECURITY CONTROLS:
- Rate limit password reset requests (3 per hour per account)
- No password hints or security questions (easily guessed)
- Token transmitted via secure channel only (HTTPS, encrypted email)
- Log all password reset attempts
```

### Session Management

**Session Security Requirements**:
```
SESSION CREATION:
- Generate cryptographically strong session tokens (128+ bits entropy)
- Never expose session ID in URL (use HTTP-only cookies)
- Set secure flag on cookies (HTTPS only)
- Set SameSite cookie attribute (CSRF protection)

SESSION LIFECYCLE:
- Absolute timeout: 24 hours (re-authentication required)
- Idle timeout: 15 minutes of inactivity
- Regenerate session ID after authentication
- Invalidate old session ID on logout
- Single concurrent session per user (or limit to N devices)

SESSION STORAGE:
- Store session data server-side (NOT in JWT payload for sensitive data)
- Use Redis or similar for distributed session management
- Encrypt session data at rest
- Implement session fixation protection
```

### API Security

**API Authentication**:
```
METHODS (in order of preference):
1. OAuth 2.0 with short-lived access tokens
2. JWT with signature verification
3. API keys with rate limiting (NOT for user authentication)

REQUIREMENTS:
- All API endpoints require authentication (no anonymous access by default)
- Use HTTPS for all API traffic
- Validate content-type header (prevent CSRF via form submission)
- Rate limit per user/API key
- Version API endpoints (/api/v1, /api/v2)
```

**API Authorization**:
```
CHECKS:
- Verify user has permission for requested operation
- Validate resource ownership (user can only access own data)
- Check RBAC/ABAC policies on every request
- No trust in client-side access control

EXAMPLE:
GET /api/v1/users/123/profile
1. Authenticate request (valid token)
2. Extract user ID from token
3. Verify requesting user is user 123 OR has admin role
4. Deny if neither condition met
```

---

## Multi-Cloud IAM Considerations

### Azure AD (Microsoft Entra ID)

**Overview**:
Microsoft Entra ID (formerly Azure Active Directory) is Microsoft's cloud-based identity and access management service. It provides authentication and authorization for Azure services, Microsoft 365, and third-party SaaS applications.

**Key Features**:

**1. Conditional Access Policies**
- Context-aware access control based on signals
- Signals: user, device, location, application, risk level
- Grant controls: Require MFA, compliant device, approved client app
- Session controls: Sign-in frequency, persistent browser session

**Example Policy**:
```
Policy: Require MFA for administrators
Assignments:
  Users: Directory role = Global Administrator
  Cloud apps: All cloud apps
Conditions:
  Sign-in risk: Not evaluated
  Device platforms: Any
  Locations: Any
Access controls:
  Grant: Grant access, Require MFA
  Session: Not configured
```

**2. Privileged Identity Management (PIM)**
- Just-in-time administrative access
- Time-limited role activation
- Approval workflow for privileged roles
- Audit trail for all privileged operations

**3. Identity Protection**
- Risk-based conditional access
- User risk: Account potentially compromised (leaked credentials, unusual behavior)
- Sign-in risk: Login attempt potentially not from legitimate user
- Automated remediation: Require password change, block access

**4. Application Management**
- Enterprise application registration
- Single sign-on (SSO) configuration
- Application proxy for legacy apps
- Consent and permissions management

**Security Recommendations for Azure AD**:
```
HIGH PRIORITY:
- Enable MFA for all users (100% coverage)
- Configure Conditional Access policies for privileged roles
- Enable Identity Protection risk policies
- Implement PIM for administrative access
- Enable security defaults if Conditional Access not available

MEDIUM PRIORITY:
- Configure named locations (corporate IP ranges)
- Enable sign-in logs and audit logs
- Integrate with Microsoft Sentinel (SIEM)
- Configure access reviews for groups and applications
- Implement app protection policies for mobile devices

ONGOING:
- Review conditional access policies quarterly
- Monitor Identity Protection risk events
- Review privileged role assignments monthly
- Update emergency access (break-glass) procedures
```

### Google Cloud IAM

**Overview**:
Google Cloud IAM provides fine-grained access control for Google Cloud resources. It uses a unified model across all Google Cloud services with centralized policy management.

**Key Concepts**:

**1. IAM Policy Structure**
```
IAM Policy = {
  Bindings: [
    {
      Role: "roles/storage.objectViewer",
      Members: [
        "user:alice@example.com",
        "group:data-analysts@example.com",
        "serviceAccount:app@project.iam.gserviceaccount.com"
      ],
      Condition: "resource.name.startsWith('projects/_/buckets/public/')"
    }
  ],
  AuditConfigs: [...],
  Etag: "BwX..."
}
```

**2. Predefined Roles**
- Primitive roles: Owner, Editor, Viewer (overly broad, avoid in production)
- Predefined roles: Curated by Google for specific services
- Custom roles: Organization-defined roles with specific permissions

**Example Roles**:
```
roles/storage.objectViewer - Read access to GCS objects
roles/compute.instanceAdmin - Manage Compute Engine instances
roles/bigquery.dataEditor - Edit BigQuery datasets and tables
roles/iam.serviceAccountUser - Impersonate service accounts
```

**3. IAM Conditions**
- Time-based access: Restrict access to business hours
- Resource-based access: Limit access to specific resources
- Attribute-based access: Grant based on resource attributes

**Example Condition**:
```
CONDITION:
  Title: "Only during business hours"
  Expression: |
    request.time.getHours("America/New_York") >= 9 &&
    request.time.getHours("America/New_York") <= 17 &&
    request.time.getDayOfWeek("America/New_York") >= 1 &&
    request.time.getDayOfWeek("America/New_York") <= 5
```

**4. Service Accounts**
- Identity for applications and workloads
- Short-lived credentials via Workload Identity Federation
- Key rotation and management
- Impersonation for privilege escalation control

**Security Recommendations for GCP IAM**:
```
HIGH PRIORITY:
- Avoid primitive roles (Owner, Editor, Viewer)
- Use predefined roles or custom roles with least privilege
- Enable Workload Identity for GKE (no service account keys)
- Implement service account key rotation (90 days)
- Use IAM Conditions for time-based access

MEDIUM PRIORITY:
- Enable Organization Policy constraints
- Configure VPC Service Controls for data perimeter
- Implement IAM Policy Analyzer recommendations
- Use separate service accounts per workload
- Enable audit logging for all services

ONGOING:
- Review IAM bindings quarterly
- Monitor IAM policy changes via Cloud Audit Logs
- Use Policy Intelligence Recommender for least privilege
- Validate service account usage and remove unused accounts
```

### Google Workspace (formerly G Suite)

**Overview**:
Google Workspace provides identity and access management for collaboration services (Gmail, Drive, Calendar, Meet). It integrates with Google Cloud IAM for unified identity across consumer and cloud services.

**Key Features**:

**1. Admin Roles and Privileges**
- Super Admin: Full administrative control
- User Management Admin: Create/delete users, reset passwords
- Groups Admin: Manage Google Groups
- Service-specific admins: Gmail, Drive, Calendar admins

**2. Security Settings**:
```
AUTHENTICATION:
- 2-Step Verification enforcement (per organizational unit)
- Security keys requirement (FIDO2)
- Password policy: Length, complexity, reuse, expiration
- Session length control

ACCESS CONTROL:
- Context-Aware Access: Device trust, location, identity
- OAuth app access control: Allowlist/blocklist third-party apps
- API access controls: Enable/disable specific APIs
- Drive sharing settings: Internal only, external domains

DATA PROTECTION:
- Data Loss Prevention (DLP) rules
- Encryption at rest and in transit
- Vault: eDiscovery, retention, holds
- Mobile device management (MDM)
```

**3. Audit and Investigation**:
- Admin audit log: Administrative actions
- Login audit: Authentication events
- Drive audit: File access and sharing
- Security investigation tool: Query logs for security events

**Security Recommendations for Google Workspace**:
```
HIGH PRIORITY:
- Enforce 2-Step Verification for all users
- Require security keys for administrators
- Configure Context-Aware Access rules
- Enable less secure app blocking
- Implement organizational units for policy inheritance

MEDIUM PRIORITY:
- Configure OAuth app access controls (allowlist trusted apps)
- Enable DLP rules for sensitive data (SSN, credit cards)
- Set up alerts for suspicious activity
- Configure mobile device management
- Implement external sharing restrictions

ONGOING:
- Review admin role assignments monthly
- Audit third-party app access quarterly
- Monitor security investigation tool for threats
- Review Drive external sharing weekly
- Update Context-Aware Access policies as needed
```

### Multi-Cloud Consistency Challenges

**Identity Federation**:
- Single source of truth for identity (Azure AD, Okta, Google Workspace)
- SAML/OIDC federation to other cloud providers
- Consistent MFA enforcement across all clouds
- Unified user lifecycle management (joiner/mover/leaver)

**Policy Standardization**:
- Equivalent policies expressed differently per cloud
- Azure Conditional Access vs GCP Organization Policies vs AWS SCPs
- Centralized policy management tools (HashiCorp Sentinel, CloudHealth)
- Policy-as-code (Terraform, Pulumi) for consistency

**Audit and Compliance**:
- Unified SIEM for multi-cloud logs (Splunk, Sentinel, Chronicle)
- Consistent log retention policies
- Cross-cloud correlation for security events
- Compliance mapping (NIST, ISO, SOC2) across all clouds

---

## Industry Standards and Compliance Frameworks

### ISO/IEC 27001:2022

**Overview**:
International standard for Information Security Management Systems (ISMS). Provides requirements for establishing, implementing, maintaining, and continually improving information security.

**Key IAM Requirements**:

**A.9: Access Control**
- A.9.1 Business requirements for access control
- A.9.2 User access management (joiner/mover/leaver)
- A.9.3 User responsibilities (acceptable use policy)
- A.9.4 System and application access control

**Implementation Guidance**:
```
ACCESS CONTROL POLICY:
- Define roles and responsibilities for granting/revoking access
- Implement formal access provisioning process
- Regular access reviews and recertification
- Remove access immediately upon termination

USER ACCESS MANAGEMENT:
- Unique user identification for all users
- Privileged access management and monitoring
- Password management system (complexity, expiration, history)
- Multi-factor authentication for remote and privileged access

ACCESS RIGHTS REVIEW:
- Review frequency: Quarterly for privileged, annually for standard
- Review scope: All user accounts, service accounts, access rights
- Approval: Manager and IT security
- Documentation: Maintain audit trail of reviews and approvals
```

### SOC 2 (Service Organization Control)

**Overview**:
Auditing standard for service organizations, focusing on controls related to security, availability, processing integrity, confidentiality, and privacy.

**Trust Services Criteria - Security**:

**CC6.1: Logical and Physical Access Controls**
- Organization implements logical access security measures to protect against threats from sources outside its system boundaries
- Organization implements controls to prevent or detect unauthorized access

**Implementation**:
```
LOGICAL ACCESS CONTROLS:
- Multi-factor authentication for all users
- Network segmentation and firewall rules
- Encryption of data in transit and at rest
- Intrusion detection and prevention systems

IDENTITY AND ACCESS MANAGEMENT:
- Centralized authentication system
- Role-based access control implementation
- Automated provisioning and deprovisioning
- Periodic access reviews and recertification
- Privileged access management for administrators

MONITORING AND LOGGING:
- Centralized logging for all authentication and authorization events
- Real-time alerting on suspicious activity
- Log retention for minimum 90 days
- Regular review of access logs
```

**CC6.2: Prior to Issuing System Credentials and Granting System Access**
- User identification and authentication
- Authorization and access rights management

### GDPR (General Data Protection Regulation)

**Overview**:
European Union regulation on data protection and privacy. Requires organizations to implement appropriate technical and organizational measures to protect personal data.

**IAM-Relevant Requirements**:

**Article 32: Security of Processing**
```
REQUIREMENTS:
- Pseudonymization and encryption of personal data
- Ability to ensure ongoing confidentiality, integrity, availability
- Ability to restore availability and access to data in a timely manner
- Regular testing and assessment of security measures

IAM IMPLEMENTATION:
- Access controls based on need-to-know principle
- Encryption of personal data at rest and in transit
- Audit logging for all access to personal data
- Regular access reviews and removal of stale permissions
- Data breach detection and notification procedures
```

**Article 25: Data Protection by Design and by Default**
- Implement appropriate technical and organizational measures to ensure only necessary personal data is processed
- Default settings should ensure highest privacy protection

**IAM Implementation**:
```
PRIVACY BY DESIGN:
- Collect minimum personal data necessary (data minimization)
- Limit access to personal data (need-to-know)
- Implement purpose limitation (access for specific purpose only)
- Delete personal data when no longer needed (right to erasure)

PRIVACY BY DEFAULT:
- Deny-by-default access control
- Explicit consent required for data processing
- Minimal data exposure in user interfaces
- Automated data retention and deletion
```

### NIST Cybersecurity Framework (CSF)

**Overview**:
Framework for improving critical infrastructure cybersecurity. Consists of five functions: Identify, Protect, Detect, Respond, Recover.

**IAM Mapping**:

**IDENTIFY (ID)**
- ID.AM: Asset Management - Inventory of all systems and assets
- ID.GV: Governance - IAM policies and procedures documented

**PROTECT (PR)**
- PR.AC: Access Control - Implement identity and access management
- PR.AC-1: Identities and credentials managed for authorized devices and users
- PR.AC-3: Remote access managed
- PR.AC-4: Access permissions and authorizations managed (least privilege)
- PR.AC-6: Identities are proofed and bound to credentials
- PR.AC-7: Users, devices, and other assets are authenticated (MFA)

**DETECT (DE)**
- DE.CM: Continuous Monitoring - Monitor IAM for unauthorized access
- DE.AE: Anomalies and Events - Detect anomalous authentication patterns

**RESPOND (RS) & RECOVER (RC)**
- RS.AN: Analysis - Investigate IAM security incidents
- RC.RP: Recovery Planning - Restore IAM services after incident

---

## Zero Trust Implementation Patterns

### Pattern 1: Identity-Aware Proxy (IAP)

**Description**: Single entry point for all application access with strong authentication and context-aware authorization.

**Architecture**:
```
USER → IDENTITY PROVIDER (AuthN) → IAP (AuthZ) → BACKEND APPLICATION

FLOW:
1. User attempts to access application
2. IAP redirects to IdP for authentication
3. User authenticates with MFA
4. IdP returns identity token to IAP
5. IAP evaluates authorization policy (user, device, location, risk)
6. IAP grants/denies access and proxies request to backend
7. Backend application trusts IAP identity headers (no additional auth)
```

**Implementation Examples**:
- **Google BeyondCorp**: IAP for GCP and on-premises apps
- **Azure AD Application Proxy**: IAP for on-premises apps with Azure AD auth
- **Cloudflare Access**: IAP for any application with multiple IdP support

**Benefits**:
- [+] Centralized authentication and authorization enforcement
- [+] Backend applications don't need authentication logic
- [+] Context-aware access decisions (device trust, location)
- [+] Simplified user experience (single sign-on)

**Challenges**:
- [!] Single point of failure (high availability required)
- [!] Performance overhead (additional network hop)
- [!] Complex initial setup and policy configuration

### Pattern 2: Service Mesh with mTLS

**Description**: Microservices architecture with mutual TLS authentication and authorization for all service-to-service communication.

**Architecture**:
```
SERVICE A → SIDECAR PROXY A → mTLS → SIDECAR PROXY B → SERVICE B

FEATURES:
- Every service has a sidecar proxy (Envoy)
- Proxies handle TLS termination and mutual authentication
- Service identity via short-lived certificates (Workload Identity)
- Authorization policies enforce which services can communicate
- Traffic encryption and authentication transparent to applications
```

**Implementation Examples**:
- **Istio**: Full-featured service mesh for Kubernetes
- **Linkerd**: Lightweight service mesh focused on simplicity
- **Consul Connect**: Service mesh from HashiCorp

**Benefits**:
- [+] Zero-trust networking (no implicit trust between services)
- [+] End-to-end encryption for all service communication
- [+] Fine-grained authorization (service-to-service policies)
- [+] Observability (distributed tracing, metrics)

**Challenges**:
- [!] Complexity of service mesh operations
- [!] Performance overhead from sidecar proxies
- [!] Learning curve for teams unfamiliar with service mesh concepts

### Pattern 3: Software-Defined Perimeter (SDP)

**Description**: Network infrastructure that dynamically creates one-to-one connections between requesting devices and resources after authentication and authorization.

**Architecture**:
```
COMPONENTS:
- SDP Controller: Central authentication and policy enforcement
- SDP Gateways: Enforce access policies and provide secure tunnels
- SDP Clients: Software agents on user devices

FLOW:
1. Client authenticates to SDP Controller (MFA)
2. Controller evaluates policy and determines accessible resources
3. Controller provisions one-time connection between client and gateway
4. Gateway creates encrypted tunnel to specific resource
5. All other resources remain invisible to client (network cloaking)
```

**Implementation Examples**:
- **Cisco Duo Network Gateway**: SDP with Duo authentication
- **Palo Alto Prisma Access**: Cloud-delivered SDP with CASB
- **Zscaler Private Access**: SDP for private application access

**Benefits**:
- [+] Resources invisible until after authentication (reduces attack surface)
- [+] No VPN (better user experience, better security)
- [+] Granular access control per user and device
- [+] Scalable for cloud and hybrid environments

**Challenges**:
- [!] Requires client software installation
- [!] May not support legacy protocols
- [!] Vendor lock-in potential

### Pattern 4: Workload Identity Federation

**Description**: Applications authenticate using workload identities rather than long-lived credentials. Cloud providers issue short-lived tokens based on platform identity (Kubernetes service account, cloud instance identity).

**Architecture**:
```
KUBERNETES POD → WORKLOAD IDENTITY → GCP IAM

FLOW:
1. Pod has Kubernetes service account
2. Kubernetes service account mapped to GCP service account
3. Application requests token from GCP metadata server
4. GCP validates Kubernetes token and issues short-lived access token
5. Application uses access token for GCP API calls
6. Token expires after 1 hour (no key rotation needed)
```

**Implementation Examples**:
- **GCP Workload Identity**: Kubernetes service accounts map to GCP service accounts
- **Azure AD Workload Identity**: Similar pattern for Azure Kubernetes Service
- **AWS IAM Roles for Service Accounts (IRSA)**: EKS pods assume IAM roles

**Benefits**:
- [+] No long-lived credentials (service account keys)
- [+] Automatic credential rotation
- [+] Least privilege (fine-grained IAM bindings per workload)
- [+] Simplified key management (no keys to manage)

**Challenges**:
- [!] Requires Kubernetes or cloud-native platform
- [!] Legacy applications may not support token-based auth
- [!] Initial setup complexity

---

## Zero Trust Maturity Models

### CISA Zero Trust Maturity Model

**Overview**:
The Cybersecurity and Infrastructure Security Agency (CISA) published a Zero Trust Maturity Model to help organizations assess their progress in implementing Zero Trust Architecture.

**Maturity Levels**:

**Level 0 - Traditional**
- Perimeter-based security model
- Implicit trust for internal network traffic
- Minimal visibility into security posture
- Reactive security approach

**Level 1 - Initial**
- Pilot Zero Trust projects initiated
- Basic identity and access management
- Some network segmentation implemented
- Beginning to collect security data

**Level 2 - Advanced**
- Zero Trust policies defined and documented
- Automated identity and access management
- Micro-segmentation of network
- Comprehensive logging and monitoring

**Level 3 - Optimal**
- Fully automated and dynamic Zero Trust
- AI/ML-driven security analytics
- Real-time threat detection and response
- Continuous optimization and improvement

### Identity Maturity Assessment

**Level 1 - Ad Hoc**:
```
CHARACTERISTICS:
- No centralized identity management
- Passwords are primary authentication method
- No MFA or inconsistent MFA adoption
- Manual user provisioning and deprovisioning
- No access reviews
- Shared administrator accounts

SCORE: 0-25 / 100
```

**Level 2 - Managed**:
```
CHARACTERISTICS:
- Centralized identity provider (Azure AD, Okta)
- MFA enabled for some users (>50%)
- Automated provisioning for primary applications
- Annual access reviews
- Separate administrator accounts
- Basic role-based access control

SCORE: 26-50 / 100
```

**Level 3 - Defined**:
```
CHARACTERISTICS:
- Single identity provider for all applications (SSO)
- MFA required for all users (100%)
- Fully automated provisioning/deprovisioning
- Quarterly access reviews
- Privileged access management implemented
- Comprehensive RBAC with least privilege
- Passwordless authentication pilot

SCORE: 51-75 / 100
```

**Level 4 - Optimized**:
```
CHARACTERISTICS:
- Passwordless authentication for all users
- Risk-based conditional access
- Just-in-time access for privileged operations
- Continuous access evaluation
- Automated access reviews with ML recommendations
- Zero standing privileges
- Comprehensive behavioral analytics

SCORE: 76-100 / 100
```

### ZeroTrust IAM Analyzer Maturity Mapping

**Current State** (based on project analysis):
```
OVERALL MATURITY: Level 1 - Initial (10-15%)

SCORING BREAKDOWN:
1. All data sources are resources: 15% (models defined, not enforced)
2. Communication secured: 0% (no TLS enforcement)
3. Per-session access: 20% (JWT defined, session mgmt missing)
4. Dynamic policy: 0% (RBAC defined, not dynamic)
5. Asset monitoring: 0% (scan models exist, no monitoring)
6. Dynamic authentication: 10% (auth infra exists, no MFA)
7. Information collection: 5% (logging defined, no SIEM)

AVERAGE: 7.1% → Level 1 - Initial
```

**Target State** (MVP):
```
TARGET MATURITY: Level 2 - Managed (40-50%)

SCORING TARGETS:
1. All data sources are resources: 50% (Azure-only, basic resource inventory)
2. Communication secured: 30% (HTTPS enforced, no mTLS)
3. Per-session access: 60% (JWT with refresh, session timeouts)
4. Dynamic policy: 40% (RBAC enforced, basic conditional access)
5. Asset monitoring: 50% (Azure AD policy scanning, basic posture)
6. Dynamic authentication: 50% (MFA enrollment flow, no passwordless)
7. Information collection: 40% (centralized logging, basic dashboards)

AVERAGE: 45.7% → Level 2 - Managed
```

---

## Conclusion

Zero Trust Architecture represents a paradigm shift from perimeter-based security to continuous verification and context-aware access control. Successful implementation requires:

**1. Comprehensive Understanding**
- Deep knowledge of NIST SP 800-207 seven tenets
- Familiarity with cloud provider IAM services (Azure AD, GCP IAM, Workspace)
- Awareness of industry compliance requirements (ISO 27001, SOC 2, GDPR)

**2. Phased Implementation**
- Start with identity and access management foundation
- Implement MFA and strong authentication universally
- Add context-aware policies incrementally
- Continuous monitoring and improvement

**3. Cultural Transformation**
- Zero Trust is not just technology, it's a mindset
- Requires organizational buy-in and training
- Challenge assumptions about "trusted" networks
- Embrace continuous verification over implicit trust

**4. Measurement and Assessment**
- Use maturity models to track progress
- Regular security posture assessments
- Quantitative metrics (MFA adoption %, session lifetime, policy coverage)
- Continuous optimization based on threat intelligence

---

**Document Version**: 1.0
**Last Updated**: October 24, 2025
**Next Review**: Upon MVP completion

**References**:
- [NIST SP 800-207 Zero Trust Architecture](https://doi.org/10.6028/NIST.SP.800-207)
- [OWASP Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/)
- [Microsoft Zero Trust Guidance](https://www.microsoft.com/security/business/zero-trust)
- [Google BeyondCorp Whitepaper](https://cloud.google.com/beyondcorp)
- [CISA Zero Trust Maturity Model](https://www.cisa.gov/zero-trust-maturity-model)
