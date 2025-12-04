"""
AWS IAM Access Analyzer Integration for ZeroTrust IAM Analyzer.

This module provides the core connector to AWS IAM Access Analyzer service using boto3.
It enables detection of external access findings including public S3 buckets,
cross-account IAM roles, KMS keys shared externally, and other resource exposure risks.

v1.1 Enhancement - December 2025
Implements AWS IAM Access Analyzer integration as part of multi-cloud CIEM expansion.

Key Capabilities:
- Connect to AWS IAM Access Analyzer API via boto3
- List and retrieve analyzers across regions
- Fetch external access findings with filtering
- Retrieve archived findings for historical analysis
- Mock mode for demos without live AWS credentials
- Comprehensive error handling and logging
"""

import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class FindingStatus(str, Enum):
    """AWS Access Analyzer finding status enumeration."""
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    RESOLVED = "RESOLVED"


class ResourceType(str, Enum):
    """AWS resource types supported by Access Analyzer."""
    S3_BUCKET = "AWS::S3::Bucket"
    IAM_ROLE = "AWS::IAM::Role"
    KMS_KEY = "AWS::KMS::Key"
    LAMBDA_FUNCTION = "AWS::Lambda::Function"
    LAMBDA_LAYER = "AWS::Lambda::LayerVersion"
    SQS_QUEUE = "AWS::SQS::Queue"
    SECRETS_MANAGER = "AWS::SecretsManager::Secret"
    SNS_TOPIC = "AWS::SNS::Topic"
    EFS_FILE_SYSTEM = "AWS::EFS::FileSystem"
    ECR_REPOSITORY = "AWS::ECR::Repository"
    RDS_DB_SNAPSHOT = "AWS::RDS::DBSnapshot"
    RDS_DB_CLUSTER_SNAPSHOT = "AWS::RDS::DBClusterSnapshot"


