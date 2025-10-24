# Phase 3 & 6: Testing, Quality Assurance, and Production Readiness

**Combined Phase Duration**: 4-6 days (full-time) or 2-3 weeks (part-time)
**Priority**: CRITICAL - Cannot deploy without comprehensive testing
**Dependencies**: Phase 2 (MVP) must be complete

---

## Phase Overview

This document combines Phase 3 (Testing and Quality Assurance) and Phase 6 (Production Readiness) as they work together to ensure the application is robust, secure, and ready for production deployment.

**Phase 3 Goals**:
- Comprehensive unit test coverage (>80%)
- Integration tests for all workflows
- End-to-end tests for user journeys
- Security testing and vulnerability scanning
- Performance testing and optimization

**Phase 6 Goals**:
- Production infrastructure deployment
- CI/CD pipeline automation
- Monitoring and alerting setup
- Security hardening and compliance
- Documentation and runbooks

---

## PART A: TESTING AND QUALITY ASSURANCE (PHASE 3)

---

## Task 3.1: Write Unit Tests for Authentication Services

**User Story**: As a developer, I need thorough authentication tests so I can trust the security implementation.

**Time Estimate**: 4-5 hours

**Acceptance Criteria**:
- [ ] 100% coverage for `services/auth_service.py`
- [ ] Tests for user registration (success, duplicate email, validation)
- [ ] Tests for login (success, wrong password, account lockout)
- [ ] Tests for JWT token creation and verification
- [ ] Tests for password hashing and verification
- [ ] Tests for session creation and management
- [ ] Tests for password reset workflow
- [ ] Tests for RBAC enforcement
- [ ] All tests pass consistently
- [ ] Test execution time <10 seconds

**Test Structure**:
```python
# tests/unit/services/test_auth_service.py

import pytest
from app.services.auth_service import AuthService

@pytest.mark.asyncio
async def test_register_user_success(db_session):
    """Test successful user registration"""
    auth_service = AuthService(db_session)
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }
    user = await auth_service.register(user_data)
    assert user.email == "test@example.com"
    assert user.password_hash != "SecurePass123!"

@pytest.mark.asyncio
async def test_register_duplicate_email(db_session):
    """Test registration with duplicate email fails"""
    auth_service = AuthService(db_session)
    # Create first user
    await auth_service.register({
        "email": "test@example.com",
        "username": "user1",
        "password": "Pass123!"
    })
    # Attempt duplicate
    with pytest.raises(ValueError, match="Email already registered"):
        await auth_service.register({
            "email": "test@example.com",
            "username": "user2",
            "password": "Pass123!"
        })

@pytest.mark.asyncio
async def test_login_success(db_session):
    """Test successful login returns JWT tokens"""
    auth_service = AuthService(db_session)
    # Register user first
    await auth_service.register({
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!"
    })
    # Login
    result = await auth_service.login("test@example.com", "SecurePass123!")
    assert "access_token" in result
    assert "refresh_token" in result
    assert result["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(db_session):
    """Test login with wrong password increments failed attempts"""
    auth_service = AuthService(db_session)
    await auth_service.register({
        "email": "test@example.com",
        "username": "testuser",
        "password": "CorrectPass123!"
    })
    with pytest.raises(ValueError, match="Invalid credentials"):
        await auth_service.login("test@example.com", "WrongPass123!")
    # Verify failed attempt increment
    user = await auth_service.get_user_by_email("test@example.com")
    assert user.failed_login_attempts == 1

@pytest.mark.asyncio
async def test_account_lockout_after_5_attempts(db_session):
    """Test account locks after 5 failed login attempts"""
    auth_service = AuthService(db_session)
    await auth_service.register({
        "email": "test@example.com",
        "username": "testuser",
        "password": "CorrectPass123!"
    })
    # Attempt 5 failed logins
    for _ in range(5):
        try:
            await auth_service.login("test@example.com", "WrongPass")
        except ValueError:
            pass
    # 6th attempt should be locked
    with pytest.raises(ValueError, match="Account locked"):
        await auth_service.login("test@example.com", "CorrectPass123!")

# Additional tests for:
# - JWT token verification
# - Token refresh
# - Logout and session revocation
# - Password reset request
# - Password reset confirmation
# - RBAC role checking
```

