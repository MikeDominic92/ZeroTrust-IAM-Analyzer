# Phase 1: Foundation - Authentication and Core Infrastructure

**Phase Duration**: 3-5 days (full-time) or 1-2 weeks (part-time)
**Priority**: CRITICAL - Blocks all other development
**Dependencies**: Phase 0 (Setup) must be complete

---

## Phase Overview

Phase 1 establishes the security foundation for the entire application. This includes user authentication, JWT token management, role-based access control (RBAC), session management, and password reset workflows. All subsequent features depend on these core security capabilities.

**Success Criteria**:
- Users can register, login, and logout securely
- JWT tokens are generated, verified, and refreshed properly
- RBAC enforcement protects all API endpoints
- Password reset workflow functions end-to-end
- 90%+ test coverage for all security components
- OpenAPI documentation generated for all auth endpoints

---

## Task 1.1: Install and Configure Authentication Dependencies

**User Story**: As a developer, I need authentication libraries installed so I can implement secure user authentication.

**Time Estimate**: 30 minutes

**Acceptance Criteria**:
- [ ] `bcrypt` library installed for password hashing
- [ ] `python-jose[cryptography]` installed for JWT operations
- [ ] `passlib[bcrypt]` installed for password utilities
- [ ] Dependencies added to `requirements.txt` and `requirements-dev.txt`
- [ ] Version pinning applied (e.g., `bcrypt>=4.0.0,<5.0.0`)
- [ ] Virtual environment rebuilt with new dependencies
- [ ] Import tests pass (`from passlib.context import CryptContext`)

**Implementation Steps**:
1. Add to `backend/requirements.txt`:
   ```
   bcrypt>=4.0.0,<5.0.0
   python-jose[cryptography]>=3.3.0,<4.0.0
   passlib[bcrypt]>=1.7.4,<2.0.0
   ```
2. Rebuild virtual environment: `pip install -r requirements.txt`
3. Verify imports in Python shell

**Technical Notes**:
- Use bcrypt with 12 rounds for password hashing (already configured in `core/security.py`)
- JWT algorithm should be HS256 (already configured)
- Secret key must be 32+ characters (validate in config)

---

## Task 1.2: Create Alembic Migrations for User, Role, and Session Models

**User Story**: As a developer, I need database tables created so I can store user authentication data.

**Time Estimate**: 1-2 hours

**Acceptance Criteria**:
- [ ] Alembic migration file generated with all models
- [ ] Migration includes `users`, `roles`, `user_roles`, `sessions` tables
- [ ] All foreign key constraints defined correctly
- [ ] UUID primary keys configured with `gen_random_uuid()`
- [ ] Timestamps (created_at, updated_at) configured with defaults
- [ ] Migration applies successfully: `alembic upgrade head`
- [ ] Migration rollback works: `alembic downgrade -1`
- [ ] Database schema matches model definitions exactly

**Implementation Steps**:
1. Ensure PostgreSQL is running via Docker Compose
2. Generate migration: `alembic revision --autogenerate -m "Add user authentication models"`
3. Review generated migration file for accuracy
4. Apply migration: `alembic upgrade head`
5. Verify tables in database: `psql -d iam_analyzer -c "\dt"`
6. Test rollback: `alembic downgrade -1` then `alembic upgrade head`

**Technical Notes**:
- Check that UUID extension is enabled: `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`
- Verify indexes on frequently queried columns (email, username)
- Ensure `is_deleted` column has default false
- Session table should have index on `token_jti` for fast lookup

**Database Schema Validation**:
```sql
-- Verify users table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users';

-- Verify foreign keys
SELECT constraint_name, table_name, column_name
FROM information_schema.key_column_usage
WHERE table_name IN ('users', 'sessions', 'user_roles');
```

---

## Task 1.3: Implement User Registration Endpoint

**User Story**: As a new user, I want to register an account so I can access the application.

**Time Estimate**: 2-3 hours

**Acceptance Criteria**:
- [ ] POST `/api/v1/auth/register` endpoint created
- [ ] Request validates email format, password strength, username length
- [ ] Duplicate email/username returns 409 Conflict
- [ ] Password is hashed with bcrypt (12 rounds) before storage
- [ ] User assigned default "User" role automatically
- [ ] Response includes user ID, email, username (no password)
- [ ] Returns 201 Created on success
- [ ] Returns 400 Bad Request for validation errors
- [ ] Unit tests cover success and all error cases
- [ ] Integration test verifies database record creation

