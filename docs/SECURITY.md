# Security

## Overview

ZeroTrust IAM Analyzer takes security seriously. This document outlines CIEM-specific threats, attack scenarios, and security best practices.

## CIEM-Specific Security Threats

### 1. Entitlement Manipulation Attacks

**Threat**: Attackers modify entitlements to grant themselves elevated permissions

**Attack Scenarios:**
- Permission injection via iam.roles.update
- Policy binding tampering
- Service account impersonation
- Cross-project access escalation

**Mitigations:**
- Continuous monitoring of IAM policy changes
- Multi-party approval for privilege changes
- Organization Policy Constraints

### 2. CIEM Platform Compromise

**Threat**: Attackers compromise the CIEM platform to hide malicious activity

**Attack Scenarios:**
- Log deletion to remove evidence
- Risk score manipulation
- Alert suppression
- Hidden backdoor creation

**Mitigations:**
- Isolated, hardened deployment
- Immutable audit logs
- Separate integrity monitoring
- MFA and JIT access for admin functions

### 3. Credential Theft and Abuse

**Threat**: Stolen credentials used to enumerate entitlements

**Attack Scenarios:**
- Service account key exfiltration
- OAuth token theft
- Workload identity misconfiguration
- Session hijacking

**Mitigations:**
- Short-lived tokens over long-lived keys
- Workload Identity Federation
- Enforce MFA
- Monitor anomalous API usage
- Regular credential rotation

### 4. Privilege Escalation Paths

**Common Escalation Paths:**

**Path 1: Service Account Impersonation**
- Initial: roles/iam.serviceAccountUser
- Escalate: Create key for admin service account
- Result: Full admin access

**Path 2: IAM Role Modification**
- Initial: roles/iam.roleAdmin
- Escalate: Modify role to add sensitive permissions
- Result: Indirect privilege escalation

**Path 3: Compute Instance Launch**
- Initial: compute.instances.create + iam.serviceAccounts.actAs
- Escalate: Launch VM with privileged service account
- Result: Code execution with elevated permissions

**Mitigations:**
- Detect escalation paths with CIEM analysis
- Organization Policy Constraints
- Separation of duties
- Monitor resource creation patterns

### 5. Permission Creep and Standing Privileges

**Threat**: Excessive permissions accumulate over time

**Attack Scenarios:**
- Temporary access never revoked
- Role accumulation across projects
- Orphaned service accounts
- Group membership drift

**Mitigations:**
- 90-day permission expiration
- Quarterly access reviews
- Monitor dormant accounts
- Just-in-time (JIT) access

### 6. Multi-Cloud Attack Surface

**Threat**: Attackers pivot between cloud providers

**Attack Scenarios:**
- Cross-cloud lateral movement
- Identity provider compromise
- Inconsistent security policies
- Shadow cloud resources

**Mitigations:**
- Unified CIEM visibility
- Consistent least-privilege policies
- Monitor cross-cloud usage
- Strong federation trust policies

## Entitlement Attack Scenarios

### Scenario 1: Developer Account Compromise

**Initial Access**: Phished developer credentials

**Privilege Escalation**:
1. Developer has iam.serviceAccountUser on admin account
2. Attacker creates service account key
3. Gains full GCP admin access

**Impact**: Full cloud control, data exfiltration

**Detection**:
- Alert on service account key creation
- Detect anomalous API calls
- CIEM flags escalation path

### Scenario 2: CI/CD Pipeline Compromise

**Initial Access**: Compromised GitHub Actions

**Lateral Movement**:
1. CI/CD service account has roles/editor
2. Access production databases
3. Exfiltrate customer data
4. Deploy backdoor functions

**Impact**: Data breach, regulatory fines

**Detection**:
- CIEM flags 98% unused permissions
- Alert on unusual access patterns
- Detect suspicious function deployments

### Scenario 3: Third-Party Vendor Compromise

**Initial Access**: Compromised vendor with GCP access

**Privilege Escalation**:
1. Vendor has iam.serviceAccounts.actAs
2. Impersonate deployment account
3. Gain roles/editor across production

**Impact**: Production compromise via trusted vendor

**Detection**:
- CIEM identifies escalation path
- Alert on non-billing access
- Detect unusual impersonation

## Security Best Practices

### 1. Least-Privilege Enforcement
- Grant only required permissions
- Create custom roles with minimal permissions
- Implement JIT access
- Regular access reviews

### 2. Continuous Monitoring
- Enable Cloud Audit Logs
- Real-time alerts for privilege escalation
- Monitor dormant accounts
- Track permission usage patterns

### 3. Defense in Depth
- Organization Policy Constraints
- VPC Service Controls
- Multi-factor authentication
- Separate prod/dev environments

### 4. Zero Trust Architecture
- Workload Identity Federation
- Short-lived tokens
- Context-aware access controls
- Continuous verification

## Reporting Security Vulnerabilities

Email: security@zerotrust-iam-analyzer.com

**Response Timeline:**
- Initial response: 24 hours
- Assessment: 72 hours
- Remediation: Critical (7 days), High (30 days)

## Compliance

Supports: SOC 2, ISO 27001, PCI-DSS, GDPR, HIPAA

## Security Hardening Checklist

### Deployment
- [ ] Isolated GCP project
- [ ] VPC Service Controls
- [ ] Organization Policy Constraints
- [ ] Workload Identity Federation
- [ ] Cloud Armor DDoS protection

### Access Controls
- [ ] Enforce MFA
- [ ] JIT admin access
- [ ] Separate service accounts
- [ ] Read-only default access
- [ ] Approval workflows

### Monitoring
- [ ] Cloud Audit Logs (Admin, Data, System)
- [ ] Real-time IAM change alerts
- [ ] SIEM log export
- [ ] Platform health monitoring
- [ ] Anomaly detection

### Data Protection
- [ ] Encryption at rest (CMEK/CSEK)
- [ ] TLS 1.3 in transit
- [ ] Data retention policies
- [ ] Backup and disaster recovery
- [ ] Incident response procedures

## Incident Response

### CIEM Platform Compromise
1. Contain: Isolate platform, revoke credentials
2. Investigate: Review audit logs
3. Eradicate: Remove attacker access
4. Recover: Restore from backup
5. Lessons Learned: Update controls

### Privilege Escalation
1. Verify escalation path
2. Assess impact
3. Remediate permissions
4. Monitor for exploitation
5. Document incident

## Conclusion

Security is a shared responsibility. Use ZeroTrust IAM Analyzer CIEM capabilities to reduce entitlement risks and prevent identity-based attacks.