**Pytest Configuration** (`pytest.ini`):
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Tests that take >1 second
```

---

## Task 3.2: Write Unit Tests for Azure Integration Services

**User Story**: As a developer, I need Azure integration tests so I can validate policy fetching logic.

**Time Estimate**: 4-5 hours

**Acceptance Criteria**:
- [ ] 100% coverage for `services/azure/policies.py`
- [ ] Tests for Azure authentication
- [ ] Tests for conditional access policy fetching
- [ ] Tests for RBAC policy fetching
- [ ] Tests for policy parsing and normalization
- [ ] Tests with mocked Azure API responses
- [ ] Tests handle API errors gracefully
- [ ] Tests verify pagination handling
- [ ] Tests verify rate limiting logic

**Test Structure**:
```python
# tests/unit/services/azure/test_policies.py

import pytest
from unittest.mock import Mock, patch
from app.services.azure.policies import AzurePolicyService

@pytest.fixture
def mock_azure_credential():
    """Mock Azure credential for testing"""
    credential = Mock()
    credential.get_token.return_value = Mock(token="mock-token")
    return credential

@pytest.mark.asyncio
async def test_fetch_conditional_access_policies(mock_azure_credential):
    """Test fetching conditional access policies from Azure"""
    service = AzurePolicyService(mock_azure_credential)

    mock_response = {
        "value": [
            {
                "id": "policy-1",
                "displayName": "Require MFA for admins",
                "state": "enabled",
                "conditions": {...},
                "grantControls": {...}
            }
        ]
    }

    with patch.object(service, '_call_graph_api', return_value=mock_response):
        policies = await service.fetch_conditional_access_policies()

    assert len(policies) == 1
    assert policies[0]["id"] == "policy-1"
    assert policies[0]["state"] == "enabled"

@pytest.mark.asyncio
async def test_fetch_policies_with_pagination(mock_azure_credential):
    """Test handling paginated policy responses"""
    service = AzurePolicyService(mock_azure_credential)

    page1 = {
        "value": [{"id": "policy-1"}],
        "@odata.nextLink": "https://graph.microsoft.com/v1.0/page2"
    }
    page2 = {
        "value": [{"id": "policy-2"}]
    }

    with patch.object(service, '_call_graph_api', side_effect=[page1, page2]):
        policies = await service.fetch_conditional_access_policies()

    assert len(policies) == 2

@pytest.mark.asyncio
async def test_fetch_policies_rate_limit_retry(mock_azure_credential):
    """Test retry logic when rate limited"""
    service = AzurePolicyService(mock_azure_credential)

    rate_limit_error = Exception("Rate limit exceeded")
    success_response = {"value": [{"id": "policy-1"}]}

    with patch.object(service, '_call_graph_api',
                     side_effect=[rate_limit_error, success_response]):
        policies = await service.fetch_conditional_access_policies()

    assert len(policies) == 1

@pytest.mark.asyncio
async def test_parse_conditional_access_policy():
    """Test policy parsing and normalization"""
    from app.services.azure.parser import PolicyParser

    raw_policy = {
        "id": "policy-1",
        "displayName": "Require MFA",
        "state": "enabled",
        "conditions": {
            "applications": {"includeApplications": ["All"]},
            "users": {"includeUsers": ["All"]}
        },
        "grantControls": {
            "operator": "OR",
            "builtInControls": ["mfa"]
        }
    }

    parser = PolicyParser()
    parsed = parser.parse_conditional_access_policy(raw_policy)

    assert parsed.mfa_required == True
    assert parsed.applies_to_all_users == True
```

---

## Task 3.3: Write Unit Tests for Zero Trust Scoring Algorithms

**User Story**: As a developer, I need scoring algorithm tests so I can ensure accurate security assessments.

**Time Estimate**: 5-6 hours

**Acceptance Criteria**:
- [ ] 100% coverage for `services/scoring/zerotrust.py`
- [ ] Tests for each tenet scoring (Tenet 1-4)
- [ ] Tests for composite score calculation
- [ ] Tests with various policy combinations
- [ ] Tests for edge cases (no policies, disabled policies)
- [ ] Tests verify score ranges (0-100)
- [ ] Tests verify gap identification logic
- [ ] Tests verify score calculation accuracy

**Test Structure**:
```python
# tests/unit/services/scoring/test_zerotrust.py

import pytest
from app.services.scoring.zerotrust import ZeroTrustScorer
from app.models.policy import Policy

def test_tenet_1_perfect_score():
    """Test Tenet 1 returns 100 with ideal policies"""
    policies = [
        create_policy(mfa_enabled=True, all_users=True),
        create_policy(legacy_auth_blocked=True),
        create_policy(phishing_resistant_mfa=True)
    ]

    scorer = ZeroTrustScorer()
    result = scorer.score_tenet_1_verify_explicitly(policies)

    assert result.score == 100
    assert len(result.gaps) == 0

