"""
Configuration module for ZeroTrust IAM Analyzer.

This module handles all application configuration using Pydantic Settings
with environment variable support.
"""

from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # Application Configuration
    app_name: str = Field(default="ZeroTrust IAM Analyzer")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    api_prefix: str = Field(default="/api/v1")
    port: int = Field(default=8080)

    # Security Configuration
    secret_key: str
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    bcrypt_rounds: int = Field(default=12)
    session_timeout_hours: int = Field(default=24)

    # Database Configuration
    database_url: str

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379")

    # CORS Configuration
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:5173"])

    # GCP Configuration
    gcp_project_id: Optional[str] = Field(default=None)
    gcp_region: str = Field(default="us-central1")

    # Google Cloud IAM & Workspace Configuration
    gcp_service_account_file: Optional[str] = Field(default=None)
    gcp_service_account_json: Optional[str] = Field(default=None)
    workspace_customer_id: Optional[str] = Field(default=None)
    workspace_admin_email: Optional[str] = Field(default=None)
    workspace_domain: Optional[str] = Field(default=None)

    # Security Command Center Configuration
    scc_organization_id: Optional[str] = Field(default=None)
    scc_source_id: Optional[str] = Field(default=None)

    # Cloud Run Configuration
    cloud_run_service_url: Optional[str] = Field(default=None)

    # Logging Configuration
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    log_requests: bool = Field(default=True)

    # Cache Configuration
    cache_ttl_seconds: int = Field(default=3600)
    cache_max_size: int = Field(default=1000)

    # External API Rate Limiting
    gcp_iam_api_rate_limit: int = Field(default=100)
    gcp_asset_api_rate_limit: int = Field(default=100)
    workspace_api_rate_limit: int = Field(default=100)
    scc_api_rate_limit: int = Field(default=100)

    # Monitoring and Observability
    enable_metrics: bool = Field(default=True)
    enable_tracing: bool = Field(default=True)
    sampling_rate: float = Field(default=0.1)

    # Email Configuration
    smtp_host: Optional[str] = Field(default=None)
    smtp_port: int = Field(default=587)
    smtp_user: Optional[str] = Field(default=None)
    smtp_password: Optional[str] = Field(default=None)
    email_from: Optional[str] = Field(default=None)
    email_from_name: Optional[str] = Field(default=None)

    # Webhook Configuration
    webhook_url: Optional[str] = Field(default=None)
    webhook_secret: Optional[str] = Field(default=None)

    # Feature Flags
    enable_scheduler: bool = Field(default=True)
    enable_email_notifications: bool = Field(default=False)
    enable_webhook_notifications: bool = Field(default=False)
    enable_advanced_analytics: bool = Field(default=True)
    enable_policy_analyzer: bool = Field(default=True)
    enable_iam_recommender: bool = Field(default=True)
    enable_security_command_center: bool = Field(default=True)

    # Development Settings
    reload: bool = Field(default=False)
    show_docs: bool = Field(default=True)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment value."""
        allowed = ["development", "testing", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v.upper()


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
