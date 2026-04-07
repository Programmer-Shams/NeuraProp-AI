"""Discord bot runner — entry point for starting Discord bots for all configured firms."""

import asyncio
import signal

from neuraprop_core.config import get_settings
from neuraprop_core.logging import get_logger, setup_logging

from channels.discord.adapter import DiscordAdapter

logger = get_logger(__name__)


async def load_firm_bot_configs() -> list[dict]:
    """
    Load bot configurations for all firms from the database.

    In production, this queries firm_integrations WHERE integration_type = 'discord'.
    For development, returns a demo config from environment.
    """
    settings = get_settings()

    # TODO: Load from database in production
    # For now, use env vars for a single demo firm
    demo_token = getattr(settings, "discord_bot_token", "")
    if not demo_token:
        logger.warning("no_discord_bot_token_configured")
        return []

    return [
        {
            "firm_id": "demo-firm-001",
            "firm_name": "Demo Trading Firm",
            "bot_token": demo_token,
            "support_channel_ids": [],
        }
    ]


async def main():
    """Main entry point for the Discord bot service."""
    setup_logging()
    logger.info("discord_service_starting")

    adapter = DiscordAdapter()

    # Load configs and register bots
    configs = await load_firm_bot_configs()
    bot_tokens = {}

    for config in configs:
        adapter.add_firm_bot(
            firm_id=config["firm_id"],
            firm_name=config["firm_name"],
            bot_token=config["bot_token"],
            support_channel_ids=config.get("support_channel_ids"),
        )
        bot_tokens[config["firm_id"]] = config["bot_token"]

    if not bot_tokens:
        logger.error("no_bots_configured")
        return

    # Graceful shutdown
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(adapter.stop_all()))

    logger.info("discord_service_started", bot_count=len(bot_tokens))
    await adapter.start_all(bot_tokens)


if __name__ == "__main__":
    asyncio.run(main())
