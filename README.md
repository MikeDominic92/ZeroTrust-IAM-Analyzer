# ZeroTrust IAM Analyzer
## A Cloud Infrastructure Entitlement Management (CIEM) Platform

A comprehensive security analysis tool for evaluating identity and access management policies across multi-cloud environments.

## Overview

ZeroTrust IAM Analyzer is a Cloud Infrastructure Entitlement Management (CIEM) platform that analyzes Google Cloud IAM policies and Google Workspace identity configurations to provide actionable security recommendations based on Zero Trust principles. The tool delivers security scoring, policy analysis, entitlement risk assessment, and automated remediation guidance through an intuitive web interface.

### What is CIEM?

Cloud Infrastructure Entitlement Management (CIEM) is a security discipline focused on managing and governing identities and their entitlements across cloud infrastructure. CIEM solutions help organizations:

- **Discover** all identities across multi-cloud environments (human and machine)
- **Analyze** permissions and entitlements to identify excessive access
- **Detect** entitlement risks like privilege escalation paths and permission creep
- **Remediate** security gaps through least-privilege recommendations
- **Monitor** for policy drift and unauthorized entitlement changes

CIEM is recognized by Gartner as a critical component of cloud security, addressing the challenge that **99% of cloud permissions granted are never used** (Gartner, 2024), creating massive attack surfaces and compliance risks.

## CIEM Capabilities

ZeroTrust IAM Analyzer provides comprehensive CIEM functionality:

### Excessive Permissions Detection
- Identifies overprivileged identities with unused permissions
- Analyzes service accounts, user accounts, and workload identities
- Detects broad wildcard permissions and administrative access
- Highlights dormant accounts with standing privileges

### Least-Privilege Scoring
- Calculates risk scores for every identity (0-100 scale)
- Evaluates permission usage patterns and access frequency
- Compares granted permissions against actual resource usage
- Recommends right-sized permissions based on activity analysis

### Entitlement Risk Analysis
- Maps privilege escalation paths across resources
- Identifies permission creep and role accumulation over time
- Detects dangerous permission combinations
- Analyzes cross-project and cross-organization access

### Cross-Cloud Visibility (Roadmap)
- Currently: Google Cloud Platform and Google Workspace
- Planned: AWS IAM Access Analyzer integration
- Planned: Azure Entra ID and Azure RBAC support
- Planned: Multi-cloud unified entitlement dashboard

### Identity-to-Resource Mapping
- Visual representation of who can access what
- Resource-centric and identity-centric access views
- Entitlement dependency analysis
- Impact assessment for permission changes

## CIEM vs Traditional IAM

| Traditional IAM | CIEM (ZeroTrust IAM Analyzer) |
|----------------|-------------------------------|
| Manages user identities and authentication | Manages entitlements and permissions across all identity types |
| Focuses on who you are | Focuses on what you can do |
| Static role assignments | Dynamic risk-based permission analysis |
| Manual access reviews | Automated entitlement discovery and analysis |
| Point-in-time compliance checks | Continuous monitoring and drift detection |
| Reactive permission cleanup | Proactive least-privilege recommendations |
| Single cloud visibility | Cross-cloud entitlement management |

CIEM complements traditional IAM by providing the visibility and governance layer needed to enforce Zero Trust principles at scale.

## Key Features

- Security analysis for Google Cloud IAM and Google Workspace
- Zero Trust security scoring (0-100 scale)
- Excessive permissions detection and least-privilege recommendations
- Entitlement risk analysis and privilege escalation path detection
- Identity-to-resource mapping and access visualization
- Actionable remediation recommendations
- Interactive dashboard with real-time visualizations
- Policy drift detection and monitoring
- Automated security scanning with alerting
- Export capabilities for security reports

## Architecture

The application consists of three main components:

1. **Frontend**: React TypeScript application with Material-UI components
2. **Backend**: FastAPI Python application with PostgreSQL database
3. **Infrastructure**: Google Cloud Platform services (Cloud Run, Cloud SQL, Memorystore)

