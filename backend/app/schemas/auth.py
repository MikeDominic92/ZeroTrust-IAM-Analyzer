"""
Authentication schemas for ZeroTrust IAM Analyzer.

This module contains Pydantic schemas for authentication operations including
registration, login, token management, and password reset.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


# ===================================================
# Registration Schemas
# ===================================================


class UserRegisterRequest(BaseModel):
    """Schema for user registration request."""

    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(
        ..., min_length=3, max_length=50, description="Unique username for login"
    )
    password: str = Field(..., min_length=8, max_length=100, description="User's password")
    first_name: Optional[str] = Field(None, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User's last name")
    department: Optional[str] = Field(None, max_length=100, description="User's department")
    job_title: Optional[str] = Field(None, max_length=100, description="User's job title")

    @validator("username")
    def validate_username(cls, v):
        """Validate username format."""
        if not v.isalnum() and "_" not in v and "-" not in v:
            raise ValueError(
                "Username must contain only alphanumeric characters, underscores, or hyphens"
            )
        return v.lower()

    @validator("password")
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, one lowercase letter, and one digit"
            )

        if not has_special:
            # Warning: special characters recommended but not required
            pass

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "analyst@example.com",
                "username": "security_analyst",
                "password": "SecurePass123!",
                "first_name": "Jane",
                "last_name": "Doe",
                "department": "Security Operations",
                "job_title": "Security Analyst",
            }
        }


class UserRegisterResponse(BaseModel):
    """Schema for user registration response."""

    id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    status: str = Field(..., description="User's account status")
    is_verified: bool = Field(..., description="Whether user's email is verified")
    created_at: datetime = Field(..., description="Account creation timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "analyst@example.com",
                "username": "security_analyst",
                "status": "pending_verification",
                "is_verified": False,
                "created_at": "2025-10-25T12:00:00Z",
            }
        }


# ===================================================
# Login Schemas
# ===================================================


class UserLoginRequest(BaseModel):
    """Schema for user login request."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User's password")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "security_analyst",
                "password": "SecurePass123!",
            }
        }


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        }


class UserLoginResponse(BaseModel):
    """Schema for user login response."""

    user: "UserProfile"
    tokens: TokenResponse

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "analyst@example.com",
                    "username": "security_analyst",
                    "full_name": "Jane Doe",
                    "role": "analyst",
                    "is_active": True,
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                },
            }
        }


# ===================================================
# User Profile Schemas
# ===================================================


class UserProfile(BaseModel):
    """Schema for user profile information."""

    id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    full_name: Optional[str] = Field(None, description="User's full name")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    display_name: Optional[str] = Field(None, description="User's display name")
    role: str = Field(..., description="User's role")
    status: str = Field(..., description="User's account status")
    is_active: bool = Field(..., description="Whether user account is active")
    is_verified: bool = Field(..., description="Whether user's email is verified")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: datetime = Field(..., description="Account creation timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "analyst@example.com",
                "username": "security_analyst",
                "full_name": "Jane Doe",
                "first_name": "Jane",
                "last_name": "Doe",
                "display_name": "Jane Doe",
                "role": "analyst",
                "status": "active",
                "is_active": True,
                "is_verified": True,
                "last_login_at": "2025-10-25T12:00:00Z",
                "created_at": "2025-10-20T10:30:00Z",
            }
        }


# ===================================================
# Token Refresh Schemas
# ===================================================


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(..., description="Refresh token")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            }
        }


# ===================================================
# Password Reset Schemas
# ===================================================


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""

    email: EmailStr = Field(..., description="User's email address")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "analyst@example.com",
            }
        }


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")

    @validator("new_password")
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, one lowercase letter, and one digit"
            )

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "token": "reset_token_abc123",
                "new_password": "NewSecurePass456!",
            }
        }


# ===================================================
# Logout Schema
# ===================================================


class LogoutRequest(BaseModel):
    """Schema for logout request."""

    revoke_all_sessions: bool = Field(
        default=False, description="Whether to revoke all user sessions"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "revoke_all_sessions": False,
            }
        }


# ===================================================
# Error Response Schemas
# ===================================================


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input data",
                "details": {
                    "field": "password",
                    "issue": "Password must contain at least one digit",
                },
            }
        }


# Update forward references
UserLoginResponse.model_rebuild()