**API Specification**:
```
POST /api/v1/auth/register
Content-Type: application/json

Request Body:
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}

Success Response (201):
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "created_at": "2025-10-24T10:30:00Z"
}

Error Response (409):
{
  "detail": "Email already registered"
}
```

**Implementation Steps**:
1. Create `backend/app/api/v1/auth.py` router file
2. Define `UserCreate` schema in `schemas/user.py`
3. Implement registration service in `services/auth_service.py`
4. Add password strength validation (min 8 chars, 1 uppercase, 1 number, 1 special)
5. Query database to check for existing email/username
6. Hash password using `security.get_password_hash()`
7. Create user record with default role
8. Return user data (exclude password hash)
9. Write unit tests for all validation rules
10. Write integration test for full workflow

**Validation Rules**:
- Email: Valid email format, max 255 characters
- Username: 3-50 characters, alphanumeric and underscore only
- Password: Min 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
- Full name: Max 255 characters, optional

---

## Task 1.4: Implement Login Endpoint with JWT Token Generation

**User Story**: As a registered user, I want to login with my credentials so I can access protected resources.

**Time Estimate**: 2-3 hours

**Acceptance Criteria**:
- [ ] POST `/api/v1/auth/login` endpoint created
- [ ] Accepts email/username and password
- [ ] Verifies password using bcrypt comparison
- [ ] Returns JWT access token (15-minute expiry)
- [ ] Returns JWT refresh token (7-day expiry)
- [ ] Creates session record in database
- [ ] Updates `last_login_at` timestamp on user
- [ ] Increments `failed_login_attempts` on wrong password
- [ ] Locks account after 5 failed attempts
- [ ] Returns 401 Unauthorized for invalid credentials
- [ ] Returns 403 Forbidden for locked accounts
- [ ] Unit tests cover all authentication scenarios
- [ ] Integration test verifies token validity

**API Specification**:
```
POST /api/v1/auth/login
Content-Type: application/json

Request Body:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Success Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "johndoe",
    "roles": ["User"]
  }
}

Error Response (401):
{
  "detail": "Invalid credentials"
}

Error Response (403):
{
  "detail": "Account locked due to too many failed attempts"
}
```

**Implementation Steps**:
1. Create login endpoint in `api/v1/auth.py`
2. Implement `authenticate_user()` in `services/auth_service.py`
3. Verify password with `security.verify_password()`
4. Generate JWT tokens with `security.create_access_token()`
5. Include user ID, email, roles in JWT payload
6. Create session record with token JTI
7. Update user's `last_login_at` timestamp
8. Handle failed login attempts with counter
9. Implement account lockout logic (5 attempts)
10. Write comprehensive unit and integration tests

**JWT Payload Structure**:
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "roles": ["User"],
  "type": "access",
  "jti": "token-uuid",
  "exp": 1635431700
}
```

---

## Task 1.5: Implement JWT Token Verification Middleware

**User Story**: As a developer, I need JWT verification middleware so protected endpoints can authenticate requests.

**Time Estimate**: 2 hours

**Acceptance Criteria**:
- [ ] Dependency function `get_current_user()` created
- [ ] Extracts JWT token from Authorization header
- [ ] Validates token signature and expiration
- [ ] Verifies session is active in database
- [ ] Returns `User` object for valid tokens
- [ ] Returns 401 Unauthorized for missing/invalid tokens
- [ ] Returns 401 Unauthorized for expired tokens
- [ ] Returns 401 Unauthorized for revoked sessions
- [ ] Handles malformed tokens gracefully
- [ ] Unit tests cover all validation paths
- [ ] Integration test verifies protected endpoint access

**Implementation Steps**:
1. Create `get_current_user()` in `core/dependencies.py`
2. Extract token from `Authorization: Bearer <token>` header
3. Decode and verify JWT using `jose.jwt.decode()`
4. Check token expiration timestamp
5. Query session table by token JTI
6. Verify session is not revoked and not expired
7. Query user by ID from token payload
8. Verify user is not deleted or disabled
9. Return `User` object with roles
10. Write tests for all failure scenarios

**Usage Example**:
```python
from fastapi import Depends
from app.core.dependencies import get_current_user

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    return {"message": f"Hello {current_user.username}"}
```

---

## Task 1.6: Implement Token Refresh Endpoint

**User Story**: As a user, I want to refresh my access token so I can stay logged in without re-authenticating.

**Time Estimate**: 1-2 hours

**Acceptance Criteria**:
- [ ] POST `/api/v1/auth/refresh` endpoint created
- [ ] Accepts refresh token in request body
- [ ] Validates refresh token signature and expiration
- [ ] Verifies session is active in database
- [ ] Generates new access token (15-minute expiry)
- [ ] Optionally generates new refresh token (7-day expiry)
- [ ] Updates session record with new token JTI
- [ ] Returns 401 Unauthorized for invalid refresh token
- [ ] Returns 401 Unauthorized for expired refresh token
- [ ] Unit tests cover success and error scenarios
- [ ] Integration test verifies token replacement

**API Specification**:
```
POST /api/v1/auth/refresh
Content-Type: application/json