def test_tenet_1_no_mfa():
    """Test Tenet 1 identifies missing MFA"""
    policies = []  # No MFA policies

    scorer = ZeroTrustScorer()
    result = scorer.score_tenet_1_verify_explicitly(policies)

    assert result.score < 50
    assert "MFA not enforced" in result.gaps

def test_tenet_2_over_privileged_accounts():
    """Test Tenet 2 identifies over-privileged accounts"""
    role_assignments = [
        create_role_assignment(role="Owner", scope="subscription"),
        create_role_assignment(role="Contributor", scope="subscription"),
    ]

    scorer = ZeroTrustScorer()
    result = scorer.score_tenet_2_least_privilege(role_assignments)

    assert result.score < 70
    assert any("Owner" in gap for gap in result.gaps)

def test_composite_score_calculation():
    """Test composite score combines all tenets correctly"""
    tenet_scores = [
        TenetScore(tenet_number=1, score=80),
        TenetScore(tenet_number=2, score=60),
        TenetScore(tenet_number=3, score=90),
        TenetScore(tenet_number=4, score=70)
    ]

    scorer = ZeroTrustScorer()
    composite = scorer.calculate_composite_score(tenet_scores)

    expected = (80 + 60 + 90 + 70) / 4
    assert composite == expected

def test_score_categorization():
    """Test score categorization into risk levels"""
    scorer = ZeroTrustScorer()

    assert scorer.categorize_score(95) == "Excellent"
    assert scorer.categorize_score(82) == "Good"
    assert scorer.categorize_score(68) == "Fair"
    assert scorer.categorize_score(55) == "Poor"
    assert scorer.categorize_score(30) == "Critical"
```

---

## Task 3.4: Write Unit Tests for Recommendation Generation

**User Story**: As a developer, I need recommendation tests so I can ensure actionable security advice.

**Time Estimate**: 3-4 hours

**Acceptance Criteria**:
- [ ] 100% coverage for `services/scoring/recommendations.py`
- [ ] Tests for recommendation generation from gaps
- [ ] Tests for severity assignment
- [ ] Tests for priority ranking
- [ ] Tests for score impact calculation
- [ ] Tests verify remediation steps included
- [ ] Tests verify effort estimation

**Test Structure**:
```python
# tests/unit/services/scoring/test_recommendations.py

import pytest
from app.services.scoring.recommendations import RecommendationEngine

def test_generate_mfa_recommendation():
    """Test MFA recommendation generation"""
    gaps = ["MFA not enforced for all users"]

    engine = RecommendationEngine()
    recommendations = engine.generate_recommendations(gaps, tenet_number=1)

    assert len(recommendations) > 0
    rec = recommendations[0]
    assert rec.severity == "critical"
    assert "MFA" in rec.title
    assert rec.score_impact == 40
    assert rec.effort_hours > 0

def test_recommendation_prioritization():
    """Test recommendations are prioritized correctly"""
    gaps = [
        "MFA not enforced",
        "Sign-in frequency not set",
        "Device compliance not required"
    ]

    engine = RecommendationEngine()
    recommendations = engine.generate_recommendations(gaps, tenet_number=3)

    # Critical recommendations should come first
    assert recommendations[0].severity == "critical"
    assert recommendations[0].priority < recommendations[-1].priority

def test_recommendation_includes_remediation():
    """Test recommendations include step-by-step remediation"""
    gaps = ["Legacy authentication not blocked"]

    engine = RecommendationEngine()
    recommendations = engine.generate_recommendations(gaps, tenet_number=1)

    rec = recommendations[0]
    assert len(rec.remediation) > 100  # Detailed steps
    assert "Azure" in rec.remediation
    assert rec.azure_doc_link.startswith("https://")
```

---

## Task 3.5: Write Unit Tests for Database Models and Schemas

**User Story**: As a developer, I need model tests so I can ensure data integrity.

**Time Estimate**: 2-3 hours

**Acceptance Criteria**:
- [ ] Tests for all SQLAlchemy models
- [ ] Tests for Pydantic schema validation
- [ ] Tests for model relationships (foreign keys)
- [ ] Tests for default values and constraints
- [ ] Tests for custom model methods
- [ ] Tests verify data serialization

**Test Structure**:
```python
# tests/unit/models/test_user.py

