# Architecture Analysis

**Document Date**: October 24, 2025
**Repository**: [MikeDominic92/ZeroTrust-IAM-Analyzer](https://github.com/MikeDominic92/ZeroTrust-IAM-Analyzer)
**Purpose**: Comprehensive technical analysis of system architecture, technology choices, and design patterns

---

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Three-Tier Architecture Breakdown](#three-tier-architecture-breakdown)
3. [Component Analysis](#component-analysis)
4. [Data Flow and System Interactions](#data-flow-and-system-interactions)
5. [Design Decisions and Patterns](#design-decisions-and-patterns)
6. [Technology Choices Rationale](#technology-choices-rationale)
7. [Scalability and Performance Considerations](#scalability-and-performance-considerations)
8. [Security Architecture](#security-architecture)

---

## System Architecture Overview

### High-Level Architecture

The ZeroTrust IAM Analyzer follows a modern three-tier architecture with clear separation of concerns, designed for cloud-native deployment on Google Cloud Platform while supporting multi-cloud analysis capabilities.

```
┌─────────────────────────────────────────────────────────────────┐
│                         PRESENTATION TIER                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ React Frontend (TypeScript + Vite)                         │ │
│  │ - Authentication UI                                         │ │
│  │ - Dashboard and Visualizations                             │ │
│  │ - Scan Configuration Interface                             │ │
│  │ - Results and Recommendations Display                      │ │
│  │ - State Management (Zustand + React Query)                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTPS/TLS
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION TIER                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ FastAPI Backend (Python 3.11+ Async)                       │ │
│  │ ┌────────────────────────────────────────────────────────┐ │ │
│  │ │ API Layer:         Authentication, Scan Management,    │ │ │
│  │ │                    Dashboard, Admin Endpoints          │ │ │
│  │ └────────────────────────────────────────────────────────┘ │ │
│  │ ┌────────────────────────────────────────────────────────┐ │ │
│  │ │ Service Layer:     GCP SDK, GCP SDK, Workspace SDK   │ │ │
│  │ │                    Analysis Engine, Policy Parser      │ │ │
│  │ └────────────────────────────────────────────────────────┘ │ │
│  │ ┌────────────────────────────────────────────────────────┐ │ │
│  │ │ Core Infrastructure: Security, Logging, Database,     │ │ │
│  │ │                      Config, Exception Handling        │ │ │
│  │ └────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓ SQL/TLS
┌─────────────────────────────────────────────────────────────────┐
│                          DATA TIER                               │
│  ┌──────────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │ PostgreSQL 15    │  │ Redis Cache     │  │ Object Storage │ │
│  │ - Users          │  │ - Sessions      │  │ - Reports      │ │
│  │ - Scans          │  │ - API Cache     │  │ - Exports      │ │
│  │ - Policies       │  │ - Rate Limits   │  │ - Attachments  │ │
│  │ - Recommendations│  │ - Queue         │  │                │ │
│  └──────────────────┘  └─────────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTPS
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL INTEGRATIONS                         │
│  ┌───────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ Microsoft     │  │ Google Cloud │  │ Google Workspace   │   │
│  │ Graph API     │  │ IAM API      │  │ Admin SDK          │   │
│  │ (Google Workspace)    │  │ (GCP)        │  │                    │   │
│  └───────────────┘  └──────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

**1. Separation of Concerns**
- Frontend: User interface and presentation logic only
- Backend: Business logic, security, orchestration
- Data Tier: Persistence, caching, storage

**2. API-First Design**
- RESTful API as primary interface
- Frontend consumes API (no server-side rendering)
- Enables future mobile apps, CLI tools, third-party integrations

**3. Async-First Implementation**
- Python async/await for I/O-bound operations
- Non-blocking cloud API calls
- Concurrent policy fetching across multiple resources
- Improved throughput and response times

**4. Stateless Application Tier**
- No server-side session state (JWT tokens)
- Horizontal scalability (add more backend instances)
- Cloud-native deployment (Cloud Run, Kubernetes)

**5. Defense in Depth**
- Multiple security layers (network, application, data)
- Authentication + Authorization + Audit
- Encryption in transit and at rest
- Rate limiting and DDoS protection

---

## Three-Tier Architecture Breakdown

### Tier 1: Presentation Layer (Frontend)

**Technology Stack**:
- **Framework**: React 18.2.0 (hooks-based, functional components)
- **Language**: TypeScript 5.2.2 (strict mode enabled)
- **Build Tool**: Vite 4.5.0 (fast HMR, optimized production builds)
- **State Management**: Zustand 4.4.1 (lightweight, no boilerplate)
- **Server State**: TanStack React Query 4.24.6 (caching, synchronization)
- **Styling**: Tailwind CSS 3.3.5 (utility-first, responsive)
- **Routing**: React Router DOM 6.8.0 (declarative, type-safe)
- **Forms**: React Hook Form 7.47.0 + Zod 3.22.2 (validation)

**Architecture Pattern**: Component-Based UI with Smart/Dumb Components

```
frontend/src/
├── components/          # Reusable UI components
│   ├── common/         # Buttons, inputs, modals (dumb components)
│   ├── auth/           # Login, registration, password reset
│   ├── dashboard/      # Dashboard widgets and visualizations
│   ├── scans/          # Scan configuration and results
│   └── layout/         # App shell, navigation, sidebar
│
├── pages/              # Route-level page components (smart components)
│   ├── HomePage.tsx
│   ├── DashboardPage.tsx
│   ├── ScansPage.tsx
│   └── SettingsPage.tsx
│
├── hooks/              # Custom React hooks
│   ├── useAuth.ts     # Authentication state and actions
│   ├── useScans.ts    # Scan data fetching and mutations
│   └── useDashboard.ts
│
├── services/           # API client layer
│   ├── api.ts         # Axios instance with interceptors
│   ├── auth.service.ts
│   ├── scan.service.ts
│   └── dashboard.service.ts
│
├── stores/             # Zustand state management
│   ├── authStore.ts   # User authentication state
│   ├── uiStore.ts     # UI state (sidebar, modals)
│   └── notificationStore.ts
│
├── utils/              # Utility functions
│   ├── validation.ts  # Zod schemas for form validation
│   ├── formatting.ts  # Date, number formatting
│   └── constants.ts   # App-wide constants
│
├── types/              # TypeScript type definitions
│   ├── models.ts      # Backend model types (User, Scan, etc.)
│   └── api.ts         # API request/response types
│
└── App.tsx             # Root component with routing
```

**Key Features**:

**1. State Management Strategy**
- **Zustand**: Global UI state (auth status, theme, notifications)
- **React Query**: Server state (API data, caching, refetching)
- **React Hook Form**: Form state (local to component, optimized)

**Rationale**: Avoid single monolithic state store (Redux complexity). Use specialized tools for different state types.

**2. API Client Design**
```typescript
// services/api.ts
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Add JWT token to all requests
apiClient.interceptors.request.use((config) => {
  const token = authStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: Handle 401 (unauthorized) globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

**3. Form Validation with Zod**
```typescript
// utils/validation.ts
import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

export type LoginFormData = z.infer<typeof loginSchema>;

// components/auth/LoginForm.tsx
const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
  resolver: zodResolver(loginSchema),
});
```

**Implementation Status**:
- [!] **0% Complete**: All component directories contain only .gitkeep placeholders
- [!] No authentication UI implemented
- [!] No dashboard or visualization components
- [!] No API integration layer
- [+] Package.json dependencies correctly configured

---

### Tier 2: Application Layer (Backend)

**Technology Stack**:
- **Framework**: FastAPI 0.104.1 (modern, async, automatic OpenAPI docs)
- **Runtime**: Python 3.11+ (performance improvements, type hints)
- **ASGI Server**: Uvicorn 0.24.0 (production-grade async server)
- **ORM**: SQLAlchemy 2.0.23 (async support, type-safe queries)
- **Migration Tool**: Alembic 1.12.1 (database schema versioning)
- **HTTP Client**: httpx 0.25.2 (async HTTP for cloud API calls)
- **Logging**: structlog 23.2.0 (structured, JSON logging)
- **Validation**: Pydantic 2.5.0 (runtime type checking, settings management)

**Architecture Pattern**: Layered Architecture with Dependency Injection

```
backend/app/
├── api/                    # API endpoints (REST controllers)
│   ├── v1/
│   │   ├── auth.py        # POST /login, /register, /refresh, /logout
│   │   ├── users.py       # GET/PUT /users/:id, POST /users
│   │   ├── scans.py       # GET/POST /scans, GET /scans/:id/status
│   │   ├── policies.py    # GET /policies, GET /policies/:id
│   │   ├── recommendations.py  # GET /recommendations
│   │   ├── dashboard.py   # GET /dashboard/overview, /dashboard/trends
│   │   └── admin.py       # Admin-only endpoints
│   └── deps.py            # Dependency injection (get_db, get_current_user)
│
├── core/                   # Core infrastructure
│   ├── config.py          # [IMPLEMENTED] Pydantic settings
│   ├── security.py        # [IMPLEMENTED] JWT, password hashing
│   ├── logging.py         # [IMPLEMENTED] Structured logging setup
│   ├── database.py        # [IMPLEMENTED] SQLAlchemy async engine
│   └── exceptions.py      # Custom exception classes
│
├── models/                 # SQLAlchemy ORM models
│   ├── base.py            # [IMPLEMENTED] Base model with UUID, timestamps
│   ├── user.py            # [IMPLEMENTED] User model (comprehensive RBAC)
│   ├── scan.py            # [IMPLEMENTED] Scan execution tracking
│   ├── policy.py          # [IMPLEMENTED] Policy data storage
│   └── recommendation.py  # [IMPLEMENTED] Security recommendations
│
├── schemas/                # Pydantic validation schemas (API contracts)
│   ├── auth.py            # [IMPLEMENTED] Login, register, token response
│   ├── user.py            # [IMPLEMENTED] User create, update, response
│   ├── scan.py            # [IMPLEMENTED] Scan create, status, results
│   ├── policy.py          # [IMPLEMENTED] Policy data schemas
│   └── recommendation.py  # [IMPLEMENTED] Recommendation schemas
│
├── services/               # Business logic layer
│   ├── auth_service.py    # User registration, authentication
│   ├── scan_service.py    # Scan orchestration and execution
│   ├── azure_service.py   # Google Workspace API integration
│   ├── gcp_service.py     # GCP IAM API integration
│   ├── workspace_service.py  # Google Workspace integration
│   ├── analysis_service.py   # Zero Trust scoring algorithm
│   └── recommendation_service.py  # Recommendation generation
│
├── utils/                  # Utility functions
│   ├── validators.py      # Custom validation logic
│   ├── formatters.py      # Data formatting utilities
│   └── helpers.py         # General helper functions
│
├── tests/                  # Test suite
│   ├── unit/              # Unit tests for services, models
│   ├── integration/       # Integration tests for APIs
│   └── fixtures/          # Test fixtures and factories
│
└── main.py                 # [IMPLEMENTED] FastAPI app entry point
```

**Key Design Patterns**:

**1. Dependency Injection Pattern**
```python
# api/deps.py
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency."""
    async with SessionLocal() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Extract and validate current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    return user

# api/v1/scans.py
@router.post("/scans", response_model=ScanResponse)
async def create_scan(
    scan_data: ScanCreate,
    current_user: User = Depends(get_current_user),  # Automatic injection
    db: AsyncSession = Depends(get_db)  # Automatic injection
):
    """Create a new security scan."""
    scan = await scan_service.create_scan(db, scan_data, current_user)
    return scan
```

**Benefits**:
- [+] Automatic database session management (no manual cleanup)
- [+] Centralized authentication logic (DRY principle)
- [+] Easy testing (mock dependencies)
- [+] Clear API endpoint signatures

**2. Service Layer Pattern**
```python
# services/scan_service.py
class ScanService:
    """Business logic for scan management."""

    async def create_scan(
        self,
        db: AsyncSession,
        scan_data: ScanCreate,
        user: User
    ) -> Scan:
        """
        Create a new scan with validation.

        Business logic:
        1. Validate user has permission to create scans
        2. Validate cloud provider credentials configured
        3. Create scan record in database
        4. Enqueue scan execution (async task)
        """
        if not user.has_permission("create_scan"):
            raise PermissionError("User does not have scan creation permission")

        # Validate credentials
        if "azure" in scan_data.sources and not settings.azure_tenant_id:
            raise ValueError("GCP credentials not configured")

        # Create scan record
        scan = Scan(
            created_by=user.id,
            sources=scan_data.sources,
            status=ScanStatus.PENDING,
        )
        db.add(scan)
        await db.commit()
        await db.refresh(scan)

        # Enqueue async execution
        await self._enqueue_scan(scan.id)

        return scan

    async def execute_scan(self, scan_id: UUID) -> None:
        """Execute scan analysis (runs in background worker)."""
        # Fetch policies from cloud providers
        # Analyze policies against Zero Trust tenets
        # Generate recommendations
        # Update scan status and results
        pass
```

**Benefits**:
- [+] Separation of concerns (API layer vs business logic)
- [+] Reusable business logic (multiple API endpoints can call same service)
- [+] Testable in isolation (mock database, no HTTP)
- [+] Clear transaction boundaries

**3. Repository Pattern** (Future Enhancement)
```python
# repositories/user_repository.py
class UserRepository:
    """Data access layer for User model."""

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Find user by email address."""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, user_data: UserCreate) -> User:
        """Create new user."""
        user = User(**user_data.dict())
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
```

**Benefits**:
- [+] Encapsulate database queries (service layer doesn't write SQL)
- [+] Easier to change ORM or database (isolate changes)
- [+] Consistent query patterns across codebase

**Implementation Status**:
- [+] **50% Complete**: Core infrastructure implemented (config, security, logging, database)
- [+] **60% Complete**: Models defined with proper relationships
- [+] **100% Complete**: Pydantic schemas for API validation
- [!] **0% Complete**: API endpoints (api/ directory empty)
- [!] **0% Complete**: Service layer (services/ directory empty)
- [!] **0% Complete**: Cloud provider integrations (SDKs not installed)

---

### Tier 3: Data Layer

**Technology Stack**:
- **Primary Database**: PostgreSQL 15 (ACID compliance, JSON support, full-text search)
- **Cache Layer**: Redis 7 (in-memory key-value store, pub/sub)
- **Object Storage**: Google Cloud Storage (planned, for reports and exports)

**Database Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                     PostgreSQL Database                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐       ┌──────────────┐                    │
│  │   users      │◄──────│   scans      │                    │
│  │              │ 1   N │              │                    │
│  │ - id (UUID)  │       │ - id (UUID)  │                    │
│  │ - email      │       │ - created_by │                    │
│  │ - role       │       │ - sources[]  │                    │
│  │ - status     │       │ - status     │                    │
│  │ - 2fa_enabled│       │ - zero_trust │                    │
│  │ - created_at │       │   _score     │                    │
│  └──────────────┘       └──────┬───────┘                    │
│                                 │ 1                          │
│                                 │                            │
│  ┌──────────────┐               │ N                          │
│  │  policies    │◄──────────────┘                            │
│  │              │                                            │
│  │ - id (UUID)  │       ┌──────────────────┐                │
│  │ - scan_id    │       │ recommendations  │                │
│  │ - source     │       │                  │                │
│  │ - risk_level │       │ - id (UUID)      │                │
│  │ - policy_json│       │ - scan_id        │                │
│  │ - compliance │       │ - priority       │                │
│  └──────────────┘       │ - severity       │                │
│                         │ - category       │                │
│                         │ - status         │                │
│                         └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

**Database Design Decisions**:

**1. UUID as Primary Key**
```python
# models/base.py
class Base(DeclarativeBase):
    """Base model with common fields."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier"
    )
```

**Rationale**:
- [+] Globally unique (safe for distributed systems, merging databases)
- [+] No sequential enumeration (security: can't guess next ID)
- [+] Consistent ID format across all models
- [!] Slightly larger storage than BIGINT (16 bytes vs 8 bytes)
- [!] Not human-readable (use display_id field if needed)

**2. Timestamp Tracking**
```python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False,
    comment="Timestamp when record was created"
)

updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    nullable=False,
    comment="Timestamp when record was last updated"
)
```

**Rationale**:
- [+] Audit trail for all records
- [+] Timezone-aware (UTC storage, local display)
- [+] Automatic updates via database triggers (consistent)

**3. Enum Types for Status Fields**
```python
class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

status: Mapped[ScanStatus] = mapped_column(
    SQLEnum(ScanStatus),
    default=ScanStatus.PENDING,
    nullable=False,
    index=True,
    comment="Current status of the scan"
)
```

**Rationale**:
- [+] Type safety (can't set invalid status values)
- [+] Database constraint enforcement
- [+] Self-documenting code (all valid values visible)
- [+] Index on status for efficient filtering (get all pending scans)

**4. JSONB for Flexible Data**
```python
# models/scan.py
zero_trust_tenet_scores: Mapped[Optional[dict]] = mapped_column(
    JSONB,
    nullable=True,
    comment="Per-tenet scores (1-7) in JSON format"
)

# Example data:
{
  "tenet_1_resources": 85,
  "tenet_2_communication": 70,
  "tenet_3_per_session": 60,
  "tenet_4_dynamic_policy": 45,
  "tenet_5_asset_monitoring": 50,
  "tenet_6_authentication": 75,
  "tenet_7_information_collection": 40
}
```

**Rationale**:
- [+] Flexible schema (add new tenets without migration)
- [+] PostgreSQL JSONB supports indexing and querying
- [+] Efficient storage for nested data
- [!] No referential integrity for JSON data
- [!] Requires application-level validation

**Redis Cache Strategy**:

```
┌─────────────────────────────────────────────────────────────┐
│                         Redis Cache                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SESSION CACHE:                                              │
│  - Key: session:{user_id}:{token_id}                         │
│  - Value: {user_id, role, permissions, device_id}            │
│  - TTL: 30 minutes (access token lifetime)                   │
│                                                              │
│  API RESPONSE CACHE:                                         │
│  - Key: api:dashboard:{user_id}                              │
│  - Value: {score, trends, recommendations}                   │
│  - TTL: 5 minutes                                            │
│                                                              │
│  RATE LIMITING:                                              │
│  - Key: ratelimit:{user_id}:{endpoint}                       │
│  - Value: request count                                      │
│  - TTL: 1 minute (sliding window)                            │
│                                                              │
│  TASK QUEUE:                                                 │
│  - Key: queue:scans                                          │
│  - Value: {scan_id, priority, created_at}                    │
│  - Type: Redis List (LPUSH/RPOP for FIFO)                    │
└─────────────────────────────────────────────────────────────┘
```

**Cache Invalidation Strategy**:
```python
# On user logout or token revocation:
await redis.delete(f"session:{user_id}:{token_id}")

# On scan completion:
await redis.delete(f"api:dashboard:{user_id}")  # Dashboard cache stale

# On policy change detected:
await redis.delete_pattern(f"api:*:{user_id}")  # Invalidate all user caches
```

**Implementation Status**:
- [+] **100% Complete**: Database models defined with proper schema
- [+] **100% Complete**: Enum types for status tracking
- [+] **100% Complete**: Audit fields (created_at, updated_at, created_by)
- [!] **0% Complete**: Alembic migrations not initialized
- [!] **0% Complete**: Redis integration (not configured)
- [!] **0% Complete**: Database indexes and constraints not optimized
- [!] **0% Complete**: No database connection pooling tuning

---

## Component Analysis

### Frontend Components (Planned)

**1. Authentication Components**
```
components/auth/
├── LoginForm.tsx          # Email + password login with MFA
├── RegisterForm.tsx       # User registration with email verification
├── PasswordResetForm.tsx  # Password reset request + token verification
├── MFASetup.tsx           # 2FA enrollment with QR code
└── MFAVerify.tsx          # 2FA code verification during login
```

**Key Features**:
- Form validation with React Hook Form + Zod
- Real-time password strength indicator
- Breached password checking (Have I Been Pwned API)
- Accessible forms (WCAG 2.1 AA compliance)

**2. Dashboard Components**
```
components/dashboard/
├── SecurityScoreCard.tsx      # 0-100 Zero Trust score with gauge
├── TenetBreakdownChart.tsx    # Radar chart for 7 tenets
├── TrendLineChart.tsx         # Historical score over time
├── RecommendationsWidget.tsx  # Top 5 priority recommendations
├── RecentScansTable.tsx       # Last 10 scans with status
└── ComplianceStatus.tsx       # NIST/ISO/SOC2 compliance badges
```

**Visualization Libraries**:
- **Recharts**: React-native charts (responsive, accessible)
- **D3.js**: Advanced custom visualizations if needed

**3. Scan Management Components**
```
components/scans/
├── ScanConfigForm.tsx     # Select sources, configure options
├── ScanStatusBadge.tsx    # Color-coded status indicator
├── ScanResultsTable.tsx   # Paginated policy list
├── PolicyDetailModal.tsx  # Deep dive into single policy
└── ScanScheduler.tsx      # Configure automated scans
```

### Backend Services (Planned)

**1. Authentication Service**
```python
# services/auth_service.py
class AuthService:
    async def register_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        """
        Register new user with email verification.

        Steps:
        1. Validate email not already registered
        2. Check password against breached password database
        3. Hash password with bcrypt (12 rounds)
        4. Create user record with status=PENDING_VERIFICATION
        5. Generate email verification token
        6. Send verification email
        """
        pass

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> TokenResponse:
        """
        Authenticate user and return JWT tokens.

        Steps:
        1. Find user by email
        2. Verify password hash
        3. Check account status (not locked, not suspended)
        4. Record login attempt (update last_login_at, reset failed_attempts)
        5. Generate access token (30 min) and refresh token (7 days)
        6. Return tokens
        """
        pass

    async def refresh_token(self, db: AsyncSession, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token.

        Steps:
        1. Validate refresh token signature and expiration
        2. Extract user_id from token
        3. Verify user still active
        4. Generate new access token
        5. Rotate refresh token (generate new one)
        6. Return new tokens
        """
        pass
```

**2. Scan Orchestration Service**
```python
# services/scan_service.py
class ScanService:
    def __init__(
        self,
        azure_service: GCPService,
        gcp_service: GCPService,
        workspace_service: WorkspaceService,
        analysis_service: AnalysisService
    ):
        self.azure = azure_service
        self.gcp = gcp_service
        self.workspace = workspace_service
        self.analysis = analysis_service

    async def execute_scan(self, scan_id: UUID) -> None:
        """
        Execute full security scan workflow.

        Workflow:
        1. Update scan status to RUNNING
        2. Fetch policies from all selected sources (parallel)
        3. Store raw policies in database
        4. Analyze policies (compute Zero Trust score)
        5. Generate recommendations
        6. Update scan status to COMPLETED
        7. Send notification to user

        Error handling:
        - Catch exceptions and update scan status to FAILED
        - Log detailed error information
        - Store partial results if some sources succeed
        """
        try:
            scan = await self._get_scan(scan_id)
            scan.status = ScanStatus.RUNNING
            await self._update_scan(scan)

            # Fetch policies in parallel
            tasks = []
            if "azure" in scan.sources:
                tasks.append(self.azure.fetch_policies())
            if "gcp" in scan.sources:
                tasks.append(self.gcp.fetch_policies())
            if "workspace" in scan.sources:
                tasks.append(self.workspace.fetch_policies())

            policy_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Store policies
            policies = []
            for result in policy_results:
                if isinstance(result, Exception):
                    logger.error("Policy fetch failed", error=str(result))
                else:
                    policies.extend(result)

            await self._store_policies(scan_id, policies)

            # Analyze
            analysis_result = await self.analysis.analyze(policies)

            # Update scan with results
            scan.status = ScanStatus.COMPLETED
            scan.zero_trust_score = analysis_result.overall_score
            scan.zero_trust_tenet_scores = analysis_result.tenet_scores
            await self._update_scan(scan)

            # Generate recommendations
            await self._generate_recommendations(scan_id, analysis_result)

        except Exception as e:
            logger.error("Scan execution failed", scan_id=scan_id, error=str(e))
            scan.status = ScanStatus.FAILED
            scan.error_message = str(e)
            await self._update_scan(scan)
            raise
```

**3. Cloud Provider Services**

**GCP Service**:
```python
# services/azure_service.py
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient

class GCPService:
    def __init__(self, settings: Settings):
        self.credential = ClientSecretCredential(
            tenant_id=settings.azure_tenant_id,
            client_id=settings.azure_client_id,
            client_secret=settings.azure_client_secret
        )
        self.client = GraphServiceClient(credentials=self.credential)

    async def fetch_policies(self) -> List[GCPPolicy]:
        """
        Fetch all Conditional Access policies from Google Workspace.

        API Endpoint: GET /identity/conditionalAccess/policies
        Required Permission: Policy.Read.All
        """
        policies = await self.client.identity.conditional_access.policies.get()
        return [self._parse_policy(p) for p in policies.value]

    async def fetch_users(self) -> List[GCPUser]:
        """Fetch all users from Google Workspace."""
        users = await self.client.users.get()
        return users.value

    async def fetch_groups(self) -> List[GCPGroup]:
        """Fetch all groups from Google Workspace."""
        groups = await self.client.groups.get()
        return groups.value
```

**GCP Service**:
```python
# services/gcp_service.py
from google.cloud import iam_v1
from google.cloud import resourcemanager_v3

class GCPService:
    def __init__(self, settings: Settings):
        self.iam_client = iam_v1.IAMClient()
        self.resource_client = resourcemanager_v3.ProjectsClient()
        self.project_id = settings.gcp_project_id

    async def fetch_policies(self) -> List[GCPPolicy]:
        """
        Fetch IAM policies for all projects in organization.

        API: resourcemanager.projects.getIamPolicy
        Required Permission: resourcemanager.projects.getIamPolicy
        """
        # Get all projects
        projects = self.resource_client.search_projects(
            query=f"parent:organizations/{self.org_id}"
        )

        # Fetch IAM policy for each project
        policies = []
        for project in projects:
            policy = self.resource_client.get_iam_policy(
                resource=project.name
            )
            policies.append(self._parse_policy(policy, project))

        return policies

    async def fetch_service_accounts(self) -> List[GCPServiceAccount]:
        """Fetch all service accounts in project."""
        accounts = self.iam_client.list_service_accounts(
            name=f"projects/{self.project_id}"
        )
        return list(accounts)
```

**4. Analysis Engine**
```python
# services/analysis_service.py
class AnalysisService:
    """Zero Trust scoring and analysis engine."""

    async def analyze(self, policies: List[Policy]) -> AnalysisResult:
        """
        Analyze policies and compute Zero Trust score.

        Scoring Algorithm:
        1. For each Zero Trust tenet (7 total):
           - Evaluate relevant policies
           - Check for tenet compliance
           - Assign score 0-100 for that tenet

        2. Compute overall score:
           - Weighted average of all tenets
           - Some tenets more critical (auth, encryption)

        3. Identify gaps and generate recommendations:
           - Missing MFA
           - Overly permissive policies
           - No encryption enforcement
        """
        tenet_scores = {
            "tenet_1_resources": await self._score_tenet_1(policies),
            "tenet_2_communication": await self._score_tenet_2(policies),
            "tenet_3_per_session": await self._score_tenet_3(policies),
            "tenet_4_dynamic_policy": await self._score_tenet_4(policies),
            "tenet_5_asset_monitoring": await self._score_tenet_5(policies),
            "tenet_6_authentication": await self._score_tenet_6(policies),
            "tenet_7_information_collection": await self._score_tenet_7(policies),
        }

        overall_score = self._compute_overall_score(tenet_scores)

        return AnalysisResult(
            overall_score=overall_score,
            tenet_scores=tenet_scores,
            total_policies=len(policies),
            high_risk_policies=self._count_high_risk(policies),
        )

    async def _score_tenet_6_authentication(self, policies: List[Policy]) -> int:
        """
        Score Tenet 6: Dynamic authentication.

        Criteria:
        - MFA required for all users? (+40 points)
        - Phishing-resistant MFA (FIDO2)? (+20 points)
        - Conditional access policies defined? (+20 points)
        - Risk-based authentication? (+20 points)

        Max Score: 100
        """
        score = 0

        # Check for MFA policies
        mfa_policies = [p for p in policies if self._is_mfa_policy(p)]
        if mfa_policies:
            coverage = self._calculate_user_coverage(mfa_policies)
            score += int(coverage * 40)  # 0-40 points based on coverage

        # Check for FIDO2 enforcement
        if any(self._requires_fido2(p) for p in mfa_policies):
            score += 20

        # Check for conditional access
        ca_policies = [p for p in policies if self._is_conditional_access(p)]
        if ca_policies:
            score += 20

        # Check for risk-based auth (Identity Protection)
        if any(self._uses_risk_detection(p) for p in ca_policies):
            score += 20

        return score
```

---

## Data Flow and System Interactions

### User Authentication Flow

```
┌────────┐                                                      ┌────────┐
│ Client │                                                      │ Server │
└───┬────┘                                                      └───┬────┘
    │                                                               │
    │ 1. POST /api/v1/auth/login                                    │
    │    {email, password}                                          │
    ├──────────────────────────────────────────────────────────────►│
    │                                                               │
    │                                      2. Query User by email   │
    │                                         ┌─────────────────┐   │
    │                                         │   PostgreSQL    │   │
    │                                         │   users table   │   │
    │                                         └────────▲────────┘   │
    │                                                  │            │
    │                                                  │            │
    │                                      3. Verify password hash  │
    │                                         (bcrypt.checkpw)      │
    │                                                               │
    │                                      4. Check account status  │
    │                                         (not locked/suspended)│
    │                                                               │
    │                                      5. Generate JWT tokens   │
    │                                         - Access token (30m)  │
    │                                         - Refresh token (7d)  │
    │                                                               │
    │                                      6. Update user record    │
    │                                         - last_login_at       │
    │                                         - last_login_ip       │
    │                                         - failed_attempts = 0 │
    │                                                  │            │
    │                                         ┌────────▼────────┐   │
    │                                         │   PostgreSQL    │   │
    │                                         │   UPDATE users  │   │
    │                                         └─────────────────┘   │
    │                                                               │
    │                                      7. Store session in Redis│
    │                                         ┌─────────────────┐   │
    │                                         │   Redis Cache   │   │
    │                                         │ session:{uuid}  │   │
    │                                         └─────────────────┘   │
    │                                                               │
    │ 8. 200 OK                                                     │
    │    {access_token, refresh_token, user}                        │
    │◄──────────────────────────────────────────────────────────────┤
    │                                                               │
    │ 9. Store tokens in localStorage/secure cookie                 │
    │                                                               │
    │ 10. Subsequent requests include:                              │
    │     Authorization: Bearer {access_token}                      │
    ├──────────────────────────────────────────────────────────────►│
    │                                                               │
    │                                     11. Validate JWT signature│
    │                                         Extract user_id       │
    │                                         Check Redis session   │
    │                                                               │
    │ 12. 200 OK {resource}                                         │
    │◄──────────────────────────────────────────────────────────────┤
    │                                                               │
```

**Security Considerations**:
1. [+] Password never transmitted in plaintext (hashed with bcrypt)
2. [+] JWT tokens short-lived (30 minutes)
3. [+] Refresh token rotation (new refresh token issued on every refresh)
4. [+] Account lockout after 5 failed attempts
5. [+] Session tracking in Redis (can invalidate all sessions)
6. [!] No rate limiting implemented yet (vulnerable to brute force)
7. [!] No IP-based anomaly detection yet

### Scan Execution Flow

```
┌────────┐    ┌────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Client │    │  API   │    │  Scan    │    │  Cloud   │    │ Analysis │
│        │    │ Layer  │    │ Service  │    │ Services │    │ Service  │
└───┬────┘    └───┬────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
    │             │              │               │               │
    │ 1. POST /scans              │               │               │
    │    {sources:["azure"]}      │               │               │
    ├────────────►│              │               │               │
    │             │              │               │               │
    │             │ 2. Create    │               │               │
    │             │    Scan      │               │               │
    │             │    record    │               │               │
    │             ├──────────────►               │               │
    │             │              │               │               │
    │             │              │ 3. Insert     │               │
    │             │              │    into DB    │               │
    │             │              ├──────────┐    │               │
    │             │              │ status=  │    │               │
    │             │              │ PENDING  │    │               │
    │             │              └──────────┘    │               │
    │             │              │               │               │
    │             │              │ 4. Enqueue   │               │
    │             │              │    task      │               │
    │             │              ├──────────┐    │               │
    │             │              │ Redis    │    │               │
    │             │              │ queue    │    │               │
    │             │              └──────────┘    │               │
    │             │              │               │               │
    │ 5. 202 Accepted            │               │               │
    │    {scan_id, status}       │               │               │
    │◄────────────┤              │               │               │
    │             │              │               │               │
    │             │              │ 6. Background │               │
    │             │              │    worker     │               │
    │             │              │    picks up   │               │
    │             │              │    task       │               │
    │             │              │               │               │
    │             │              │ 7. Update     │               │
    │             │              │    status=    │               │
    │             │              │    RUNNING    │               │
    │             │              │               │               │
    │             │              │ 8. Fetch      │               │
    │             │              │    GCP      │               │
    │             │              │    policies   │               │
    │             │              ├───────────────►               │
    │             │              │               │               │
    │             │              │               │ 9. Call       │
    │             │              │               │    Microsoft  │
    │             │              │               │    Graph API  │
    │             │              │               ├──────────┐    │
    │             │              │               │ GET      │    │
    │             │              │               │ /identity│    │
    │             │              │               │ /policies│    │
    │             │              │               └──────────┘    │
    │             │              │               │               │
    │             │              │ 10. Return    │               │
    │             │              │     policies  │               │
    │             │              │◄──────────────┤               │
    │             │              │               │               │
    │             │              │ 11. Store     │               │
    │             │              │     policies  │               │
    │             │              ├──────────┐    │               │
    │             │              │ INSERT   │    │               │
    │             │              │ policies │    │               │
    │             │              └──────────┘    │               │
    │             │              │               │               │
    │             │              │ 12. Analyze   │               │
    │             │              │     policies  │               │
    │             │              ├───────────────┼───────────────►
    │             │              │               │               │
    │             │              │               │ 13. Compute   │
    │             │              │               │     scores    │
    │             │              │               ├──────────┐    │
    │             │              │               │ Tenet 1-7│    │
    │             │              │               │ algorithm│    │
    │             │              │               └──────────┘    │
    │             │              │               │               │
    │             │              │ 14. Return    │               │
    │             │              │     analysis  │               │
    │             │              │◄──────────────┼───────────────┤
    │             │              │               │               │
    │             │              │ 15. Generate  │               │
    │             │              │     recommendations           │
    │             │              ├──────────┐    │               │
    │             │              │ INSERT   │    │               │
    │             │              │ recommen-│    │               │
    │             │              │ dations  │    │               │
    │             │              └──────────┘    │               │
    │             │              │               │               │
    │             │              │ 16. Update    │               │
    │             │              │     scan      │               │
    │             │              │     status=   │               │
    │             │              │     COMPLETED │               │
    │             │              │               │               │
    │ 17. WebSocket notification │               │               │
    │     "Scan completed"        │               │               │
    │◄────────────────────────────               │               │
    │             │              │               │               │
    │ 18. GET /scans/:id         │               │               │
    ├────────────►│              │               │               │
    │             │              │               │               │
    │ 19. 200 OK                 │               │               │
    │     {scan with results}    │               │               │
    │◄────────────┤              │               │               │
```

**Performance Optimizations**:
1. [+] Async background processing (don't block API response)
2. [+] Parallel policy fetching (GCP, GCP, Workspace concurrently)
3. [+] Redis queue for task distribution (multiple workers)
4. [+] WebSocket for real-time status updates (no polling)
5. [!] No caching of cloud provider responses (fetch every time)
6. [!] No incremental scans (always full scan)

---

## Design Decisions and Patterns

### 1. Async-First Architecture

**Decision**: Use Python async/await throughout backend application.

**Rationale**:
- [+] I/O-bound workload (cloud API calls, database queries)
- [+] Better concurrency (handle multiple requests with fewer threads)
- [+] Reduced memory footprint (no thread overhead)
- [+] Native support in FastAPI, SQLAlchemy 2.0, httpx

**Implementation**:
```python
# Async route handler
@router.get("/scans/{scan_id}")
async def get_scan(
    scan_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ScanResponse:
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(404, "Scan not found")
    return scan

# Async service method
async def fetch_azure_policies(self) -> List[Policy]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{self.graph_url}/identity/conditionalAccess/policies",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.json()
```

**Trade-offs**:
- [+] Excellent for I/O-bound operations
- [!] Slightly more complex debugging (async stack traces)
- [!] Requires async-compatible libraries (can't use blocking libraries)

### 2. JWT Token-Based Authentication

**Decision**: Use JWT tokens (not server-side sessions) for authentication.

**Rationale**:
- [+] Stateless (no session storage on server)
- [+] Horizontally scalable (any backend instance can validate token)
- [+] Works across different services (microservices, API gateway)
- [+] Mobile-friendly (no cookies required)

**Token Structure**:
```json
{
  "sub": "user-uuid-here",
  "email": "user@example.com",
  "role": "analyst",
  "iat": 1698789123,
  "exp": 1698791923
}
```

**Security Measures**:
```python
# Short-lived access tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Refresh token rotation
async def refresh_access_token(refresh_token: str) -> TokenResponse:
    # Validate old refresh token
    # Generate NEW access token
    # Generate NEW refresh token (rotate)
    # Invalidate old refresh token
    pass

# Token blacklist (for logout)
async def logout(token: str) -> None:
    # Add token to Redis blacklist with TTL=remaining token lifetime
    await redis.setex(f"blacklist:{token}", ttl, "1")
```

**Trade-offs**:
- [+] Stateless and scalable
- [+] No database lookup per request
- [!] Cannot revoke tokens immediately (must wait for expiration)
- [!] Larger payload than session IDs (200-500 bytes)
- Solution: Short expiration + refresh token rotation + blacklist for logout

### 3. Repository Pattern (Future)

**Decision**: Plan to implement Repository pattern for data access.

**Rationale**:
- [+] Encapsulate database queries (service layer doesn't write SQL)
- [+] Testable (easy to mock repository)
- [+] Consistent query patterns (one place to optimize)
- [+] Easier to migrate ORM or database

**Example**:
```python
# repositories/user_repository.py
class UserRepository:
    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, user: User) -> User:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

# services/auth_service.py
class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.users = user_repo

    async def register(self, db: AsyncSession, data: UserCreate) -> User:
        existing = await self.users.get_by_email(db, data.email)
        if existing:
            raise ValueError("Email already registered")

        user = User(email=data.email, ...)
        return await self.users.create(db, user)
```

**Status**: Not yet implemented (currently models accessed directly)

### 4. Structured Logging

**Decision**: Use structlog for structured JSON logging.

**Rationale**:
- [+] Machine-parseable logs (easily ingest into SIEM)
- [+] Contextual logging (add fields: user_id, request_id, trace_id)
- [+] Efficient log querying (filter by structured fields)
- [+] Better observability

**Implementation**:
```python
# core/logging.py
import structlog

logger = structlog.get_logger()

# Usage in code
logger.info(
    "user_login_success",
    user_id=str(user.id),
    email=user.email,
    ip_address=request.client.host,
    duration_ms=123
)

# Output (JSON):
{
  "event": "user_login_success",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "ip_address": "192.0.2.1",
  "duration_ms": 123,
  "timestamp": "2025-10-24T10:30:00Z",
  "level": "info"
}
```

**Benefits for Production**:
- [+] Easy log aggregation (Splunk, ELK, Google Cloud Logging)
- [+] Correlation across services (trace_id propagation)
- [+] Alerting on specific events (user_login_failed count)

---

## Technology Choices Rationale

### Backend Framework: FastAPI

**Alternatives Considered**: Django, Flask, Quart

**Decision**: FastAPI

**Rationale**:
1. [+] **Performance**: Built on Starlette (async ASGI), comparable to Node.js/Go
2. [+] **Async Native**: First-class async/await support (not bolted on)
3. [+] **Automatic API Docs**: OpenAPI/Swagger UI generation from code
4. [+] **Type Safety**: Leverages Python type hints for validation (Pydantic)
5. [+] **Modern Python**: Designed for Python 3.7+ (no legacy baggage)
6. [+] **Developer Experience**: Excellent error messages, fast feedback loop

**Comparison**:
- **vs Django**: Django heavy for API-only backend, ORM not async-native
- **vs Flask**: Flask synchronous, requires extensions for async
- **vs Quart**: Similar to FastAPI, but smaller ecosystem

### ORM: SQLAlchemy 2.0

**Alternatives Considered**: Django ORM, Tortoise ORM, raw SQL

**Decision**: SQLAlchemy 2.0

**Rationale**:
1. [+] **Async Support**: Native async in 2.0 release
2. [+] **Maturity**: 15+ years of development, battle-tested
3. [+] **Flexibility**: Can use ORM or Core (SQL expression language)
4. [+] **Type Safety**: Mapped classes with type annotations
5. [+] **Ecosystem**: Alembic migrations, large community

**SQLAlchemy 2.0 Features**:
```python
# New declarative style with type hints
class User(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    role: Mapped[UserRole]  # Enum support

# Async queries
async with AsyncSession(engine) as session:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
```

### Frontend Framework: React + TypeScript

**Alternatives Considered**: Vue, Angular, Svelte

**Decision**: React 18 + TypeScript

**Rationale**:
1. [+] **Ecosystem**: Largest component library ecosystem (MUI, Ant Design, Chakra)
2. [+] **Type Safety**: TypeScript for fewer runtime errors
3. [+] **Developer Experience**: Fast Refresh, DevTools, excellent documentation
4. [+] **Performance**: React 18 concurrent features, automatic batching
5. [+] **Hiring**: Easier to find React developers

**TypeScript Benefits**:
- [+] Catch errors at compile-time (not runtime)
- [+] Excellent IDE support (autocomplete, refactoring)
- [+] Self-documenting code (types as documentation)
- [+] Safer refactoring (compiler catches breaking changes)

### Build Tool: Vite

**Alternatives Considered**: Create React App (CRA), Webpack, Parcel

**Decision**: Vite 4

**Rationale**:
1. [+] **Fast Dev Server**: Instant server start (native ESM)
2. [+] **Hot Module Replacement**: Sub-second HMR (better than CRA)
3. [+] **Optimized Builds**: Rollup for production (tree-shaking, code splitting)
4. [+] **Modern**: Built for modern browsers, no legacy baggage
5. [+] **Simple Config**: Minimal configuration required

**Performance Comparison**:
- **CRA**: ~30-60 seconds cold start, 1-3 seconds HMR
- **Vite**: <1 second cold start, <100ms HMR

### State Management: Zustand + React Query

**Alternatives Considered**: Redux, MobX, Recoil, Jotai

**Decision**: Zustand (UI state) + React Query (server state)

**Rationale**:
1. [+] **Simplicity**: Minimal boilerplate compared to Redux
2. [+] **Performance**: Only re-renders components that use changed state
3. [+] **TypeScript**: Excellent TypeScript support
4. [+] **Specialized Tools**: React Query for server state (caching, refetching)

**Zustand Example**:
```typescript
// stores/authStore.ts
interface AuthState {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  login: async (email, password) => {
    const response = await authService.login(email, password);
    set({ user: response.user, token: response.token });
  },
  logout: () => set({ user: null, token: null }),
}));

// Usage in component
const { user, login } = useAuthStore();
```

**React Query Example**:
```typescript
// hooks/useScans.ts
const useScans = () => {
  return useQuery({
    queryKey: ['scans'],
    queryFn: () => scanService.getScans(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
};

// Usage
const { data: scans, isLoading, error, refetch } = useScans();
```

---

## Scalability and Performance Considerations

### Horizontal Scalability

**Current Architecture**: Stateless application tier enables horizontal scaling.

**Deployment Strategy**:
```
┌──────────────────────────────────────────────────┐
│         Google Cloud Load Balancer               │
│         (HTTPS, SSL termination)                 │
└────────────┬─────────────────────────────────────┘
             │
       ┌─────┴──────┐
       │            │
┌──────▼─────┐ ┌───▼────────┐ ┌───────────┐
│ Backend    │ │ Backend    │ │ Backend   │
│ Instance 1 │ │ Instance 2 │ │ Instance N│
│ (Cloud Run)│ │ (Cloud Run)│ │(Cloud Run)│
└──────┬─────┘ └───┬────────┘ └─────┬─────┘
       │           │                │
       └───────────┼────────────────┘
                   │
       ┌───────────▼────────────┐
       │ Cloud SQL (PostgreSQL) │
       │ with read replicas     │
       └────────────────────────┘
```

**Auto-Scaling Configuration**:
```yaml
# cloud-run.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: iam-analyzer-backend
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "2"
        autoscaling.knative.dev/maxScale: "100"
        autoscaling.knative.dev/target: "80"  # Target 80% CPU
    spec:
      containers:
      - image: gcr.io/project/iam-analyzer-backend
        resources:
          limits:
            memory: "512Mi"
            cpu: "1000m"
```

**Scalability Considerations**:
- [+] Stateless application tier (scale infinitely)
- [+] JWT tokens (no shared session state)
- [+] Redis for shared cache (not critical path)
- [!] PostgreSQL bottleneck (vertical scaling limit)
- [!] Cloud API rate limits (external dependency)

### Database Performance

**Connection Pooling**:
```python
# core/database.py
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=20,          # Max connections in pool
    max_overflow=10,       # Additional connections when pool full
    pool_timeout=30,       # Seconds to wait for connection
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True,    # Validate connection before use
)
```

**Indexing Strategy**:
```sql
-- User lookups by email (login)
CREATE INDEX idx_users_email ON users(email);

-- Scan lookups by user and status
CREATE INDEX idx_scans_user_status ON scans(created_by, status);

-- Policy lookups by scan
CREATE INDEX idx_policies_scan_id ON policies(scan_id);

-- Recommendation lookups by scan and priority
CREATE INDEX idx_recommendations_scan_priority
  ON recommendations(scan_id, priority);
```

**Query Optimization**:
```python
# Eager loading to avoid N+1 queries
scan = await db.execute(
    select(Scan)
    .options(
        selectinload(Scan.policies),
        selectinload(Scan.recommendations)
    )
    .where(Scan.id == scan_id)
)

# Instead of:
# scan = await db.get(Scan, scan_id)
# policies = scan.policies  # Triggers separate query (N+1 problem)
```

### Caching Strategy

**Multi-Layer Caching**:

**1. Redis Cache (Application-Level)**:
```python
# Cache expensive dashboard query
@cache(ttl=300)  # 5 minutes
async def get_dashboard_data(user_id: UUID) -> DashboardData:
    # Expensive aggregation query
    pass

# Cache cloud provider responses
@cache(ttl=3600)  # 1 hour
async def fetch_azure_policies(tenant_id: str) -> List[Policy]:
    # External API call
    pass
```

**2. Browser Cache (HTTP Headers)**:
```python
@router.get("/dashboard/overview")
async def dashboard_overview():
    response = JSONResponse(content=data)
    response.headers["Cache-Control"] = "private, max-age=300"  # 5 min
    return response
```

**3. CDN Cache (Static Assets)**:
```
Frontend build output:
  /assets/main.[hash].js  # Cache forever (immutable, content-addressed)
  /assets/styles.[hash].css  # Cache forever
  /index.html  # No cache (entry point, frequent updates)
```

### API Rate Limiting

**Implementation**:
```python
# middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Global rate limit
@app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Endpoint-specific limits
@router.post("/auth/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute per IP
async def login(request: Request, credentials: LoginRequest):
    pass

@router.post("/scans")
@limiter.limit("10/hour")  # Max 10 scans per hour per user
async def create_scan(request: Request, scan_data: ScanCreate):
    pass
```

**Redis-Based Rate Limiting** (per user):
```python
async def check_rate_limit(user_id: UUID, endpoint: str, limit: int, window: int):
    """
    Sliding window rate limiting.

    Args:
        user_id: User identifier
        endpoint: API endpoint
        limit: Max requests allowed
        window: Time window in seconds
    """
    key = f"ratelimit:{user_id}:{endpoint}"
    current = await redis.get(key)

    if current and int(current) >= limit:
        raise RateLimitExceeded(f"Max {limit} requests per {window}s")

    pipe = redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, window)
    await pipe.execute()
```

---

## Security Architecture

### Defense in Depth Layers

**1. Network Layer**:
- HTTPS/TLS 1.3 for all connections
- WAF (Web Application Firewall) for DDoS protection
- VPC isolation for backend services
- Private IP for database (not internet-accessible)

**2. Application Layer**:
- JWT token authentication
- Role-based access control (RBAC)
- Input validation (Pydantic schemas)
- SQL injection prevention (parameterized queries via ORM)
- XSS prevention (React escapes by default)
- CSRF protection (SameSite cookies, CORS configuration)

**3. Data Layer**:
- Encryption at rest (database, object storage)
- Encryption in transit (TLS for all connections)
- Password hashing (bcrypt with 12 rounds)
- Secrets management (Google Secret Manager for credentials)

### OWASP Top 10 Mitigation

**A01: Broken Access Control**:
```python
# Enforce authorization on every request
@router.get("/scans/{scan_id}")
async def get_scan(
    scan_id: UUID,
    current_user: User = Depends(get_current_user),  # Authentication
    db: AsyncSession = Depends(get_db)
):
    scan = await db.get(Scan, scan_id)

    # Authorization: User can only access own scans (or admin)
    if scan.created_by != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "Access denied")

    return scan
```

**A02: Cryptographic Failures**:
```python
# Enforce HTTPS in production
if settings.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Secure password hashing
password_hash = bcrypt.hashpw(
    password.encode('utf-8'),
    bcrypt.gensalt(rounds=12)  # Adaptive, increase rounds over time
)

# Encrypt sensitive data in database
encrypted_secret = encrypt(api_key, encryption_key)
```

**A03: Injection**:
```python
# Parameterized queries via SQLAlchemy (no raw SQL)
result = await db.execute(
    select(User).where(User.email == email)  # Safe, parameterized
)

# Input validation with Pydantic
class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    password: constr(min_length=8, max_length=128)  # Length constraints
```

**A07: Identification and Authentication Failures**:
```python
# Multi-factor authentication
if user.two_factor_enabled:
    if not verify_totp(mfa_code, user.two_factor_secret):
        raise HTTPException(401, "Invalid MFA code")

# Account lockout
if user.failed_login_attempts >= 5:
    user.status = UserStatus.LOCKED
    raise HTTPException(403, "Account locked due to failed login attempts")

# Session timeout
if token_age > settings.access_token_expire_minutes * 60:
    raise HTTPException(401, "Token expired")
```

### Secrets Management

**Current** (Development):
```bash
# .env file (git-ignored)
SECRET_KEY=development-secret-key
AZURE_CLIENT_SECRET=...
GCP_SERVICE_ACCOUNT_KEY=...
```

**Production** (Google Secret Manager):
```python
# core/secrets.py
from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    """Retrieve secret from Google Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Usage
SECRET_KEY = get_secret("jwt-secret-key")
AZURE_CLIENT_SECRET = get_secret("azure-client-secret")
```

**Benefits**:
- [+] Secrets not in code or environment variables
- [+] Automatic rotation support
- [+] Audit logging of secret access
- [+] IAM-based access control

---

## Conclusion

The ZeroTrust IAM Analyzer architecture demonstrates professional engineering practices with a clear separation of concerns, modern technology choices, and comprehensive security design. The three-tier architecture provides flexibility for future enhancements while the async-first implementation ensures excellent performance for I/O-bound workloads.

**Key Strengths**:
1. [+] Modern, async-first Python backend with FastAPI
2. [+] Type-safe implementation (Python type hints, TypeScript)
3. [+] Scalable, stateless application tier
4. [+] Security-first design with defense in depth
5. [+] Well-organized codebase following best practices

**Implementation Status**:
- Core infrastructure: 50% complete
- Data models: 60% complete
- API endpoints: 0% complete
- Cloud integrations: 0% complete
- Frontend: 0% complete

**Next Steps**:
1. Implement authentication API endpoints
2. Integrate GCP SDK for policy fetching
3. Build analysis engine with Zero Trust scoring
4. Create frontend authentication and dashboard components
5. Add comprehensive testing

---

**Document Version**: 1.0
**Last Updated**: October 24, 2025
**Next Review**: Upon MVP completion

**References**:
- [Executive Summary](./00-executive-summary.md)
- [Project Overview](./01-project-overview.md)
- [Implementation Status](./04-implementation-status.md)
