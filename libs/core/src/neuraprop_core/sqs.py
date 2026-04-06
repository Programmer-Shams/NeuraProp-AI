"""SQS publisher and consumer for async message processing."""

import json
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


async def publish_message(
    queue_url: str,
    message: dict[str, Any],
    message_group_id: str | None = None,
    deduplication_id: str | None = None,
) -> str:
    """
    Publish a message to an SQS queue.

    Returns the message ID.
    """
    session = _get_session()
    async with session.client("sqs", endpoint_url=_get_endpoint_url()) as client:
        kwargs: dict[str, Any] = {
            "QueueUrl": queue_url,
            "MessageBody": json.dumps(message, default=str),
        }
        if message_group_id:
            kwargs["MessageGroupId"] = message_group_id
        if deduplication_id:
            kwargs["MessageDeduplicationId"] = deduplication_id

        response = await client.send_message(**kwargs)
        message_id = response["MessageId"]
        logger.info("sqs_message_published", queue_url=queue_url, message_id=message_id)
        return message_id


async def receive_messages(
    queue_url: str,
    max_messages: int = 10,
    wait_time_seconds: int = 20,
    visibility_timeout: int = 60,
) -> list[dict[str, Any]]:
    """
    Receive messages from an SQS queue (long polling).

    Returns list of messages with 'Body', 'MessageId', 'ReceiptHandle'.
    """
    session = _get_session()
    async with session.client("sqs", endpoint_url=_get_endpoint_url()) as client:
        response = await client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=wait_time_seconds,
            VisibilityTimeout=visibility_timeout,
        )
        messages = response.get("Messages", [])
        for msg in messages:
            msg["ParsedBody"] = json.loads(msg["Body"])
        return messages


async def delete_message(queue_url: str, receipt_handle: str) -> None:
    """Delete a message from the queue after successful processing."""
    session = _get_session()
    async with session.client("sqs", endpoint_url=_get_endpoint_url()) as client:
        await client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle,
        )


async def create_queue(queue_name: str, fifo: bool = False) -> str:
    """Create an SQS queue (used in development/testing). Returns queue URL."""
    session = _get_session()
    async with session.client("sqs", endpoint_url=_get_endpoint_url()) as client:
        attributes: dict[str, str] = {}
        name = queue_name
        if fifo:
            attributes["FifoQueue"] = "true"
            attributes["ContentBasedDeduplication"] = "true"
            if not name.endswith(".fifo"):
                name += ".fifo"

        response = await client.create_queue(
            QueueName=name,
            Attributes=attributes,
        )
        return response["QueueUrl"]