import pytest
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

def test_user_model_creation(db_session):
    """Test User model can be created"""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.created_at is not None

def test_user_verify_password():
    """Test User.verify_password method"""
    from app.core.security import get_password_hash

    user = User(
        email="test@example.com",
        password_hash=get_password_hash("SecurePass123!")
    )

    assert user.verify_password("SecurePass123!") == True
    assert user.verify_password("WrongPass") == False

def test_user_schema_validation():
    """Test UserCreate schema validation"""
    # Valid data
    valid_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }
    schema = UserCreate(**valid_data)
    assert schema.email == "test@example.com"

    # Invalid email
    with pytest.raises(ValueError):
        UserCreate(**{**valid_data, "email": "invalid-email"})

    # Weak password
    with pytest.raises(ValueError):
        UserCreate(**{**valid_data, "password": "weak"})
```

---

## Task 3.6: Write Integration Tests for Authentication Flow

**User Story**: As a developer, I need authentication integration tests so I can validate end-to-end workflows.

**Time Estimate**: 3-4 hours

**Acceptance Criteria**:
- [ ] Test full registration → login → access protected endpoint flow
- [ ] Test token refresh workflow
- [ ] Test logout and session invalidation
- [ ] Test password reset workflow
- [ ] Test RBAC enforcement on protected endpoints
- [ ] Tests use real database (test DB)
- [ ] Tests clean up data after execution

**Test Structure**:
```python
# tests/integration/test_auth_flow.py

import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_full_auth_flow(test_db):
    """Test complete authentication flow"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Register
        register_response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
            "full_name": "Test User"
        })
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]

        # 2. Login
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        })
        assert login_response.status_code == 200
        tokens = login_response.json()
        access_token = tokens["access_token"]

        # 3. Access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = await client.get("/api/v1/users/me", headers=headers)
        assert profile_response.status_code == 200
        assert profile_response.json()["id"] == user_id

@pytest.mark.asyncio
async def test_token_refresh_flow(test_db):
    """Test token refresh workflow"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!"
        })
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        })
        tokens = login_response.json()
        refresh_token = tokens["refresh_token"]

        # Refresh token
        refresh_response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert new_tokens["access_token"] != tokens["access_token"]

