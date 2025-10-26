"""
Authentication endpoints for ZeroTrust IAM Analyzer.

This module provides authentication endpoints including registration,
login, token refresh, logout, and password reset.
"""

import uuid
from datetime import datetime, timedelta

from app.core.config import get_settings
from app.core.database import get_db
from app.core.dependencies import get_current_session
from app.core.logging import get_logger
from app.schemas.auth import (
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserProfile,
    UserRegisterRequest,
    UserRegisterResponse,
)
from app.models.session import Session as SessionModel
from app.services.auth_service import get_auth_service
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

settings = get_settings()
logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password",
    responses={
        201: {"description": "User successfully created"},
        400: {"description": "Validation error or invalid data"},
        409: {"description": "Email or username already exists"},
    },
)
async def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> UserRegisterResponse:
    """
    Register a new user account.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user information

    Raises:
        HTTPException 400: If email or username already exists
        HTTPException 400: If validation fails

    Example:
        Request:
        ```json
        {
            "email": "analyst@example.com",
            "username": "security_analyst",
            "password": "SecurePass123!",
            "first_name": "Jane",
            "last_name": "Doe"
        }
        ```

        Response (201):
        ```json
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "analyst@example.com",
            "username": "security_analyst",
            "status": "pending_verification",
            "is_verified": false,
            "created_at": "2025-10-25T12:00:00Z"
        }
        ```
    """
    # Get auth service
    auth_service = get_auth_service(db)

    # Register user
    try:
        new_user = auth_service.register_user(user_data)

        # Return response
        return UserRegisterResponse(
            id=str(new_user.id),
            email=new_user.email,
            username=new_user.username,
            status=new_user.status.value,
            is_verified=new_user.is_verified,
            created_at=new_user.created_at,
        )
    except HTTPException:
        # Re-raise HTTP exceptions from service layer
        raise
    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {str(e)}",
        )