The system integrates with external APIs including Google Cloud IAM API, and Google Workspace Admin SDK to collect and analyze security policies.

## Quick Start

### Prerequisites

- Google Cloud SDK (gcloud)
- Docker and Docker Compose
- Python 3.11 or higher
- Node.js 20 or higher
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/zerotrust-iam-analyzer.git
cd zerotrust-iam-analyzer
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Start with Docker Compose:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Development Setup

For local development without Docker:

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# GCP Configuration
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=us-central1


# Database Configuration
DATABASE_URL=postgresql://iam_user:password@localhost:5432/iam_analyzer

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Application Configuration
SECRET_KEY=your-jwt-secret-key
DEBUG=true
ENVIRONMENT=development
```

### Required API Permissions


**Google Cloud:**
- iam.roles.list
- iam.serviceAccounts.list
- resourcemanager.projects.getIamPolicy
- cloudidentity.groups.list

**Google Workspace:**
- admin.directory.user.readonly
- admin.directory.group.readonly
- admin.directory.device.readonly

## Deployment

### Google Cloud Platform Deployment

1. Set up GCP project:
```bash
./scripts/setup/gcp-setup.sh
```

2. Deploy backend:
```bash
./scripts/deployment/deploy-backend.sh
```

3. Deploy frontend:
```bash
./scripts/deployment/deploy-frontend.sh
```

4. Configure secrets:
```bash
./scripts/deployment/setup-secrets.sh
```

### Manual Deployment

1. Create GCP project and enable APIs:
```bash
gcloud projects create zerotrust-iam-analyzer
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
```

2. Build and deploy containers:
```bash
# Backend
cd backend
gcloud builds submit --tag gcr.io/PROJECT_ID/iam-analyzer-backend
gcloud run deploy iam-analyzer-backend --image gcr.io/PROJECT_ID/iam-analyzer-backend

# Frontend
cd frontend
gcloud builds submit --tag gcr.io/PROJECT_ID/iam-analyzer-frontend
gcloud run deploy iam-analyzer-frontend --image gcr.io/PROJECT_ID/iam-analyzer-frontend
```

## Usage

### Getting Started

1. Configure your API credentials in the environment variables
2. Run your first comprehensive security analysis
3. Review the dashboard for security scores and recommendations

### Dashboard Features

- **Overview**: Security posture summary with key metrics
- **Policy Analysis**: Detailed breakdown of IAM policies and risk scores
- **Trends**: Historical security data and improvement tracking
- **Recommendations**: Actionable security improvements with implementation steps

### API Examples

Get security overview:
```bash
curl http://localhost:8000/api/v1/dashboard/overview
```

Analyze policies:
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"sources": ["gcp", "workspace"]}'
```

Get recommendations:
```bash
curl http://localhost:8000/api/v1/recommendations?severity=high
```

## Testing

### Backend Tests
```bash
cd backend
pytest --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:e2e
```

### Full Test Suite
```bash
./scripts/development/test-all.sh
```

## Monitoring

The application includes comprehensive monitoring for:

- API response times and error rates
- User authentication and activity patterns
- Security events and policy changes
- System performance and resource usage

View logs with:
```bash
gcloud logs read "resource.type=cloud_run_revision" --limit 50
```

## Security

### Data Protection

- All data encrypted at rest and in transit
- OAuth 2.0 authentication with JWT tokens
- Role-based access control
- Complete audit trail for compliance

### Security Best Practices

- Principle of least privilege for all access
- Regular security reviews and access audits
- Automated threat detection and monitoring
- Secure development following OWASP guidelines

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please follow the established coding standards and include appropriate tests for new features.

## Documentation

### Project Documentation Structure

This project uses a comprehensive documentation system located in the `claudedocs/` directory, designed to support crash recovery, knowledge preservation, and project continuity.

#### Directory Organization

```
claudedocs/
├── analysis/          # Security analysis findings and IAM policy reviews
├── tasks/             # TODO.md and granular task tracking
├── decisions/         # Architecture Decision Records (ADRs)
└── progress/          # Session logs, summaries, and progress tracking
```

