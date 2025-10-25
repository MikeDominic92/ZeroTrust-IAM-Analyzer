"""
User schemas for ZeroTrust IAM Analyzer.

This module contains Pydantic schemas for user authentication,
profile management, and user-related operations.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from .common import BaseResponse, BaseSchema, PaginatedResponse, TimestampedSchema, UUIDSchema


class UserRole(BaseSchema):
    """User role enumeration schema."""

    ADMIN: str = "admin"
    ANALYST: str = "analyst"
    VIEWER: str = "viewer"
    AUDITOR: str = "auditor"


class UserStatus(BaseSchema):
    """User status enumeration schema."""

    ACTIVE: str = "active"
    INACTIVE: str = "inactive"
    SUSPENDED: str = "suspended"
    PENDING_VERIFICATION: str = "pending_verification"
    LOCKED: str = "locked"


class AuthenticationProvider(BaseSchema):
    """Authentication provider enumeration schema."""

    LOCAL: str = "local"
    MICROSOFT: str = "microsoft"
    GOOGLE: str = "google"
    SAML: str = "saml"


# Base User Schemas
class UserBase(BaseSchema):
    """Base user schema with common fields."""

    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=100, description="Unique username")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    display_name: Optional[str] = Field(None, max_length=200, description="Display name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    department: Optional[str] = Field(None, max_length=100, description="Department")
    job_title: Optional[str] = Field(None, max_length=100, description="Job title")
    role: str = Field(default="viewer", description="User role")
    is_active: bool = Field(default=True, description="Whether user is active")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Validate username format."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")
        return v.lower()


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8, description="Password")
    confirm_password: str = Field(..., description="Confirm password")
    auth_provider: str = Field(default="local", description="Authentication provider")

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, values):
        """Validate that passwords match."""
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseSchema):
    """User update schema."""

    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    display_name: Optional[str] = Field(None, max_length=200, description="Display name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    department: Optional[str] = Field(None, max_length=100, description="Department")
    job_title: Optional[str] = Field(None, max_length=100, description="Job title")
    role: Optional[str] = Field(None, description="User role")
    is_active: Optional[bool] = Field(None, description="Whether user is active")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar URL")


class UserAdminUpdate(UserUpdate):
    """Admin user update schema with additional fields."""

    email: Optional[EmailStr] = Field(None, description="Email address")
    status: Optional[str] = Field(None, description="Account status")
    is_verified: Optional[bool] = Field(None, description="Whether email is verified")
    is_superuser: Optional[bool] = Field(None, description="Superuser status")
    notes: Optional[str] = Field(None, description="Administrative notes")


# Authentication Schemas
class UserLogin(BaseSchema):
    """User login schema."""

    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(default=False, description="Remember me")


class UserLoginResponse(BaseSchema):
    """User login response schema."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: "UserResponse" = Field(..., description="User information")


class TokenRefresh(BaseSchema):
    """Token refresh schema."""

    refresh_token: str = Field(..., description="Refresh token")