Request Body:
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}

Success Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}

Error Response (401):
{
  "detail": "Invalid or expired refresh token"
}
```

**Implementation Steps**:
1. Create refresh endpoint in `api/v1/auth.py`
2. Decode and verify refresh token
3. Check token type is "refresh"
4. Query session by token JTI
5. Verify session is active and not expired
6. Generate new access token
7. Optionally generate new refresh token (rotate tokens)
8. Update session record with new JTI
9. Write tests for token rotation logic

---

## Task 1.7: Implement Logout Endpoint with Session Invalidation

**User Story**: As a user, I want to logout so my session is terminated and tokens are invalidated.

**Time Estimate**: 1 hour

**Acceptance Criteria**:
- [ ] POST `/api/v1/auth/logout` endpoint created
- [ ] Requires valid access token (authentication required)
- [ ] Marks session as revoked in database
- [ ] Sets `revoked_at` timestamp on session
- [ ] Returns 200 OK on success
- [ ] Returns 401 Unauthorized if not authenticated
- [ ] Subsequent requests with same token fail with 401
- [ ] Unit tests verify session revocation
- [ ] Integration test verifies token invalidation

**API Specification**:
```
POST /api/v1/auth/logout
Authorization: Bearer <access_token>

Success Response (200):
{
  "message": "Successfully logged out"
}
```

**Implementation Steps**:
1. Create logout endpoint in `api/v1/auth.py`
2. Require authentication with `Depends(get_current_user)`
3. Extract token JTI from current user's token
4. Query session by JTI
5. Update session: `is_revoked = True`, `revoked_at = now()`
6. Return success message
7. Write tests verifying token no longer works

---

## Task 1.8: Implement Password Reset Request Endpoint

**User Story**: As a user, I want to request a password reset so I can recover access if I forget my password.

**Time Estimate**: 2 hours

**Acceptance Criteria**:
- [ ] POST `/api/v1/auth/password-reset/request` endpoint created
- [ ] Accepts email address
- [ ] Generates password reset token (valid 1 hour)
- [ ] Stores token hash in database with expiration
- [ ] Sends reset email with token link (email service stubbed for now)
- [ ] Returns 200 OK even if email doesn't exist (security best practice)
- [ ] Rate limits requests to 3 per hour per email
- [ ] Token is single-use and expires after 1 hour
- [ ] Unit tests verify token generation
- [ ] Integration test verifies workflow

**API Specification**:
```
POST /api/v1/auth/password-reset/request
Content-Type: application/json

Request Body:
{
  "email": "user@example.com"
}

