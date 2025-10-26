"""
Authentication dependencies for ZeroTrust IAM Analyzer.

This module provides FastAPI dependency functions for JWT token verification,
user authentication, and role-based access control enforcement.
"""

import uuid
from datetime import datetime
from typing import Optional

from app.core.config import get_settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.session import Session as SessionModel
from app.models.user import User
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session, joinedload

settings = get_settings()
logger = get_logger(__name__)

# HTTP Bearer token scheme for Authorization header extraction
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency function to get current authenticated user from JWT token.

    This function validates JWT tokens and returns the authenticated User object
    for protected endpoints. It performs the following validations:
    1. Extracts JWT token from Authorization header
    2. Verifies token signature and expiration
    3. Validates token type is "access" (not "refresh")
    4. Queries session by token JTI to verify it exists and is active
    5. Verifies session is not revoked and not expired
    6. Queries user by ID from token payload
    7. Verifies user account is active
    8. Returns User object with roles eagerly loaded

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        db: Database session dependency

    Returns:
        Authenticated User object with roles relationship loaded

    Raises:
        HTTPException 401: For any authentication failure (missing, invalid,
                          expired, or revoked token; inactive user)

    Example:
        ```python
        from fastapi import APIRouter, Depends
        from app.core.dependencies import get_current_user
        from app.models.user import User

        router = APIRouter()

        @router.get("/protected")
        async def protected_route(
            current_user: User = Depends(get_current_user)
        ):
            return {"message": f"Hello {current_user.username}"}
        ```

    Token Structure Expected:
        ```json
        {
            "sub": "user-uuid",
            "email": "user@example.com",
            "roles": ["User"],
            "jti": "token-jti-uuid",
            "type": "access",
            "exp": 1729909188
        }
        ```

    Security Notes:
        - Returns generic error messages to avoid leaking information
        - Validates both token expiration and session expiration
        - Checks session revocation for logout support
        - Requires active user account status
    """
    # Extract token from credentials
    token = credentials.credentials

    # Define credential exception for all authentication failures
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and verify JWT token
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        # Extract user ID from subject claim
        user_id_str: Optional[str] = payload.get("sub")
        if user_id_str is None:
            logger.warning("token_missing_subject")
            raise credentials_exception

        # Extract token JTI for session verification
        token_jti: Optional[str] = payload.get("jti")
        if token_jti is None:
            logger.warning("token_missing_jti")
            raise credentials_exception

        # Validate token type is "access" (reject refresh tokens)
        token_type: Optional[str] = payload.get("type")
        if token_type != "access":
            logger.warning(
                "invalid_token_type",
                token_type=token_type,
                expected="access",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Convert user ID string to UUID
        try:
            user_id = uuid.UUID(user_id_str)
        except (ValueError, AttributeError) as e:
            logger.warning("invalid_user_id_format", user_id=user_id_str, error=str(e))
            raise credentials_exception

    except JWTError as e:
        # Token decode failed (invalid signature, expired, malformed)
        logger.warning("jwt_decode_failed", error=str(e))
        raise credentials_exception

    # Query session by token JTI to verify it exists and is active
    session = db.query(SessionModel).filter(SessionModel.token_jti == token_jti).first()

    if session is None:
        logger.warning("session_not_found", token_jti=token_jti)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked session",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if session is revoked (logout)
    if session.is_revoked:
        logger.warning(
            "session_revoked",
            token_jti=token_jti,
            revoked_at=session.revoked_at,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if session has expired
    if session.expires_at < datetime.utcnow():
        logger.warning(
            "session_expired",
            token_jti=token_jti,
            expires_at=session.expires_at,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Query user by ID with roles eagerly loaded
    user = db.query(User).options(joinedload(User.roles)).filter(User.id == user_id).first()

    if user is None:
        logger.warning("user_not_found", user_id=user_id)
        raise credentials_exception

    # Verify user account is active
    if not user.is_active:
        logger.warning(
            "user_account_inactive",
            user_id=user_id,
            username=user.username,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Log successful authentication
    logger.debug(
        "user_authenticated",
        user_id=str(user.id),
        username=user.username,
        email=user.email,
    )

    return user
