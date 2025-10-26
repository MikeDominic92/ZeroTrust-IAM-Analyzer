"""
Authentication endpoints for ZeroTrust IAM Analyzer.

This module provides authentication endpoints including registration,
login, token refresh, logout, and password reset.
"""

import uuid
from datetime import datetime, timedelta

from app.core.config import get_settings
from app.core.database import get_db
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserProfile,
    UserRegisterRequest,
    UserRegisterResponse,
)
from app.services.auth_service import get_auth_service
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from sqlalchemy.orm import Session

settings = get_settings()

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