Success Response (200):
{
  "message": "If the email exists, a password reset link has been sent"
}
```

**Implementation Steps**:
1. Create password reset request endpoint
2. Generate random reset token (32 bytes, hex encoded)
3. Hash token with bcrypt before storage
4. Store hashed token with 1-hour expiration
5. Log reset request for rate limiting
6. Send email with reset link (stub for now)
7. Return generic success message
8. Write tests for token generation and expiration

**Reset Token Structure**:
- Plain token sent to user: 64-character hex string
- Hashed token stored in DB: bcrypt hash
- Expiration: 1 hour from generation
- Single-use: Deleted after successful reset

---

## Task 1.9: Implement Password Reset Confirmation Endpoint

**User Story**: As a user, I want to confirm my password reset so I can set a new password and regain access.

**Time Estimate**: 2 hours

**Acceptance Criteria**:
- [ ] POST `/api/v1/auth/password-reset/confirm` endpoint created
- [ ] Accepts reset token and new password
- [ ] Validates reset token exists and not expired
- [ ] Validates new password strength
- [ ] Hashes new password with bcrypt
- [ ] Updates user password in database
- [ ] Deletes reset token (single-use)
- [ ] Revokes all existing sessions for user
- [ ] Returns 200 OK on success
- [ ] Returns 400 Bad Request for invalid/expired token
- [ ] Unit tests verify password update
- [ ] Integration test verifies full reset workflow

**API Specification**:
```
POST /api/v1/auth/password-reset/confirm
Content-Type: application/json

Request Body:
{
  "token": "64-character-hex-string",
  "new_password": "NewSecurePass123!"
}

Success Response (200):
{
  "message": "Password successfully reset"
}

Error Response (400):
{
  "detail": "Invalid or expired reset token"
}
```

**Implementation Steps**:
1. Create password reset confirm endpoint
2. Query reset token by provided token (hash comparison)
3. Check token expiration
4. Validate new password strength
5. Hash new password with bcrypt
6. Update user password
7. Delete reset token record
8. Revoke all user sessions
9. Write comprehensive tests

---

## Task 1.10: Implement RBAC Enforcement Middleware and Decorators

**User Story**: As a developer, I need RBAC enforcement so I can restrict endpoints to specific roles.

**Time Estimate**: 2-3 hours

**Acceptance Criteria**:
- [ ] `require_role()` dependency function created
- [ ] `require_permission()` dependency function created
- [ ] Functions verify user has required role(s)
- [ ] Returns 403 Forbidden if user lacks permission
- [ ] Supports multiple role requirements (OR logic)
- [ ] Works with `get_current_user()` dependency
- [ ] Unit tests verify role checking logic
- [ ] Integration tests verify endpoint protection
- [ ] Documentation includes usage examples

**Implementation Steps**:
1. Create `require_role()` in `core/dependencies.py`
2. Accept list of allowed role names
3. Check current user's roles against allowed roles
4. Raise 403 if no role match
5. Create `require_permission()` for future permission system
6. Write tests for single role, multiple roles, no roles
7. Document usage patterns

**Usage Example**:
```python
from app.core.dependencies import get_current_user, require_role

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_role(["Admin"]))
):
    # Only admins can access this endpoint
    pass
```

---

## Task 1.11: Implement Session Management with Redis Caching

**User Story**: As a developer, I need session caching so token validation is fast and scalable.

**Time Estimate**: 2-3 hours

**Acceptance Criteria**:
- [ ] Redis connection configured in `core/database.py`
- [ ] Session data cached in Redis with 15-minute TTL
- [ ] Cache key format: `session:{token_jti}`
- [ ] `get_current_user()` checks Redis before database
- [ ] Session revocation clears Redis cache
- [ ] Cache miss falls back to database query
- [ ] Cache updates on session changes
- [ ] Unit tests verify cache operations
- [ ] Integration tests verify performance improvement

**Implementation Steps**:
1. Install `redis` and `aioredis` libraries
2. Configure Redis connection in config
3. Create Redis client in `core/database.py`
4. Modify `get_current_user()` to check Redis first
5. Cache session data after database query
6. Implement cache invalidation on logout
7. Set appropriate TTL (match access token expiry)
8. Write tests for cache hit/miss scenarios

**Cache Data Structure**:
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "roles": ["User"],
  "is_revoked": false,
  "expires_at": "2025-10-24T10:45:00Z"
}
```

---

## Task 1.12: Write Comprehensive Security Tests

**User Story**: As a developer, I need thorough security tests so I can trust the authentication system.

**Time Estimate**: 4-6 hours

