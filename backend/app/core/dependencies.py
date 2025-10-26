"""
Authentication dependencies for ZeroTrust IAM Analyzer.

This module provides FastAPI dependency functions for JWT token verification,
user authentication, and role-based access control enforcement.
"""

import json
import uuid
from datetime import datetime
from typing import List, Optional

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


def get_current_session(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> SessionModel:
    """
    Dependency function to get current active session from JWT token.

    This function validates JWT tokens and returns the active Session object.
    Useful for endpoints that need to modify session state (e.g., logout).

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        db: Database session dependency

    Returns:
        Active Session object

    Raises:
        HTTPException 401: For any session validation failure

    Example:
        ```python
        from fastapi import APIRouter, Depends
        from app.core.dependencies import get_current_session
        from app.models.session import Session

        router = APIRouter()

        @router.post("/logout")
        async def logout(
            session: Session = Depends(get_current_session)
        ):
            session.revoke()
            return {"message": "Logged out"}
        ```
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

        # Extract token JTI for session lookup
        token_jti: Optional[str] = payload.get("jti")
        if token_jti is None:
            logger.warning("token_missing_jti")
            raise credentials_exception

        # Validate token type is "access" (reject refresh tokens)
        token_type: Optional[str] = payload.get("type")
        if token_type != "access":
            logger.warning(
                "invalid_token_type_for_session",
                token_type=token_type,
                expected="access",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWTError as e:
        # Token decode failed (invalid signature, expired, malformed)
        logger.warning("jwt_decode_failed_for_session", error=str(e))
        raise credentials_exception

    # Query session by token JTI
    session = db.query(SessionModel).filter(SessionModel.token_jti == token_jti).first()

    if session is None:
        logger.warning("session_not_found", token_jti=token_jti)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked session",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if session is revoked
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

    # Log successful session retrieval
    logger.debug(
        "session_retrieved",
        session_id=str(session.id),
        token_jti=token_jti,
    )

    return session


def require_role(allowed_roles: List[str]):
    """
    Dependency factory for role-based access control (RBAC).

    Returns a dependency function that verifies the current user has at least
    one of the specified roles. Raises 403 Forbidden if user lacks all roles.

    This factory pattern allows flexible role requirements per endpoint using
    FastAPI's dependency injection system. Multiple roles use OR logic - any
    matching role grants access.

    Args:
        allowed_roles: List of role names that grant access (e.g., ["Admin", "Manager"])

    Returns:
        Dependency function that performs role checking

    Raises:
        HTTPException 403: If user has none of the allowed roles

    Example:
        ```python
        from fastapi import APIRouter, Depends
        from app.core.dependencies import get_current_user, require_role
        from app.models.user import User

        router = APIRouter()

        # Single role requirement
        @router.delete("/users/{user_id}")
        async def delete_user(
            user_id: str,
            current_user: User = Depends(get_current_user),
            _: None = Depends(require_role(["Admin"]))
        ):
            # Only admins can delete users
            pass

        # Multiple role requirement (OR logic)
        @router.post("/policies")
        async def create_policy(
            policy_data: dict,
            current_user: User = Depends(get_current_user),
            _: None = Depends(require_role(["Admin", "PolicyManager"]))
        ):
            # Admins OR PolicyManagers can create policies
            pass
        ```

    Notes:
        - Role names are case-sensitive
        - Only active roles are checked (role.is_active == True)
        - User must be authenticated (requires get_current_user dependency)
        - Access granted if user has ANY of the allowed roles (OR logic)
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> None:
        """Inner dependency that performs the actual role checking."""
        # Extract active role names from user's roles
        user_role_names = [role.name for role in current_user.roles if role.is_active]

        # Check if user has any of the allowed roles (OR logic)
        has_required_role = any(role_name in allowed_roles for role_name in user_role_names)

        if not has_required_role:
            # User lacks all required roles - deny access
            logger.warning(
                "rbac_access_denied_insufficient_role",
                user_id=str(current_user.id),
                username=current_user.username,
                user_roles=user_role_names,
                required_roles=allowed_roles,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(allowed_roles)}",
            )

        # User has at least one required role - grant access
        matched_role = next(r for r in user_role_names if r in allowed_roles)
        logger.info(
            "rbac_access_granted",
            user_id=str(current_user.id),
            username=current_user.username,
            matched_role=matched_role,
            required_roles=allowed_roles,
        )

    return role_checker