class AWSAccessAnalyzer:
    """
    AWS IAM Access Analyzer connector for external access detection.

    This class provides methods to interact with AWS IAM Access Analyzer service
    to identify resources with external access permissions. Supports both live
    AWS API calls and mock mode for demonstrations.

    Attributes:
        region: AWS region for the analyzer
        mock_mode: Enable mock data instead of real AWS API calls
        client: boto3 Access Analyzer client (if not in mock mode)
        account_id: AWS account ID

    Example:
        >>> analyzer = AWSAccessAnalyzer(region="us-east-1", mock_mode=False)
        >>> findings = analyzer.list_findings(status=FindingStatus.ACTIVE)
        >>> print(f"Found {len(findings)} active findings")
    """

    def __init__(
        self,
        region: str = "us-east-1",
        profile_name: Optional[str] = None,
        mock_mode: bool = False,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
    ) -> None:
        """
        Initialize AWS Access Analyzer connector.

        Args:
            region: AWS region (default: us-east-1)
            profile_name: AWS CLI profile name for credentials
            mock_mode: Use mock data instead of real AWS API calls
            aws_access_key_id: AWS access key ID (alternative to profile)
            aws_secret_access_key: AWS secret access key
            aws_session_token: AWS session token (for temporary credentials)

        Raises:
            ImportError: If boto3 is not installed and mock_mode is False
            ValueError: If credentials are invalid
        """
        self.region = region
        self.mock_mode = mock_mode
        self.client = None
        self.account_id = None

        if not mock_mode:
            if not BOTO3_AVAILABLE:
                raise ImportError(
                    "boto3 is required for AWS integration. "
                    "Install with: pip install boto3"
                )

            try:
                # Initialize boto3 session with credentials
                session_kwargs: Dict[str, Any] = {"region_name": region}

                if profile_name:
                    session_kwargs["profile_name"] = profile_name
                elif aws_access_key_id and aws_secret_access_key:
                    session_kwargs["aws_access_key_id"] = aws_access_key_id
                    session_kwargs["aws_secret_access_key"] = aws_secret_access_key
                    if aws_session_token:
                        session_kwargs["aws_session_token"] = aws_session_token

                session = boto3.Session(**session_kwargs)
                self.client = session.client("accessanalyzer")

                # Get AWS account ID
                sts_client = session.client("sts")
                self.account_id = sts_client.get_caller_identity()["Account"]

            except NoCredentialsError:
                raise ValueError(
                    "AWS credentials not found. Please configure credentials "
                    "via AWS CLI, environment variables, or provide explicitly."
                )
            except (BotoCoreError, ClientError) as e:
                raise ValueError(f"Failed to initialize AWS client: {str(e)}")

    def list_analyzers(self) -> List[Dict[str, Any]]:
        """
        List all IAM Access Analyzers in the account.

        Returns:
            List of analyzer metadata dictionaries

        Raises:
            RuntimeError: If API call fails
        """
        if self.mock_mode:
            return self._get_mock_analyzers()

        try:
            response = self.client.list_analyzers()
            return response.get("analyzers", [])
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"Failed to list analyzers: {str(e)}")

    def get_analyzer(self, analyzer_name: str) -> Optional[Dict[str, Any]]:
        """
        Get details of a specific analyzer.

        Args:
            analyzer_name: Name of the analyzer

        Returns:
            Analyzer details dictionary or None if not found

        Raises:
            RuntimeError: If API call fails
        """
        if self.mock_mode:
            analyzers = self._get_mock_analyzers()
            return next((a for a in analyzers if a["name"] == analyzer_name), None)

        try:
            response = self.client.get_analyzer(analyzerName=analyzer_name)
            return response.get("analyzer")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                return None
            raise RuntimeError(f"Failed to get analyzer: {str(e)}")
        except BotoCoreError as e:
            raise RuntimeError(f"Failed to get analyzer: {str(e)}")

    def list_findings(
        self,
        analyzer_arn: Optional[str] = None,
        status: Optional[FindingStatus] = None,
        resource_type: Optional[ResourceType] = None,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List findings from Access Analyzer.

        Args:
            analyzer_arn: ARN of the analyzer (uses first if not specified)
            status: Filter by finding status (ACTIVE, ARCHIVED, RESOLVED)
            resource_type: Filter by resource type
            max_results: Maximum number of findings to return

        Returns:
            List of finding dictionaries with metadata

        Raises:
            RuntimeError: If API call fails or no analyzer found
        """
        if self.mock_mode:
            return self._get_mock_findings(status, resource_type, max_results)

        # Get analyzer ARN if not provided
        if not analyzer_arn:
            analyzers = self.list_analyzers()
            if not analyzers:
                raise RuntimeError("No Access Analyzer found in account")
            analyzer_arn = analyzers[0]["arn"]

        try:
            # Build filter criteria
            filter_criteria = {}
            if status:
                filter_criteria["status"] = {"eq": [status.value]}
            if resource_type:
                filter_criteria["resourceType"] = {"eq": [resource_type.value]}

            # List findings with pagination
            findings = []
            kwargs = {
                "analyzerArn": analyzer_arn,
                "maxResults": min(max_results, 100),
            }
            if filter_criteria:
                kwargs["filter"] = filter_criteria

            while len(findings) < max_results:
                response = self.client.list_findings(**kwargs)
                findings.extend(response.get("findings", []))

                next_token = response.get("nextToken")
                if not next_token or len(findings) >= max_results:
                    break
                kwargs["nextToken"] = next_token

            return findings[:max_results]

        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"Failed to list findings: {str(e)}")

    def get_finding(
        self,
        finding_id: str,
        analyzer_arn: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific finding.

        Args:
            finding_id: ID of the finding
            analyzer_arn: ARN of the analyzer (uses first if not specified)

        Returns:
            Finding details dictionary or None if not found

        Raises:
            RuntimeError: If API call fails
        """
        if self.mock_mode:
            findings = self._get_mock_findings()
            return next((f for f in findings if f["id"] == finding_id), None)

        # Get analyzer ARN if not provided
        if not analyzer_arn:
            analyzers = self.list_analyzers()
            if not analyzers:
                raise RuntimeError("No Access Analyzer found in account")
            analyzer_arn = analyzers[0]["arn"]

        try:
            response = self.client.get_finding(
                analyzerArn=analyzer_arn,
                id=finding_id,
            )
            return response.get("finding")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                return None
            raise RuntimeError(f"Failed to get finding: {str(e)}")
        except BotoCoreError as e:
            raise RuntimeError(f"Failed to get finding: {str(e)}")

    def list_findings_v2(
        self,
        analyzer_arn: Optional[str] = None,
        status: Optional[FindingStatus] = None,
        resource_type: Optional[ResourceType] = None,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List findings using the v2 API with enhanced metadata.

        This method retrieves detailed finding information including full
        resource details, principal information, and access actions.

        Args:
            analyzer_arn: ARN of the analyzer
            status: Filter by finding status
            resource_type: Filter by resource type
            max_results: Maximum number of findings

        Returns:
            List of detailed finding dictionaries

        Raises:
            RuntimeError: If API call fails
        """
        if self.mock_mode:
            return self._get_mock_findings(status, resource_type, max_results)

        # Get analyzer ARN if not provided
        if not analyzer_arn:
            analyzers = self.list_analyzers()
            if not analyzers:
                raise RuntimeError("No Access Analyzer found in account")
            analyzer_arn = analyzers[0]["arn"]

        try:
            # Build filter
            filter_criteria = {}
            if status:
                filter_criteria["status"] = {"eq": [status.value]}
            if resource_type:
                filter_criteria["resourceType"] = {"eq": [resource_type.value]}

            # List findings v2 with pagination
            findings = []
            kwargs = {
                "analyzerArn": analyzer_arn,
                "maxResults": min(max_results, 100),
            }
            if filter_criteria:
                kwargs["filter"] = filter_criteria

            while len(findings) < max_results:
                response = self.client.list_findings_v2(**kwargs)
                findings.extend(response.get("findings", []))

                next_token = response.get("nextToken")
                if not next_token or len(findings) >= max_results:
                    break
                kwargs["nextToken"] = next_token

            return findings[:max_results]

        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"Failed to list findings v2: {str(e)}")

    def get_finding_statistics(
        self,
        analyzer_arn: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get statistics about findings for an analyzer.

        Args:
            analyzer_arn: ARN of the analyzer

        Returns:
            Dictionary with finding counts by status and resource type
        """
        if self.mock_mode:
            return self._get_mock_statistics()

        findings = self.list_findings(analyzer_arn=analyzer_arn, max_results=1000)

        stats = {
            "total_findings": len(findings),
            "by_status": {},
            "by_resource_type": {},
            "by_severity": {},
        }

        for finding in findings:
            # Count by status
            status = finding.get("status", "UNKNOWN")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # Count by resource type
            resource_type = finding.get("resourceType", "UNKNOWN")
            stats["by_resource_type"][resource_type] = \
                stats["by_resource_type"].get(resource_type, 0) + 1

        return stats

    # Mock data methods for demo mode

    def _get_mock_analyzers(self) -> List[Dict[str, Any]]:
        """Generate mock analyzer data for demo mode."""
        return [
            {
                "arn": f"arn:aws:access-analyzer:{self.region}:123456789012:analyzer/demo-analyzer",
                "name": "demo-analyzer",
                "status": "ACTIVE",
                "type": "ACCOUNT",
                "createdAt": datetime(2024, 1, 1).isoformat(),
                "lastResourceAnalyzed": datetime(2025, 12, 4).isoformat(),
                "tags": {"Environment": "Demo", "Purpose": "ZeroTrust-IAM-Analyzer"},
            }
        ]

    def _get_mock_findings(
        self,
        status: Optional[FindingStatus] = None,
        resource_type: Optional[ResourceType] = None,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """Generate mock finding data for demo mode."""
        mock_findings = [
            {
                "id": "finding-001",
                "resourceType": "AWS::S3::Bucket",
                "resourceOwnerAccount": "123456789012",
                "resource": "arn:aws:s3:::public-demo-bucket",
                "status": "ACTIVE",
                "principal": {"AWS": "*"},
                "action": ["s3:GetObject"],
                "condition": {},
                "createdAt": "2025-12-01T10:00:00Z",
                "analyzedAt": "2025-12-04T08:00:00Z",
                "updatedAt": "2025-12-04T08:00:00Z",
                "isPublic": True,
                "error": None,
            },
            {
                "id": "finding-002",
                "resourceType": "AWS::IAM::Role",
                "resourceOwnerAccount": "123456789012",
                "resource": "arn:aws:iam::123456789012:role/cross-account-demo-role",
                "status": "ACTIVE",
                "principal": {"AWS": "arn:aws:iam::999999999999:root"},
                "action": ["sts:AssumeRole"],
                "condition": {},
                "createdAt": "2025-11-15T14:30:00Z",
                "analyzedAt": "2025-12-04T08:00:00Z",
                "updatedAt": "2025-12-04T08:00:00Z",
                "isPublic": False,
                "error": None,
            },
            {
                "id": "finding-003",
                "resourceType": "AWS::KMS::Key",
                "resourceOwnerAccount": "123456789012",
                "resource": "arn:aws:kms:us-east-1:123456789012:key/demo-shared-key",
                "status": "ACTIVE",
                "principal": {"AWS": "arn:aws:iam::888888888888:root"},
                "action": ["kms:Decrypt", "kms:Encrypt"],
                "condition": {},
                "createdAt": "2025-10-20T09:00:00Z",
                "analyzedAt": "2025-12-04T08:00:00Z",
                "updatedAt": "2025-12-04T08:00:00Z",
                "isPublic": False,
                "error": None,
            },
            {
                "id": "finding-004",
                "resourceType": "AWS::Lambda::Function",
                "resourceOwnerAccount": "123456789012",
                "resource": "arn:aws:lambda:us-east-1:123456789012:function:demo-public-function",
                "status": "ARCHIVED",
                "principal": {"Service": "s3.amazonaws.com"},
                "action": ["lambda:InvokeFunction"],
                "condition": {},
                "createdAt": "2025-09-10T16:00:00Z",
                "analyzedAt": "2025-11-01T08:00:00Z",
                "updatedAt": "2025-11-01T08:00:00Z",
                "isPublic": False,
                "error": None,
            },
        ]

        # Apply filters
        filtered = mock_findings
        if status:
            filtered = [f for f in filtered if f["status"] == status.value]
        if resource_type:
            filtered = [f for f in filtered if f["resourceType"] == resource_type.value]

        return filtered[:max_results]

    def _get_mock_statistics(self) -> Dict[str, Any]:
        """Generate mock statistics for demo mode."""
        return {
            "total_findings": 4,
            "by_status": {
                "ACTIVE": 3,
                "ARCHIVED": 1,
            },
            "by_resource_type": {
                "AWS::S3::Bucket": 1,
                "AWS::IAM::Role": 1,
                "AWS::KMS::Key": 1,
                "AWS::Lambda::Function": 1,
            },
            "by_severity": {
                "CRITICAL": 1,
                "HIGH": 1,
                "MEDIUM": 2,
            },
        }
