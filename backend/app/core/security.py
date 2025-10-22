"""
Security utilities for ZeroTrust IAM Analyzer.

This module handles JWT token creation and verification, password hashing,
and authentication dependencies.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.
    
    Args:
        subject: Token subject (usually user ID or email)
        expires_delta: Token expiration time (optional)
        
    Returns:
        JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )
    
    logger.debug("access_token_created", subject=subject, expires=expire)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verify JWT token and return subject.
    
    Args:
        token: JWT token string
        
    Returns:
        Token subject if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        subject: str = payload.get("sub")
        if subject is None:
            logger.warning("token_missing_subject", token=token[:10] + "...")
            return None
        
        logger.debug("token_verified", subject=subject)
        return subject
    except JWTError as e:
        logger.warning("token_verification_failed", error=str(e))
        return None


def get_password_hash(password: str) -> str:
    """
    Hash password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    hashed_password = pwd_context.hash(password, rounds=settings.bcrypt_rounds)
    logger.debug("password_hashed")
    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    is_valid = pwd_context.verify(plain_password, hashed_password)
    logger.debug("password_verification_completed", is_valid=is_valid)
    return is_valid


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> str:
    """
    Dependency to get current user ID from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        User ID
        
    Raises:
        HTTPException: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        user_id = verify_token(credentials.credentials)
        if user_id is None:
            raise credentials_exception
        
        # Here you would typically verify the user exists in the database
        # For now, we'll just return the user_id
        return user_id
    except JWTError as e:
        logger.error("jwt_error", error=str(e))
        raise credentials_exception


def get_current_user(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Dependency to get current user information.
    
    Args:
        current_user_id: Current user ID
        db: Database session
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user is not found
    """
    # This is a placeholder - in a real application, you would
    # fetch the user from the database
    user_info = {
        "id": current_user_id,
        "email": f"user_{current_user_id}@example.com",  # Placeholder
        "is_active": True,
    }
    
    logger.debug("current_user_retrieved", user_id=current_user_id)
    return user_info


def create_refresh_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token.
    
    Args:
        subject: Token subject (usually user ID or email)
        expires_delta: Token expiration time (optional)
        
    Returns:
        JWT refresh token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Refresh tokens typically have longer expiration
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode = {
        "exp": expire, 
        "sub": str(subject),
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )
    
    logger.debug("refresh_token_created", subject=subject, expires=expire)
    return encoded_jwt


def verify_refresh_token(token: str) -> Optional[str]:
    """
    Verify JWT refresh token and return subject.
    
    Args:
        token: JWT refresh token string
        
    Returns:
        Token subject if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        subject: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if subject is None or token_type != "refresh":
            logger.warning("invalid_refresh_token", token=token[:10] + "...")
            return None
        
        logger.debug("refresh_token_verified", subject=subject)
        return subject
    except JWTError as e:
        logger.warning("refresh_token_verification_failed", error=str(e))
        return None


class TokenManager:
    """Token management utility class."""
    
    def __init__(self):
        """Initialize token manager."""
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def create_token_pair(self, subject: Union[str, Any]) -> Dict[str, str]:
        """
        Create access and refresh token pair.
        
        Args:
            subject: Token subject
            
        Returns:
            Dictionary containing access and refresh tokens
        """
        access_token = create_access_token(subject)
        refresh_token = create_refresh_token(subject)
        
        logger.info("token_pair_created", subject=subject)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Create new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token if refresh token is valid, None otherwise
        """
        subject = verify_refresh_token(refresh_token)
        if subject is None:
            return None
        
        new_access_token = create_access_token(subject)
        logger.info("access_token_refreshed", subject=subject)
        return new_access_token


# Create global token manager instance
token_manager = TokenManager()


def get_token_manager() -> TokenManager:
    """
    Get token manager instance.
    
    Returns:
        Token manager instance
    """
    return token_manager


def generate_session_token() -> str:
    """
    Generate a random session token.
    
    Returns:
        Random session token
    """
    import secrets
    token = secrets.token_urlsafe(32)
    logger.debug("session_token_generated")
    return token


def hash_api_key(api_key: str) -> str:
    """
    Hash API key using bcrypt.
    
    Args:
        api_key: Plain text API key
        
    Returns:
        Hashed API key
    """
    hashed_key = pwd_context.hash(api_key, rounds=settings.bcrypt_rounds)
    logger.debug("api_key_hashed")
    return hashed_key


def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """
    Verify plain API key against hashed API key.
    
    Args:
        plain_api_key: Plain text API key
        hashed_api_key: Hashed API key
        
    Returns:
        True if API key matches, False otherwise
    """
    is_valid = pwd_context.verify(plain_api_key, hashed_api_key)
    logger.debug("api_key_verification_completed", is_valid=is_valid)
    return is_valid


def create_api_key() -> Dict[str, str]:
    """
    Create a new API key.
    
    Returns:
        Dictionary containing API key and its hash
    """
    import secrets
    api_key = secrets.token_urlsafe(32)
    hashed_key = hash_api_key(api_key)
    
    logger.info("api_key_created")
    return {
        "api_key": api_key,
        "hashed_key": hashed_key,
    }