"""
Configuration module for ZeroTrust IAM Analyzer.

This module handles all application configuration using Pydantic Settings
with environment variable support.
"""

import os
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application Configuration
    app_name: str = Field(default="ZeroTrust IAM Analyzer", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    port: int = Field(default=8080, env="PORT")
    
    # Security Configuration
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    bcrypt_rounds: int = Field(default=12, env="BCRYPT_ROUNDS")
    session_timeout_hours: int = Field(default=24, env="SESSION_TIMEOUT_HOURS")
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )
    
    # GCP Configuration
    gcp_project_id: Optional[str] = Field(default=None, env="GCP_PROJECT_ID")
    gcp_region: str = Field(default="us-central1", env="GCP_REGION")
    
    # Google Cloud IAM & Workspace Configuration
    gcp_service_account_file: Optional[str] = Field(default=None, env="GCP_SERVICE_ACCOUNT_FILE")
    gcp_service_account_json: Optional[str] = Field(default=None, env="GCP_SERVICE_ACCOUNT_JSON")
    workspace_customer_id: Optional[str] = Field(default=None, env="WORKSPACE_CUSTOMER_ID")
    workspace_admin_email: Optional[str] = Field(default=None, env="WORKSPACE_ADMIN_EMAIL")
    workspace_domain: Optional[str] = Field(default=None, env="WORKSPACE_DOMAIN")

    # Security Command Center Configuration
    scc_organization_id: Optional[str] = Field(default=None, env="SCC_ORGANIZATION_ID")
    scc_source_id: Optional[str] = Field(default=None, env="SCC_SOURCE_ID")
    
    # Cloud Run Configuration
    cloud_run_service_url: Optional[str] = Field(default=None, env="CLOUD_RUN_SERVICE_URL")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_requests: bool = Field(default=True, env="LOG_REQUESTS")
    
    # Cache Configuration
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    cache_max_size: int = Field(default=1000, env="CACHE_MAX_SIZE")
    
    # External API Rate Limiting
    gcp_iam_api_rate_limit: int = Field(default=100, env="GCP_IAM_API_RATE_LIMIT")
    gcp_asset_api_rate_limit: int = Field(default=100, env="GCP_ASSET_API_RATE_LIMIT")
    workspace_api_rate_limit: int = Field(default=100, env="WORKSPACE_API_RATE_LIMIT")
    scc_api_rate_limit: int = Field(default=100, env="SCC_API_RATE_LIMIT")
    
    # Monitoring and Observability
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    enable_tracing: bool = Field(default=True, env="ENABLE_TRACING")
    sampling_rate: float = Field(default=0.1, env="SAMPLING_RATE")
    
    # Email Configuration
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    email_from: Optional[str] = Field(default=None, env="EMAIL_FROM")
    email_from_name: Optional[str] = Field(default=None, env="EMAIL_FROM_NAME")
    
    # Webhook Configuration
    webhook_url: Optional[str] = Field(default=None, env="WEBHOOK_URL")
    webhook_secret: Optional[str] = Field(default=None, env="WEBHOOK_SECRET")
    
    # Feature Flags
    enable_scheduler: bool = Field(default=True, env="ENABLE_SCHEDULER")
    enable_email_notifications: bool = Field(default=False, env="ENABLE_EMAIL_NOTIFICATIONS")
    enable_webhook_notifications: bool = Field(default=False, env="ENABLE_WEBHOOK_NOTIFICATIONS")
    enable_advanced_analytics: bool = Field(default=True, env="ENABLE_ADVANCED_ANALYTICS")
    enable_policy_analyzer: bool = Field(default=True, env="ENABLE_POLICY_ANALYZER")
    enable_iam_recommender: bool = Field(default=True, env="ENABLE_IAM_RECOMMENDER")
    enable_security_command_center: bool = Field(default=True, env="ENABLE_SECURITY_COMMAND_CENTER")
    
    # Development Settings
    reload: bool = Field(default=False, env="RELOAD")
    show_docs: bool = Field(default=True, env="SHOW_DOCS")
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment value."""
        allowed = ["development", "testing", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings