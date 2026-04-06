"""S3 client for document storage."""

from typing import Any

import aioboto3

from neuraprop_core.config import get_settings
from neuraprop_core.logging import get_logger

logger = get_logger(__name__)

_session: aioboto3.Session | None = None


def _get_session() -> aioboto3.Session:
    global _session
    if _session is None:
        settings = get_settings()
        _session = aioboto3.Session(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
    return _session


def _get_endpoint_url() -> str | None:
    settings = get_settings()
    return settings.aws_endpoint_url


async def upload_file(
    key: str,
    data: bytes,
    content_type: str = "application/octet-stream",
    bucket: str | None = None,
    metadata: dict[str, str] | None = None,
) -> str:
    """Upload a file to S3. Returns the S3 key."""
    settings = get_settings()
    bucket = bucket or settings.s3_bucket_name
    session = _get_session()

    async with session.client("s3", endpoint_url=_get_endpoint_url()) as client:
        kwargs: dict[str, Any] = {
            "Bucket": bucket,
            "Key": key,
            "Body": data,
            "ContentType": content_type,
        }
        if metadata:
            kwargs["Metadata"] = metadata

        await client.put_object(**kwargs)
        logger.info("s3_file_uploaded", bucket=bucket, key=key, size=len(data))
        return key


async def download_file(key: str, bucket: str | None = None) -> bytes:
    """Download a file from S3."""
    settings = get_settings()
    bucket = bucket or settings.s3_bucket_name
    session = _get_session()

    async with session.client("s3", endpoint_url=_get_endpoint_url()) as client:
        response = await client.get_object(Bucket=bucket, Key=key)
        data = await response["Body"].read()
        return data


async def delete_file(key: str, bucket: str | None = None) -> None:
    """Delete a file from S3."""
    settings = get_settings()
    bucket = bucket or settings.s3_bucket_name
    session = _get_session()

    async with session.client("s3", endpoint_url=_get_endpoint_url()) as client:
        await client.delete_object(Bucket=bucket, Key=key)


async def generate_presigned_url(
    key: str,
    bucket: str | None = None,
    expires_in: int = 3600,
) -> str:
    """Generate a presigned URL for temporary file access."""
    settings = get_settings()
    bucket = bucket or settings.s3_bucket_name
    session = _get_session()

    async with session.client("s3", endpoint_url=_get_endpoint_url()) as client:
        url = await client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        return url


async def create_bucket(bucket: str | None = None) -> None:
    """Create an S3 bucket (used in development/testing)."""
    settings = get_settings()
    bucket = bucket or settings.s3_bucket_name
    session = _get_session()

    async with session.client("s3", endpoint_url=_get_endpoint_url()) as client:
        try:
            await client.create_bucket(Bucket=bucket)
        except client.exceptions.BucketAlreadyOwnedByYou:
            pass
