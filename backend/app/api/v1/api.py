"""
Main API router for v1 endpoints.

This module aggregates all v1 API routers (auth, scans, policies, etc.)
and provides a single router to include in the main FastAPI application.
"""

from app.api.v1 import auth
from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