@pytest.mark.asyncio
async def test_password_reset_flow(test_db):
    """Test password reset workflow"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user
        await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "OldPass123!"
        })

        # Request password reset
        reset_request = await client.post("/api/v1/auth/password-reset/request",
                                         json={"email": "test@example.com"})
        assert reset_request.status_code == 200

        # Get reset token (from database in test)
        reset_token = "mock-reset-token"  # Retrieved from test DB

        # Confirm password reset
        reset_confirm = await client.post("/api/v1/auth/password-reset/confirm", json={
            "token": reset_token,
            "new_password": "NewPass123!"
        })
        assert reset_confirm.status_code == 200

        # Login with new password
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "NewPass123!"
        })
        assert login_response.status_code == 200
```

---

## Task 3.7: Write Integration Tests for Azure API Connections

**User Story**: As a developer, I need Azure integration tests so I can validate cloud connectivity.

**Time Estimate**: 3-4 hours

**Acceptance Criteria**:
- [ ] Test credential storage and retrieval
- [ ] Test Azure connection validation
- [ ] Test policy fetching from real Azure tenant (optional, uses mocks by default)
- [ ] Tests handle API errors gracefully
- [ ] Tests verify retry logic
- [ ] Tests use test Azure credentials when available

**Test Structure**:
```python
# tests/integration/test_azure_integration.py

import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_azure_credential_management(test_db, auth_headers):
    """Test Azure credential CRUD operations"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Add credential
        create_response = await client.post("/api/v1/credentials/azure",
            headers=auth_headers,
            json={
                "name": "Test Azure Tenant",
                "tenant_id": "test-tenant-id",
                "client_id": "test-client-id",
                "client_secret": "test-secret"
            }
        )
        assert create_response.status_code == 201
        credential_id = create_response.json()["id"]

        # Validate credential
        validate_response = await client.post(
            f"/api/v1/credentials/{credential_id}/validate",
            headers=auth_headers
        )
        # Note: Will fail with test credentials, that's expected
        assert validate_response.status_code in [200, 400]

        # List credentials
        list_response = await client.get("/api/v1/credentials",
                                        headers=auth_headers)
        assert list_response.status_code == 200
        assert len(list_response.json()) >= 1

        # Delete credential
        delete_response = await client.delete(
            f"/api/v1/credentials/{credential_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 204
```

---

## Task 3.8: Write Integration Tests for Scan Execution Workflow

**User Story**: As a developer, I need scan integration tests so I can validate the complete analysis workflow.

**Time Estimate**: 4-5 hours

**Acceptance Criteria**:
- [ ] Test full scan execution from start to finish
- [ ] Test scan status updates
- [ ] Test scan results retrieval
- [ ] Test scan history
- [ ] Tests use mocked Azure responses
- [ ] Tests verify database state changes
- [ ] Tests handle scan failures gracefully

**Test Structure**:
```python
# tests/integration/test_scan_workflow.py

import pytest
from httpx import AsyncClient
from unittest.mock import patch
from app.main import app

@pytest.mark.asyncio
async def test_full_scan_workflow(test_db, auth_headers, test_credential):
    """Test complete scan execution workflow"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Mock Azure policy responses
        mock_policies = [
            {
                "id": "policy-1",
                "displayName": "Require MFA",
                "state": "enabled",
                "conditions": {...},
                "grantControls": {"builtInControls": ["mfa"]}
            }
        ]

        with patch('app.services.azure.policies.AzurePolicyService.fetch_policies',
                  return_value=mock_policies):
            # Initiate scan
            scan_response = await client.post("/api/v1/scans",
                headers=auth_headers,
                json={
                    "credential_id": test_credential.id,
                    "scan_type": "full"
                }
            )
            assert scan_response.status_code == 202
            scan_id = scan_response.json()["scan_id"]

            # Wait for scan completion (in test, runs synchronously)
            result_response = await client.get(f"/api/v1/scans/{scan_id}",
                                              headers=auth_headers)
            assert result_response.status_code == 200

            result = result_response.json()
            assert result["status"] == "completed"
            assert result["overall_score"] >= 0
            assert result["overall_score"] <= 100
            assert len(result["tenet_scores"]) == 4
            assert len(result["recommendations"]) > 0

@pytest.mark.asyncio
async def test_scan_history(test_db, auth_headers, test_credential):
    """Test scan history retrieval"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Run multiple scans
        scan_ids = []
        for i in range(3):
            scan_response = await client.post("/api/v1/scans",
                headers=auth_headers,
                json={"credential_id": test_credential.id, "scan_type": "quick"}
            )
            scan_ids.append(scan_response.json()["scan_id"])

        # Get scan history
        history_response = await client.get("/api/v1/scans",
                                           headers=auth_headers)
        assert history_response.status_code == 200
        assert len(history_response.json()) >= 3
```

---

## Task 3.9: Write Integration Tests for Dashboard Endpoints

**User Story**: As a developer, I need dashboard integration tests so I can validate aggregated data display.

**Time Estimate**: 2-3 hours

**Acceptance Criteria**:
- [ ] Test dashboard overview endpoint
- [ ] Test recommendations endpoint with filters
- [ ] Test score trends endpoint
- [ ] Tests verify data aggregation logic
- [ ] Tests verify filtering and sorting

---

## Task 3.10: Set Up Playwright for E2E Testing

**User Story**: As a QA engineer, I need E2E testing tools so I can test the complete user experience.

**Time Estimate**: 2-3 hours

**Acceptance Criteria**:
- [ ] Playwright installed and configured
- [ ] Test browser automation working
- [ ] Screenshot capture on test failure
- [ ] Video recording for debugging
- [ ] Parallel test execution configured
- [ ] CI/CD integration ready

**Installation**:
```bash
npm install -D @playwright/test
npx playwright install
```

**Configuration** (`playwright.config.ts`):
```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  retries: 2,
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
    { name: 'firefox', use: { browserName: 'firefox' } },
  ],
});
```

---

## Task 3.11: Write E2E Tests for Complete User Workflow

**User Story**: As a QA engineer, I need E2E tests so I can validate the complete user journey.

**Time Estimate**: 5-6 hours

**Acceptance Criteria**:
- [ ] Test user registration and login via UI
- [ ] Test Azure credential addition via UI
- [ ] Test scan initiation and results viewing via UI
- [ ] Test dashboard navigation
- [ ] Test recommendations filtering
- [ ] Tests run in multiple browsers
- [ ] Tests capture screenshots on failure

**Test Structure**:
```typescript
// tests/e2e/user-journey.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Complete User Journey', () => {
  test('user can register, add credentials, and run scan', async ({ page }) => {
    // Navigate to app
    await page.goto('/');

    // Register
    await page.click('text=Sign Up');
    await page.fill('input[name=email]', 'test@example.com');
    await page.fill('input[name=username]', 'testuser');
    await page.fill('input[name=password]', 'SecurePass123!');
    await page.click('button[type=submit]');

    // Verify redirected to dashboard
    await expect(page).toHaveURL('/dashboard');

    // Add Azure credential
    await page.click('text=Add Credential');
    await page.selectOption('select[name=provider]', 'azure');
    await page.fill('input[name=name]', 'Test Tenant');
    await page.fill('input[name=tenant_id]', 'test-tenant-id');
    await page.fill('input[name=client_id]', 'test-client-id');
    await page.fill('input[name=client_secret]', 'test-secret');
    await page.click('button[type=submit]');

    // Verify credential added
    await expect(page.locator('text=Test Tenant')).toBeVisible();

    // Initiate scan
    await page.click('text=Run Scan');
    await page.selectOption('select[name=credential]', 'Test Tenant');
    await page.click('button:has-text("Start Scan")');

    // Wait for scan completion (mock in E2E)
    await expect(page.locator('text=Scan Complete')).toBeVisible({ timeout: 10000 });

    // View results
    await expect(page.locator('text=Zero Trust Score')).toBeVisible();
    await expect(page.locator('[data-testid=overall-score]')).toContainText(/\d+/);
  });

  test('user can filter recommendations by severity', async ({ page }) => {
    // Login first (using helper function)
    await loginAsTestUser(page);

    // Navigate to recommendations
    await page.click('text=Recommendations');

    // Filter by critical
    await page.selectOption('select[name=severity]', 'critical');

    // Verify only critical recommendations shown
    const recommendations = await page.locator('[data-testid=recommendation-card]').all();
    for (const rec of recommendations) {
      await expect(rec.locator('.severity-badge')).toHaveText('Critical');
    }
  });
});
```

---

## Task 3.12: Configure Test Coverage Reporting

**User Story**: As a developer, I need coverage reporting so I can ensure thorough testing.

**Time Estimate**: 1-2 hours

**Acceptance Criteria**:
- [ ] Coverage tracking configured for backend (pytest-cov)
- [ ] Coverage tracking configured for frontend (Jest)
- [ ] Coverage reports generated in HTML and JSON
- [ ] Coverage thresholds enforced (80% minimum)
- [ ] Coverage reports uploaded to CI/CD
- [ ] Coverage badges added to README

**Backend Configuration** (`.coveragerc`):
```ini
[run]
source = app
omit =
    */tests/*
    */migrations/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:

