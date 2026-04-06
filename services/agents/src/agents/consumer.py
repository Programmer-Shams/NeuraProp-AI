"""SQS consumer — polls inbound queue and dispatches to orchestrator."""

import asyncio
import signal

from neuraprop_core.config import get_settings
from neuraprop_core.logging import setup_logging, get_logger
from neuraprop_core.sqs import receive_messages, delete_message

from agents.orchestrator.graph import process_message

logger = get_logger(__name__)

# Graceful shutdown flag
_shutdown = False


def _handle_signal(signum: int, frame: object) -> None:
    global _shutdown
    logger.info("shutdown_signal_received", signal=signum)
    _shutdown = True


async def run_consumer() -> None:
    """Main consumer loop — polls SQS and processes messages."""
    settings = get_settings()
    setup_logging(log_level=settings.log_level, json_output=settings.is_production)
    logger.info("agent_consumer_starting", queue=settings.sqs_inbound_queue_url)

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    while not _shutdown:
        try:
            messages = await receive_messages(
                queue_url=settings.sqs_inbound_queue_url,
                max_messages=5,
                wait_time_seconds=20,
                visibility_timeout=120,
            )

            for msg in messages:
                try:
                    unified_message = msg["ParsedBody"]
                    logger.info(
                        "processing_message",
                        message_id=unified_message.get("id"),
                        firm_id=unified_message.get("firm_id"),
                        channel=unified_message.get("channel"),
                    )

                    await process_message(unified_message)

                    # Delete message after successful processing
                    await delete_message(
                        queue_url=settings.sqs_inbound_queue_url,
                        receipt_handle=msg["ReceiptHandle"],
                    )

                    logger.info(
                        "message_processed",
                        message_id=unified_message.get("id"),
                    )

                except Exception:
                    logger.exception(
                        "message_processing_failed",
                        message_id=msg.get("MessageId"),
                    )
                    # Message will return to queue after visibility timeout

        except Exception:
            logger.exception("consumer_poll_error")
            await asyncio.sleep(5)

    logger.info("agent_consumer_stopped")


def main() -> None:
    """Entry point for the consumer."""
    asyncio.run(run_consumer())


if __name__ == "__main__":
    main()
