"""
Authentication endpoints for ZeroTrust IAM Analyzer.

This module provides authentication endpoints including registration,
login, token refresh, logout, and password reset.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import UserRegisterRequest, UserRegisterResponse
from app.services.auth_service import AuthService, get_auth_service

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