[html]
directory = htmlcov
```

**Run Coverage**:
```bash
# Backend
pytest --cov=app --cov-report=html --cov-report=term --cov-fail-under=80

# Frontend
npm test -- --coverage --coverageReporters=html --coverageReporters=text
```

---

## PART B: PRODUCTION READINESS (PHASE 6)

---

## Task 6.1: Configure GCP Cloud Run Deployment for Backend

**User Story**: As a DevOps engineer, I need backend deployment automation so the app can run in production.

**Time Estimate**: 4-5 hours

**Acceptance Criteria**:
- [ ] Cloud Run service created for backend
- [ ] Dockerfile optimized for production (multi-stage build)
- [ ] Environment variables configured via Secret Manager
- [ ] Cloud SQL connection configured
- [ ] Memorystore Redis connection configured
- [ ] Auto-scaling configured (min 1, max 10 instances)
- [ ] Health check endpoints implemented
- [ ] Deployment script created

**Dockerfile** (Production-optimized):
```dockerfile
# backend/Dockerfile.prod

FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Deployment Script** (`scripts/deployment/deploy-backend.sh`):
```bash
#!/bin/bash
set -e

PROJECT_ID="zerotrust-iam-analyzer"
REGION="us-central1"
SERVICE_NAME="iam-analyzer-backend"

echo "Building container..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="ENVIRONMENT=production" \
  --set-secrets="DATABASE_URL=database-url:latest,SECRET_KEY=jwt-secret:latest" \
  --add-cloudsql-instances=$PROJECT_ID:$REGION:iam-analyzer-db \
  --vpc-connector=iam-analyzer-vpc \
  --min-instances=1 \
  --max-instances=10 \
  --cpu=1 \
  --memory=2Gi \
  --timeout=60s

echo "Deployment complete!"
```

---

## Task 6.2: Configure GCP Cloud Run Deployment for Frontend