**Acceptance Criteria**:
- [ ] JWT creation and verification tests (valid, expired, malformed)
- [ ] Password hashing and verification tests
- [ ] User registration tests (success, duplicate email, validation errors)
- [ ] Login tests (success, wrong password, account lockout)
- [ ] Token refresh tests (valid, expired, revoked)
- [ ] Logout tests (session revocation verification)
- [ ] Password reset tests (request, confirm, expiration)
- [ ] RBAC enforcement tests (role checking, permission denial)
- [ ] Session management tests (creation, caching, invalidation)
- [ ] Account lockout tests (failed attempts, unlock)
- [ ] Test coverage >90% for all auth code
- [ ] Integration tests for complete workflows

**Test Categories**:

1. **Unit Tests** (`tests/unit/test_security.py`):
   - Password hashing with various inputs
   - JWT token creation with different payloads
   - JWT verification with valid/invalid/expired tokens
   - Role checking logic

2. **Integration Tests** (`tests/integration/test_auth.py`):
   - Full registration workflow
   - Full login workflow
   - Token refresh workflow
   - Logout and session invalidation
   - Password reset end-to-end

3. **Security Tests** (`tests/security/test_auth_security.py`):
   - SQL injection attempts
   - XSS attack prevention
   - Brute force protection (rate limiting)
   - Session fixation prevention
   - CSRF protection (for future web forms)

**Test Execution**:
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/integration/test_auth.py -v
```

---

## Task 1.13: Generate OpenAPI Documentation for Authentication Endpoints

**User Story**: As a developer, I need API documentation so I can integrate with authentication endpoints.

**Time Estimate**: 1 hour

**Acceptance Criteria**:
- [ ] All auth endpoints include docstrings
- [ ] Request/response schemas documented with examples
- [ ] Error responses documented with status codes
- [ ] Authentication requirements specified (Bearer token)
- [ ] OpenAPI spec accessible at `/docs`
- [ ] ReDoc accessible at `/redoc`
- [ ] Schemas include field descriptions and constraints
- [ ] Examples include realistic data

**Implementation Steps**:
1. Add docstrings to all auth endpoints
2. Add descriptions to Pydantic schemas
3. Add examples to request/response models
4. Verify documentation at http://localhost:8000/docs
5. Test all endpoints from Swagger UI
6. Export OpenAPI JSON spec for external tools

**Example Documentation**:
```python
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password",
    responses={
        201: {"description": "User successfully created"},
        400: {"description": "Validation error or invalid data"},
        409: {"description": "Email or username already exists"}
    }
)
async def register(user_data: UserCreate) -> UserResponse:
    """
    Register a new user account.

    - **email**: Valid email address (unique)
    - **username**: 3-50 characters (unique)
    - **password**: Min 8 chars, 1 uppercase, 1 number, 1 special
    - **full_name**: Optional display name
    """
    pass
```

---

## Phase 1 Completion Checklist

Before proceeding to Phase 2, verify:

- [ ] All 13 tasks completed and checked off
- [ ] Test coverage >90% for authentication code
- [ ] All API endpoints documented in OpenAPI
- [ ] Database migrations applied successfully
- [ ] Redis caching functional and tested
- [ ] No security vulnerabilities in code (run `bandit -r app/`)
- [ ] Code passes linting (`flake8 app/`)
- [ ] Code passes type checking (`mypy app/`)
- [ ] Manual testing complete for all workflows
- [ ] Code reviewed and merged to main branch

**Phase 1 Deliverables**:
1. Fully functional authentication API
2. JWT token management system
3. RBAC enforcement infrastructure
4. Password reset workflow
5. Session management with Redis
6. Comprehensive test suite (90%+ coverage)
7. OpenAPI documentation

**Ready for Phase 2**: Azure integration and Zero Trust analysis implementation

---

## Common Issues and Solutions

**Issue**: Alembic migration fails with foreign key errors
- **Solution**: Ensure parent tables created before child tables, check constraint order

**Issue**: JWT tokens expire too quickly during development
- **Solution**: Increase `ACCESS_TOKEN_EXPIRE_MINUTES` in config for local dev only

**Issue**: Redis connection fails
- **Solution**: Verify Docker Compose started Redis, check REDIS_URL in .env

**Issue**: Password hashing is slow
- **Solution**: This is intentional (bcrypt with 12 rounds), do not reduce rounds

**Issue**: Tests fail with database errors
- **Solution**: Use separate test database, reset between test runs

---

**Next Phase**: [Phase 2 - MVP Azure Analysis](./phase-2-mvp.md)
