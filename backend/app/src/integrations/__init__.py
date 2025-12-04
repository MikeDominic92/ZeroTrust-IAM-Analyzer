"""
AWS IAM Access Analyzer Integration Module for ZeroTrust IAM Analyzer.

This module provides integration with AWS IAM Access Analyzer service to extend
the ZeroTrust IAM Analyzer platform with AWS cloud provider support.

v1.1 Enhancement - December 2025
Added AWS IAM Access Analyzer integration to complement existing GCP and
Google Workspace analysis capabilities, enabling multi-cloud CIEM functionality.

Key Features:
- AWS IAM Access Analyzer API integration via boto3
- External access findings detection (public S3, cross-account roles, etc.)
- Finding normalization for unified CIEM dashboard
- Policy validation against CIS AWS Foundations Benchmark
- Severity scoring and risk assessment
- Mock mode for demos without AWS credentials

Modules:
    aws_access_analyzer: Core AWS IAM Access Analyzer connector
    finding_processor: Finding normalization and processing
    policy_validator: IAM policy validation against security benchmarks
"""

from typing import Optional

__version__ = "1.1.0"
__author__ = "ZeroTrust IAM Analyzer Team"
__date__ = "December 2025"

# Import main classes for convenience
try:
    from .aws_access_analyzer import AWSAccessAnalyzer
    from .finding_processor import FindingProcessor
    from .policy_validator import PolicyValidator

    __all__ = [
        "AWSAccessAnalyzer",
        "FindingProcessor",
        "PolicyValidator",
    ]
except ImportError as e:
    # Allow module import even if dependencies aren't installed
    __all__ = []


def get_version() -> str:
    """
    Get the current version of the AWS integration module.

    Returns:
        Version string in semantic versioning format
    """
    return __version__
