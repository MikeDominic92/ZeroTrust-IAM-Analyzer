"""
Logging configuration for ZeroTrust IAM Analyzer.

This module provides structured logging with request context and proper formatting.
"""

import logging
import sys
import time
from typing import Any, Dict
from uuid import uuid4

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .config import get_settings

settings = get_settings()


def configure_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.log_format == "json"
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and log details."""
        # Generate request ID
        request_id = str(uuid4())
        
        # Get start time
        start_time = time.time()
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Get user agent
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log request
        logger = structlog.get_logger()
        logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=client_ip,
            user_agent=user_agent,
        )
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            logger.error(
                "request_failed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                error=str(e),
                exc_info=True,
            )
            raise
        finally:
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                "request_completed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                status_code=status_code,
                process_time=round(process_time, 4),
            )
            
            # Add processing time to response headers
            if "response" in locals():
                response.headers["X-Process-Time"] = str(round(process_time, 4))
                response.headers["X-Request-ID"] = request_id
        
        return response


class LoggerMixin:
    """Mixin to add logging capabilities to classes."""
    
    @property
    def logger(self):
        """Get logger for the class."""
        return structlog.get_logger(self.__class__.__name__)


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance.
    
    Args:
        name: Logger name (optional)
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


def log_function_call(func):
    """Decorator to log function calls.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(
            "function_called",
            function=func.__name__,
            args=args,
            kwargs=kwargs,
        )
        
        try:
            result = func(*args, **kwargs)
            logger.debug(
                "function_completed",
                function=func.__name__,
                result_type=type(result).__name__,
            )
            return result
        except Exception as e:
            logger.error(
                "function_failed",
                function=func.__name__,
                error=str(e),
                exc_info=True,
            )
            raise
    
    return wrapper


async def log_async_function_call(func, *args, **kwargs):
    """Log async function calls.
    
    Args:
        func: Async function to call
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result
    """
    logger = get_logger(func.__module__)
    logger.debug(
        "async_function_called",
        function=func.__name__,
        args=args,
        kwargs=kwargs,
    )
    
    try:
        result = await func(*args, **kwargs)
        logger.debug(
            "async_function_completed",
            function=func.__name__,
            result_type=type(result).__name__,
        )
        return result
    except Exception as e:
        logger.error(
            "async_function_failed",
            function=func.__name__,
            error=str(e),
            exc_info=True,
        )
        raise


def log_api_request(
    request: Request,
    response: Response = None,
    error: Exception = None,
    additional_data: Dict[str, Any] = None
) -> None:
    """Log API request details.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object (optional)
        error: Exception if request failed (optional)
        additional_data: Additional data to log (optional)
    """
    logger = get_logger("api")
    
    log_data = {
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
    }
    
    if response:
        log_data["status_code"] = response.status_code
    
    if error:
        log_data["error"] = str(error)
        logger.error("api_request_failed", **log_data, exc_info=True)
    else:
        logger.info("api_request_completed", **log_data)
    
    if additional_data:
        logger.info("api_request_additional_data", **additional_data)


# Initialize logging on module import
configure_logging()