**User Story**: As a DevOps engineer, I need frontend deployment automation so users can access the UI.

**Time Estimate**: 3-4 hours

**Acceptance Criteria**:
- [ ] Cloud Run service created for frontend
- [ ] Nginx configured for serving React build
- [ ] Environment variables for API endpoint configured
- [ ] HTTPS enforced
- [ ] Custom domain configured (optional)
- [ ] CDN caching enabled
- [ ] Deployment script created

**Dockerfile** (Frontend):
```dockerfile
# frontend/Dockerfile.prod

FROM node:20-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass https://backend-service-url;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Task 6.3: Set Up Cloud SQL PostgreSQL Instance

**User Story**: As a DevOps engineer, I need managed database so data is persistent and backed up.

**Time Estimate**: 2-3 hours

**Acceptance Criteria**:
- [ ] Cloud SQL instance created
- [ ] PostgreSQL 15 configured
- [ ] Automated backups enabled (daily)
- [ ] High availability configured
- [ ] Private IP configured for security
- [ ] Connection from Cloud Run verified
- [ ] Database migrations applied

**Setup Script**:
```bash
#!/bin/bash
set -e

PROJECT_ID="zerotrust-iam-analyzer"
REGION="us-central1"
INSTANCE_NAME="iam-analyzer-db"

echo "Creating Cloud SQL instance..."
gcloud sql instances create $INSTANCE_NAME \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=$REGION \
  --network=default \
  --no-assign-ip \
  --backup \
  --backup-start-time=03:00 \
  --enable-bin-log \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=04

echo "Creating database..."
gcloud sql databases create iam_analyzer --instance=$INSTANCE_NAME

echo "Creating user..."
gcloud sql users create iam_user \
  --instance=$INSTANCE_NAME \
  --password=$(openssl rand -base64 32)

echo "Cloud SQL setup complete!"
```

---

## Task 6.4: Set Up Memorystore Redis Instance

**User Story**: As a DevOps engineer, I need managed Redis so session caching is fast and reliable.

**Time Estimate**: 1-2 hours

**Acceptance Criteria**:
- [ ] Memorystore Redis instance created
- [ ] High availability configured
- [ ] VPC connection configured
- [ ] Connection from Cloud Run verified
- [ ] Redis caching tested in production

**Setup Script**:
```bash
#!/bin/bash
set -e

PROJECT_ID="zerotrust-iam-analyzer"
REGION="us-central1"
INSTANCE_NAME="iam-analyzer-redis"

echo "Creating Memorystore Redis instance..."
gcloud redis instances create $INSTANCE_NAME \
  --size=1 \
  --region=$REGION \
  --redis-version=redis_7_0 \
  --tier=standard-ha \
  --network=default

echo "Redis setup complete!"
```

---

## Task 6.5: Configure Secret Manager for Credential Storage

**User Story**: As a security engineer, I need secrets management so credentials are stored securely.

**Time Estimate**: 2 hours

**Acceptance Criteria**:
- [ ] Secret Manager enabled
- [ ] Secrets created for all sensitive values
- [ ] Cloud Run service accounts granted access
- [ ] Secrets rotation policy configured
- [ ] Audit logging enabled

**Setup Script**:
```bash
#!/bin/bash
set -e

PROJECT_ID="zerotrust-iam-analyzer"

echo "Creating secrets..."
echo -n "your-secret-key" | gcloud secrets create jwt-secret --data-file=-
echo -n "postgresql://user:pass@host/db" | gcloud secrets create database-url --data-file=-

echo "Granting access to Cloud Run service account..."
SERVICE_ACCOUNT="iam-analyzer-backend@$PROJECT_ID.iam.gserviceaccount.com"
gcloud secrets add-iam-policy-binding jwt-secret \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"

echo "Secret Manager setup complete!"
```

---

## Task 6.6: Implement CI/CD Pipeline with GitHub Actions

**User Story**: As a developer, I need automated deployment so changes go live safely.

**Time Estimate**: 4-5 hours

**Acceptance Criteria**:
- [ ] GitHub Actions workflow created
- [ ] Runs tests on all PRs
- [ ] Deploys to production on main branch merge
- [ ] Includes deployment approval gate
- [ ] Sends notifications on failures
- [ ] Includes rollback capability

**GitHub Actions Workflow** (`.github/workflows/deploy.yml`):
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage

  deploy-production:
    needs: [test-backend, test-frontend]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3
      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      - name: Deploy backend
        run: ./scripts/deployment/deploy-backend.sh
      - name: Deploy frontend
        run: ./scripts/deployment/deploy-frontend.sh
      - name: Run smoke tests
        run: ./scripts/deployment/smoke-tests.sh
```