class TokenRefreshResponse(BaseSchema):
    """Token refresh response schema."""

    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class PasswordChange(BaseSchema):
    """Password change schema."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, values):
        """Validate that passwords match."""
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class PasswordReset(BaseSchema):
    """Password reset request schema."""

    email: EmailStr = Field(..., description="Email address")


class PasswordResetConfirm(BaseSchema):
    """Password reset confirmation schema."""

    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, values):
        """Validate that passwords match."""
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v


# Response Schemas
class UserResponse(UUIDSchema, TimestampedSchema, UserBase):
    """User response schema."""

    auth_provider: str = Field(..., description="Authentication provider")
    provider_id: Optional[str] = Field(None, description="External provider ID")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    status: str = Field(..., description="Account status")
    is_verified: bool = Field(..., description="Whether email is verified")
    is_superuser: bool = Field(..., description="Superuser status")
    failed_login_attempts: int = Field(..., description="Failed login attempts")
    last_login_at: Optional[datetime] = Field(None, description="Last login time")
    last_login_ip: Optional[str] = Field(None, description="Last login IP")
    two_factor_enabled: bool = Field(..., description="Two-factor authentication status")
    full_name: Optional[str] = Field(None, description="Full name")
    is_account_locked: bool = Field(..., description="Whether account is locked")

    model_config = {"from_attributes": True}


class UserSummary(BaseSchema):
    """User summary schema for list views."""

    id: uuid.UUID = Field(..., description="User ID")
    email: EmailStr = Field(..., description="Email address")
    username: str = Field(..., description="Username")
    display_name: Optional[str] = Field(None, description="Display name")
    full_name: Optional[str] = Field(None, description="Full name")
    role: str = Field(..., description="User role")
    status: str = Field(..., description="Account status")
    is_active: bool = Field(..., description="Whether user is active")
    is_verified: bool = Field(..., description="Whether email is verified")
    last_login_at: Optional[datetime] = Field(None, description="Last login time")
    created_at: datetime = Field(..., description="Account creation time")

    model_config = {"from_attributes": True}


class UserProfile(UserResponse):
    """Extended user profile schema."""

    permissions: Optional[Dict[str, Any]] = Field(None, description="User permissions")
    last_password_change: Optional[datetime] = Field(None, description="Last password change")
    password_expires_at: Optional[datetime] = Field(None, description="Password expiration")
    must_change_password: bool = Field(..., description="Must change password")
    notes: Optional[str] = Field(None, description="Administrative notes")
    created_by: Optional[uuid.UUID] = Field(None, description="Created by user ID")


# Admin Schemas
class UserAdminCreate(UserCreate):
    """Admin user creation schema."""

    is_verified: bool = Field(default=False, description="Whether email is verified")
    is_superuser: bool = Field(default=False, description="Superuser status")
    status: str = Field(default="pending_verification", description="Account status")
    notes: Optional[str] = Field(None, description="Administrative notes")
    send_welcome_email: bool = Field(default=True, description="Send welcome email")


class UserBulkUpdate(BaseSchema):
    """Bulk user update schema."""

    user_ids: List[uuid.UUID] = Field(..., description="List of user IDs")
    updates: UserAdminUpdate = Field(..., description="Updates to apply")

    @field_validator("user_ids")
    @classmethod
    def validate_user_ids(cls, v):
        """Validate user IDs list."""
        if not v:
            raise ValueError("user_ids cannot be empty")
        if len(v) > 50:
            raise ValueError("Cannot update more than 50 users at once")
        return v


class UserActivity(BaseSchema):
    """User activity schema."""

    id: uuid.UUID = Field(..., description="Activity ID")
    user_id: uuid.UUID = Field(..., description="User ID")
    action: str = Field(..., description="Action performed")
    resource: Optional[str] = Field(None, description="Resource affected")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    timestamp: datetime = Field(..., description="Activity timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")

    model_config = {"from_attributes": True}


# Response Types
class UserListResponse(PaginatedResponse[UserSummary]):
    """User list response schema."""

    pass


class UserDetailResponse(BaseResponse[UserProfile]):
    """User detail response schema."""

    pass


class UserActivityResponse(PaginatedResponse[UserActivity]):
    """User activity response schema."""

    pass


class UserStats(BaseSchema):
    """User statistics schema."""

    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    verified_users: int = Field(..., description="Number of verified users")
    locked_users: int = Field(..., description="Number of locked users")
    users_by_role: Dict[str, int] = Field(..., description="Users by role")
    users_by_status: Dict[str, int] = Field(..., description="Users by status")
    recent_logins: int = Field(..., description="Number of recent logins (24h)")
    new_users: int = Field(..., description="Number of new users (7d)")


# Two-Factor Authentication Schemas
class TwoFactorSetup(BaseSchema):
    """Two-factor authentication setup schema."""

    secret: str = Field(..., description="TOTP secret")
    qr_code: str = Field(..., description="QR code for setup")
    backup_codes: List[str] = Field(..., description="Backup codes")


class TwoFactorVerify(BaseSchema):
    """Two-factor verification schema."""

    code: str = Field(..., min_length=6, max_length=6, description="Verification code")


class TwoFactorEnable(BaseSchema):
    """Two-factor enable schema."""

    code: str = Field(..., min_length=6, max_length=6, description="Verification code")


class TwoFactorDisable(BaseSchema):
    """Two-factor disable schema."""

    password: str = Field(..., description="Password for confirmation")


# Session Management
class SessionInfo(BaseSchema):
    """Session information schema."""

    session_id: str = Field(..., description="Session ID")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    created_at: datetime = Field(..., description="Session creation time")
    last_accessed: datetime = Field(..., description="Last access time")
    expires_at: datetime = Field(..., description="Session expiration time")
    is_current: bool = Field(..., description="Whether this is the current session")


class UserSessionsResponse(PaginatedResponse[SessionInfo]):
    """User sessions response schema."""

    pass


# Forward references for type hints
UserLoginResponse.model_rebuild()