@router.post(
    "/login",
    response_model=UserLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user credentials and return JWT access and refresh tokens",
    responses={
        200: {"description": "Login successful, tokens returned"},
        401: {"description": "Invalid credentials (wrong username/password)"},
        403: {"description": "Account locked or inactive"},
    },
)
async def login(
    credentials: UserLoginRequest,
    db: Session = Depends(get_db),
) -> UserLoginResponse:
    """
    User login endpoint.

    Authenticates user credentials and returns JWT access and refresh tokens.
    Creates session record for token tracking and revocation support.

    Args:
        credentials: Login credentials (username/email and password)
        db: Database session

    Returns:
        User profile and JWT token pair

    Raises:
        HTTPException 401: Invalid credentials
        HTTPException 403: Account locked or inactive

    Example:
        Request:
        ```json
        {
            "username": "security_analyst",
            "password": "SecurePass123!"
        }
        ```

        Response (200):
        ```json
        {
            "user": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "analyst@example.com",
                "username": "security_analyst",
                "role": "analyst",
                "is_active": true
            },
            "tokens": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }
        ```
    """
    auth_service = get_auth_service(db)

    try:
        # Authenticate user (handles failed attempts and lockout)
        user = auth_service.authenticate_user(
            username_or_email=credentials.username,
            password=credentials.password,
            ip_address=None,  # TODO: Extract from request.client.host in future
        )

        # Generate unique JTI for both tokens
        access_token_jti = str(uuid.uuid4())
        refresh_token_jti = str(uuid.uuid4())

        # Calculate token expiration times
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token_exp_time = datetime.utcnow() + access_token_expires
        refresh_token_exp_time = datetime.utcnow() + timedelta(days=7)

        # Create access token with full payload
        access_token_payload = {
            "sub": str(user.id),
            "email": user.email,
            "roles": [role.name for role in user.roles],
            "jti": access_token_jti,
            "type": "access",
            "exp": int(access_token_exp_time.timestamp()),
        }
        access_token = jwt.encode(
            access_token_payload,
            settings.secret_key,
            algorithm=settings.algorithm,
        )

        # Create refresh token with minimal payload
        refresh_token_payload = {
            "sub": str(user.id),
            "jti": refresh_token_jti,
            "type": "refresh",
            "exp": int(refresh_token_exp_time.timestamp()),
        }
        refresh_token = jwt.encode(
            refresh_token_payload,
            settings.secret_key,
            algorithm=settings.algorithm,
        )

        # Create session record in database
        auth_service.create_session(
            user=user,
            access_token_jti=access_token_jti,
            refresh_token_jti=refresh_token_jti,
            expires_at=access_token_exp_time,
            ip_address=None,  # TODO: Extract from request
            user_agent=None,  # TODO: Extract from request headers
        )

        # Return user profile and tokens
        return UserLoginResponse(
            user=UserProfile(
                id=str(user.id),
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                first_name=user.first_name,
                last_name=user.last_name,
                display_name=user.display_name,
                role=user.role.value,
                status=user.status.value,
                is_active=user.is_active,
                is_verified=user.is_verified,
                last_login_at=user.last_login_at,
                created_at=user.created_at,
            ),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=int(access_token_expires.total_seconds()),
            ),
        )

    except HTTPException:
        # Re-raise HTTP exceptions from service layer (401, 403)
        raise
    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}",
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Generate new access and refresh tokens using valid refresh token",
    responses={
        200: {"description": "Tokens refreshed successfully"},
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def refresh_token(
    refresh_request: TokenRefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Refresh access token using valid refresh token.

    This endpoint implements token rotation for enhanced security:
    - Validates the provided refresh token
    - Generates a NEW access token (30-minute expiry)
    - Generates a NEW refresh token (7-day expiry)
    - Updates the session record with new token JTIs
    - Invalidates the old refresh token (single-use)

    Args:
        refresh_request: Refresh token request containing refresh_token
        db: Database session

    Returns:
        New token pair (access + refresh tokens)

    Raises:
        HTTPException 401: For any refresh token validation failure

    Example:
        Request:
        ```json
        {
            "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
        }
        ```

        Response (200):
        ```json
        {
            "access_token": "eyJhbGciOiJIUzI1NiIs...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
            "token_type": "bearer",
            "expires_in": 1800
        }
        ```

    Security Notes:
        - Token rotation: Each refresh generates new tokens, old ones invalidated
        - Single-use tokens: Prevents token replay attacks
        - Session validation: Verifies session is not revoked or expired
        - Generic error messages: Avoids leaking information about token validity
    """
    # Define credential exception for all authentication failures
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and verify refresh token
        payload = jwt.decode(
            refresh_request.refresh_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        # Extract user ID from subject claim
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception

        # Extract refresh token JTI for session lookup
        refresh_token_jti = payload.get("jti")
        if refresh_token_jti is None:
            raise credentials_exception

        # Validate token type is "refresh" (reject access tokens)
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Convert user ID to UUID
        try:
            user_id = uuid.UUID(user_id_str)
        except (ValueError, AttributeError):
            raise credentials_exception

    except JWTError:
        # Token decode failed (invalid signature, expired, malformed)
        raise credentials_exception

    # Query session by refresh_token_jti (NOT token_jti which is for access tokens)
    session = (
        db.query(SessionModel)
        .filter(SessionModel.refresh_token_jti == refresh_token_jti)
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked session",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if session is revoked
    if session.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if session has expired
    if session.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Query user to include in new access token payload
    auth_service = get_auth_service(db)
    user = auth_service.get_user_by_id(user_id)

    if user is None:
        raise credentials_exception

    # Verify user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate NEW token JTIs for rotation (old tokens become invalid)
    new_access_token_jti = str(uuid.uuid4())
    new_refresh_token_jti = str(uuid.uuid4())

    # Calculate token expiration times
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token_exp_time = datetime.utcnow() + access_token_expires
    refresh_token_exp_time = datetime.utcnow() + timedelta(days=7)

    # Create new access token with full payload
    access_token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "roles": [role.name for role in user.roles],
        "jti": new_access_token_jti,
        "type": "access",
        "exp": int(access_token_exp_time.timestamp()),
    }
    new_access_token = jwt.encode(
        access_token_payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    # Create new refresh token with minimal payload (rotation)
    refresh_token_payload = {
        "sub": str(user.id),
        "jti": new_refresh_token_jti,
        "type": "refresh",
        "exp": int(refresh_token_exp_time.timestamp()),
    }
    new_refresh_token = jwt.encode(
        refresh_token_payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    # Update session with new token JTIs (invalidates old tokens)
    session.token_jti = new_access_token_jti
    session.refresh_token_jti = new_refresh_token_jti
    session.expires_at = access_token_exp_time
    session.last_activity_at = datetime.utcnow()
    db.commit()

    # Return new token pair
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Logout user and invalidate current session",
    responses={
        200: {"description": "Successfully logged out"},
        401: {"description": "Not authenticated or invalid token"},
    },
)
async def logout(
    session: SessionModel = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> dict:
    """
    Logout user and invalidate current session.

    This endpoint revokes the current session, making the access token
    and refresh token pair invalid for future requests. The user must
    login again to obtain new tokens.

    Args:
        session: Current active session from get_current_session dependency
        db: Database session

    Returns:
        Success message confirming logout

    Raises:
        HTTPException 401: If not authenticated or token is invalid

    Example:
        Request:
        ```
        POST /api/v1/auth/logout
        Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
        ```

        Response (200):
        ```json
        {
            "message": "Successfully logged out"
        }
        ```

    Security Notes:
        - Requires valid access token (authentication required)
        - Session is immediately revoked in database
        - Both access and refresh tokens become invalid
        - Subsequent requests with same tokens will fail with 401
        - Session revocation is permanent and cannot be undone
    """
    # Revoke the session (sets is_revoked=True, revoked_at=now())
    session.revoke()
    db.commit()

    # Log successful logout
    logger.info(
        "user_logged_out",
        session_id=str(session.id),
        user_id=str(session.user_id),
    )

    return {"message": "Successfully logged out"}