---

## Task 6.7: Configure Cloud Monitoring and Alerting

**User Story**: As an SRE, I need monitoring so I can detect and respond to issues quickly.

**Time Estimate**: 3-4 hours

**Acceptance Criteria**:
- [ ] Cloud Monitoring dashboards created
- [ ] Uptime checks configured
- [ ] Error rate alerts configured
- [ ] Latency alerts configured
- [ ] Resource utilization alerts configured
- [ ] Log-based metrics configured
- [ ] Alert notifications to email/Slack

**Monitoring Configuration**:
```yaml
# monitoring/alerts.yaml

alertPolicies:
  - displayName: "High Error Rate"
    conditions:
      - displayName: "Error rate > 5%"
        conditionThreshold:
          filter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.label.response_code_class="5xx"'
          comparison: COMPARISON_GT
          thresholdValue: 0.05
    notificationChannels:
      - email-notifications

  - displayName: "High Response Time"
    conditions:
      - displayName: "P95 latency > 2s"
        conditionThreshold:
          filter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_latencies"'
          aggregations:
            - alignmentPeriod: 60s
              perSeriesAligner: ALIGN_PERCENTILE_95
          comparison: COMPARISON_GT
          thresholdValue: 2000
```

---

## Task 6.8: Create Production Deployment Runbook and Documentation

**User Story**: As a team member, I need deployment documentation so I can deploy safely and respond to incidents.

**Time Estimate**: 3-4 hours

**Acceptance Criteria**:
- [ ] Deployment runbook created
- [ ] Rollback procedures documented
- [ ] Incident response guide created
- [ ] Architecture diagram updated
- [ ] API documentation complete
- [ ] Troubleshooting guide written

**Runbook Structure** (`docs/deployment/production-runbook.md`):
```markdown
# Production Deployment Runbook

## Pre-Deployment Checklist
- [ ] All tests passing in CI/CD
- [ ] Code review approved
- [ ] Database migrations reviewed
- [ ] Secrets updated if needed
- [ ] Monitoring dashboards verified

## Deployment Steps
1. Merge PR to main branch
2. GitHub Actions automatically builds and deploys
3. Monitor deployment progress in GCP Console
4. Run smoke tests: `./scripts/deployment/smoke-tests.sh`
5. Monitor error rates for 15 minutes

## Rollback Procedure
If issues detected:
1. Revert to previous Cloud Run revision:
   ```bash
   gcloud run services update-traffic iam-analyzer-backend \
     --to-revisions=iam-analyzer-backend-v123=100
   ```
2. Revert database migrations if applied:
   ```bash
   alembic downgrade -1
   ```
3. Notify team in #incidents Slack channel

## Smoke Tests
- Health check: `curl https://api.example.com/health`
- Auth flow: Test login via UI
- Scan execution: Run quick scan and verify results

## Monitoring
- Errors: https://console.cloud.google.com/logs/query
- Metrics: https://console.cloud.google.com/monitoring/dashboards
- Uptime: https://console.cloud.google.com/monitoring/uptime

## Incident Response
1. Check logs for error messages
2. Check Cloud Run metrics for resource issues
3. Check Cloud SQL performance
4. Review recent deployments in GitHub Actions
5. If critical, rollback immediately
6. Post-incident: Write postmortem
```

---

## Phase 3 & 6 Completion Checklist

Before declaring production-ready, verify:

- [ ] Test coverage >80% for backend
- [ ] Test coverage >70% for frontend
- [ ] All integration tests passing
- [ ] E2E tests passing in multiple browsers
- [ ] Security scan completed (no high/critical vulnerabilities)
- [ ] Performance testing completed (load testing)
- [ ] Production infrastructure deployed
- [ ] CI/CD pipeline functional
- [ ] Monitoring and alerting operational
- [ ] Secrets managed securely
- [ ] Backup and recovery tested
- [ ] Documentation complete (runbooks, API docs, architecture)
- [ ] Incident response procedures documented

**Deliverables**:
1. Comprehensive test suite (unit, integration, E2E)
2. Production-ready infrastructure on GCP
3. Automated CI/CD pipeline
4. Monitoring and alerting system
5. Security hardening implemented
6. Complete documentation and runbooks

---

**Production Launch Ready!**

The application is now fully tested, deployed, monitored, and documented for production use.