#### Key Documentation Files

**High-Level Overview:**
- [Executive Summary](claudedocs/analysis/00-executive-summary.md): Business value and project overview
- [Architecture](claudedocs/architecture.md): System design and component responsibilities
- [Roadmap](claudedocs/roadmap.md): Development phases and timeline

**Task Management:**
- [TODO.md](claudedocs/tasks/TODO.md): Master task list with 31 tasks across 4 phases
- [PROGRESS.md](claudedocs/progress/PROGRESS.md): Overall project completion metrics

**Technical Analysis:**
- [Zero Trust Principles](claudedocs/analysis/zero-trust-principles.md): Core security principles
- [IAM Analysis Methodology](claudedocs/analysis/iam-analysis-methodology.md): Analysis approach
- [Threat Model](claudedocs/analysis/threat-model.md): Security threats and mitigations
- [Compliance Requirements](claudedocs/analysis/compliance-requirements.md): Regulatory standards

**Development Guides:**
- [Development Setup](claudedocs/guides/development-setup.md): Environment configuration
- [Testing Strategy](claudedocs/guides/testing-strategy.md): Testing approach and standards
- [Contribution Guidelines](claudedocs/guides/contribution-guidelines.md): Collaboration standards

**Architecture Decisions:**
- [ADR 001: Documentation Structure](claudedocs/decisions/001-documentation-structure.md): Documentation organization rationale
- [ADR 002: Commit Strategy](claudedocs/decisions/002-commit-strategy.md): Crash recovery commit approach
- [ADR 003: CIEM Positioning](claudedocs/decisions/003-ciem-positioning.md): Cloud Infrastructure Entitlement Management strategy

**Progress Tracking:**
- [Session Log](claudedocs/progress/session-log.md): Chronological work tracking across all sessions
- [Session Summaries](claudedocs/progress/): Comprehensive session reviews (e.g., session-1-summary.md)

#### Crash Recovery Strategy

This project implements a robust crash recovery mechanism to prevent work loss during interruptions:

**Commit Strategy:**
- **Rule**: Commit after every completed task (see [ADR 002](claudedocs/decisions/002-commit-strategy.md))
- **Format**: `[Task] Brief description` with details and TODO.md reference
- **Benefit**: Maximum 1 task worth of work lost on crash (typically <1 hour)
- **Rollback**: Granular rollback capability to any task completion state

**Session Continuity:**
- **Session Logs**: Track all development sessions with goals, work completed, and next steps
- **Session Summaries**: Comprehensive reviews of major accomplishments per session
- **Progress Tracking**: Regular updates to PROGRESS.md and TODO.md status

**Recovery Procedure:**
1. Check `git log --oneline -10` to see recent commits
2. Review TODO.md to identify last completed task
3. Read session-log.md to understand session context
4. Resume from next pending task

**Documentation Philosophy:**
- Knowledge preservation over minimal documentation
- Structured organization for rapid information retrieval
- Version-controlled alongside code
- Human and AI agent accessible

### Additional Documentation

- [Architecture Overview](architecture-overview.md)
- [Project Structure](project-structure.md)
- [Implementation Plan](implementation-plan.md)
- [Execution Strategy](execution-strategy.md)
- [GitHub Workflow Guide](github-workflow-guide.md)
- [API Documentation](docs/api/README.md)
- [Deployment Guide](docs/deployment/README.md)
- [CIEM Capabilities](docs/CIEM_CAPABILITIES.md)
- [Security](docs/SECURITY.md)

## Troubleshooting

**Google Workspace authentication fails**
Verify your Google Workspace service account has domain-wide delegation enabled and that your service account JSON key is valid.

**Google Cloud API calls return permission errors**
Ensure your service account has the required IAM roles and that the APIs are enabled in your GCP project.

**Docker containers fail to start**
Check that all required environment variables are set in your .env file and that ports 3000 and 8000 are available.

For additional support, create an issue in the repository or review the troubleshooting guide.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Built with Google Cloud Platform, FastAPI, and React. Thanks to the open source community for the tools and libraries that made this project possible.
