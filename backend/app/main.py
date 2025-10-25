"""
Main FastAPI application for ZeroTrust IAM Analyzer.

This module contains the FastAPI app instance with proper configuration,
CORS middleware setup, API router inclusion, and health check endpoints.
"""

from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import get_settings
from .core.database import check_database_connection, get_database_info
from .core.logging import RequestLoggingMiddleware, configure_logging, get_logger
from .core.security import get_token_manager

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("application_startup", app_name=settings.app_name, version=settings.app_version)

    # Check database connection
    db_healthy = check_database_connection()
    if not db_healthy:
        logger.error("database_connection_failed_on_startup")

    logger.info("application_startup_completed")

    yield

    # Shutdown
    logger.info("application_shutdown")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Multi-cloud IAM analyzer for Microsoft Entra ID and Google Cloud IAM policies",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.show_docs else None,
    redoc_url="/redoc" if settings.show_docs else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware if enabled
if settings.log_requests:
    app.add_middleware(RequestLoggingMiddleware)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None),
        },
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404 exception handler."""
    logger.warning(
        "not_found",
        path=request.url.path,
        method=request.method,
    )

    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"Endpoint {request.method} {request.url.path} not found",
        },
    )


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, any]:
    """
    Basic health check endpoint.

    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/health/ready", tags=["Health"])
async def readiness_check() -> Dict[str, any]:
    """
    Readiness check endpoint.

    Returns:
        Readiness status with database connectivity
    """
    db_healthy = check_database_connection()

    status = "ready" if db_healthy else "not_ready"

    return {
        "status": status,
        "checks": {
            "database": "healthy" if db_healthy else "unhealthy",
        },
        "service": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/health/live", tags=["Health"])
async def liveness_check() -> Dict[str, any]:
    """
    Liveness check endpoint.

    Returns:
        Liveness status
    """
    return {
        "status": "alive",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check() -> Dict[str, any]:
    """
    Detailed health check endpoint.

    Returns:
        Detailed health status including database info
    """
    db_healthy = check_database_connection()
    db_info = get_database_info() if db_healthy else {"error": "Database not connected"}

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "checks": {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "info": db_info,
            },
        },
        "token_manager": {
            "status": "healthy",
            "algorithm": settings.algorithm,
        },
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, any]:
    """
    Root endpoint with application information.

    Returns:
        Application information
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs_url": "/docs" if settings.show_docs else None,
        "health_check": "/health",
        "api_prefix": settings.api_prefix,
    }


@app.get(f"{settings.api_prefix}/info", tags=["Root"])
async def app_info() -> Dict[str, any]:
    """
    Application information endpoint.

    Returns:
        Detailed application information
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "api_prefix": settings.api_prefix,
        "features": {
            "metrics": settings.enable_metrics,
            "tracing": settings.enable_tracing,
            "scheduler": settings.enable_scheduler,
            "email_notifications": settings.enable_email_notifications,
            "webhook_notifications": settings.enable_webhook_notifications,
            "advanced_analytics": settings.enable_advanced_analytics,
        },
        "cloud_providers": {
            "azure": bool(settings.azure_tenant_id),
            "gcp": bool(settings.gcp_project_id),
        },
    }


# Placeholder for API router inclusion
# This will be expanded as we add more endpoints
# from app.api.v1.api import api_router
# app.include_router(api_router, prefix=settings.api_prefix)


if __name__ == "__main__":
    import uvicorn

    logger.info(
        "starting_server",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.reload,
        debug=settings.debug,
    )

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