def require_permission(required_permissions: List[str]):
    """
    Dependency factory for permission-based access control.

    Returns a dependency function that verifies the current user has at least
    one of the specified permissions across all their active roles. Permissions
    are stored as JSON arrays in the Role.permissions field.

    This provides granular access control beyond role-based checks, allowing
    fine-grained permission management. Multiple permissions use OR logic - any
    matching permission grants access.

    Args:
        required_permissions: List of permission strings (e.g., ["policy.create", "policy.admin"])

    Returns:
        Dependency function that performs permission checking

    Raises:
        HTTPException 403: If user has none of the required permissions

    Example:
        ```python
        from fastapi import APIRouter, Depends
        from app.core.dependencies import get_current_user, require_permission
        from app.models.user import User

        router = APIRouter()

        # Single permission requirement
        @router.post("/scans")
        async def initiate_scan(
            scan_data: dict,
            current_user: User = Depends(get_current_user),
            _: None = Depends(require_permission(["scan.create"]))
        ):
            # Users with scan.create permission can initiate scans
            pass

        # Multiple permission requirement (OR logic)
        @router.put("/policies/{policy_id}")
        async def update_policy(
            policy_id: str,
            policy_data: dict,
            current_user: User = Depends(get_current_user),
            _: None = Depends(require_permission(["policy.update", "policy.admin"]))
        ):
            # Users with policy.update OR policy.admin can update policies
            pass
        ```

    Permission Format:
        Permissions are stored in Role.permissions as JSON arrays:
        ```json
        ["policy.create", "policy.read", "policy.update", "scan.create"]
        ```

    Notes:
        - Permission strings are case-sensitive
        - Only permissions from active roles are checked (role.is_active == True)
        - User must be authenticated (requires get_current_user dependency)
        - Access granted if user has ANY of the required permissions (OR logic)
        - Invalid JSON in role.permissions is logged as error and skipped
    """

    def permission_checker(current_user: User = Depends(get_current_user)) -> None:
        """Inner dependency that performs the actual permission checking."""
        # Collect all permissions from user's active roles
        user_permissions = set()

        for role in current_user.roles:
            if role.is_active and role.permissions:
                try:
                    # Parse permissions JSON array
                    role_perms = json.loads(role.permissions)
                    if isinstance(role_perms, list):
                        user_permissions.update(role_perms)
                    else:
                        logger.warning(
                            "role_permissions_not_list",
                            role_id=str(role.id),
                            role_name=role.name,
                            permissions_type=type(role_perms).__name__,
                        )
                except json.JSONDecodeError as e:
                    logger.error(
                        "invalid_role_permissions_json",
                        role_id=str(role.id),
                        role_name=role.name,
                        error=str(e),
                    )

        # Check if user has any of the required permissions (OR logic)
        has_required_permission = any(perm in user_permissions for perm in required_permissions)

        if not has_required_permission:
            # User lacks all required permissions - deny access
            logger.warning(
                "rbac_access_denied_insufficient_permission",
                user_id=str(current_user.id),
                username=current_user.username,
                user_permissions=list(user_permissions),
                required_permissions=required_permissions,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission(s): {', '.join(required_permissions)}",
            )

        # User has at least one required permission - grant access
        matched_permission = next(p for p in user_permissions if p in required_permissions)
        logger.info(
            "permission_access_granted",
            user_id=str(current_user.id),
            username=current_user.username,
            matched_permission=matched_permission,
            required_permissions=required_permissions,
        )

    return permission_checker
