"""Discord bot — white-label bot instance for a single firm."""

import discord
from discord import app_commands
from discord.ext import commands

from neuraprop_core.logging import get_logger

logger = get_logger(__name__)


class NeuraPropBot(commands.Bot):
    """White-label Discord bot for a single prop firm.

    Each firm gets their own bot instance with custom branding.
    The bot listens for messages in support channels and slash commands.
    """

    def __init__(
        self,
        firm_id: str,
        firm_name: str,
        support_channel_ids: list[int] | None = None,
        **kwargs,
    ):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            **kwargs,
        )

        self.firm_id = firm_id
        self.firm_name = firm_name
        self.support_channel_ids = set(support_channel_ids or [])
        self._message_callback = None

    def set_message_callback(self, callback):
        """Set the callback for processing inbound messages.

        callback(firm_id, channel_user_id, content, channel_ref, attachments) -> str
        """
        self._message_callback = callback

    async def setup_hook(self):
        """Called when the bot is starting up — register slash commands."""
        self.tree.add_command(self._support_command())
        self.tree.add_command(self._status_command())
        self.tree.add_command(self._escalate_command())
        await self.tree.sync()
        logger.info("discord_bot_ready", firm_id=self.firm_id, firm=self.firm_name)

    async def on_ready(self):
        logger.info(
            "discord_bot_connected",
            firm_id=self.firm_id,
            bot_user=str(self.user),
            guilds=len(self.guilds),
        )

    async def on_message(self, message: discord.Message):
        """Handle direct messages and support channel messages."""
        if message.author.bot:
            return

        # Process commands first
        await self.process_commands(message)

        # Handle DMs
        if isinstance(message.channel, discord.DMChannel):
            await self._handle_support_message(message)
            return

        # Handle messages in designated support channels
        if message.channel.id in self.support_channel_ids:
            await self._handle_support_message(message)

    async def _handle_support_message(self, message: discord.Message):
        """Process a support message through the agent pipeline."""
        if not self._message_callback:
            logger.warning("no_message_callback", firm_id=self.firm_id)
            return

        # Show typing indicator while processing
        async with message.channel.typing():
            try:
                attachments = [
                    {"filename": a.filename, "url": a.url, "size": a.size}
                    for a in message.attachments
                ]

                # Determine channel ref for conversation threading
                if isinstance(message.channel, discord.DMChannel):
                    channel_ref = f"dm_{message.author.id}"
                elif isinstance(message.channel, discord.Thread):
                    channel_ref = f"thread_{message.channel.id}"
                else:
                    channel_ref = f"channel_{message.channel.id}_{message.author.id}"

                response = await self._message_callback(
                    firm_id=self.firm_id,
                    channel_user_id=str(message.author.id),
                    display_name=message.author.display_name,
                    content=message.content,
                    channel_ref=channel_ref,
                    attachments=attachments,
                )

                # Split long responses (Discord 2000 char limit)
                for chunk in _split_message(response):
                    await message.reply(chunk, mention_author=False)

            except Exception:
                logger.exception("discord_message_error", firm_id=self.firm_id)
                await message.reply(
                    "I'm experiencing a temporary issue. Please try again in a moment, "
                    "or type `/escalate` to reach our support team.",
                    mention_author=False,
                )

    def _support_command(self) -> app_commands.Command:
        @app_commands.command(name="support", description="Start a support conversation")
        @app_commands.describe(question="What do you need help with?")
        async def support(interaction: discord.Interaction, question: str):
            await interaction.response.defer(thinking=True)

            if self._message_callback:
                response = await self._message_callback(
                    firm_id=self.firm_id,
                    channel_user_id=str(interaction.user.id),
                    display_name=interaction.user.display_name,
                    content=question,
                    channel_ref=f"slash_{interaction.user.id}",
                    attachments=[],
                )
                await interaction.followup.send(response)
            else:
                await interaction.followup.send("Support is currently unavailable.")

        return support

    def _status_command(self) -> app_commands.Command:
        @app_commands.command(name="status", description="Check your account or ticket status")
        async def status(interaction: discord.Interaction):
            await interaction.response.defer(thinking=True)

            if self._message_callback:
                response = await self._message_callback(
                    firm_id=self.firm_id,
                    channel_user_id=str(interaction.user.id),
                    display_name=interaction.user.display_name,
                    content="What is the status of my account and any open tickets?",
                    channel_ref=f"slash_{interaction.user.id}",
                    attachments=[],
                )
                await interaction.followup.send(response)
            else:
                await interaction.followup.send("Support is currently unavailable.")

        return status

    def _escalate_command(self) -> app_commands.Command:
        @app_commands.command(name="escalate", description="Request to speak with a human agent")
        @app_commands.describe(reason="Why do you need human support?")
        async def escalate(interaction: discord.Interaction, reason: str = ""):
            await interaction.response.defer(thinking=True)

            if self._message_callback:
                content = f"I want to speak with a human agent. {reason}".strip()
                response = await self._message_callback(
                    firm_id=self.firm_id,
                    channel_user_id=str(interaction.user.id),
                    display_name=interaction.user.display_name,
                    content=content,
                    channel_ref=f"slash_{interaction.user.id}",
                    attachments=[],
                )
                await interaction.followup.send(response)
            else:
                await interaction.followup.send(
                    "Escalation request received. A team member will reach out shortly."
                )

        return escalate


def _split_message(text: str, max_length: int = 2000) -> list[str]:
    """Split a message into chunks that fit Discord's character limit."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break

        # Try to split at a newline
        split_idx = text.rfind("\n", 0, max_length)
        if split_idx == -1:
            # Fall back to space
            split_idx = text.rfind(" ", 0, max_length)
        if split_idx == -1:
            # Hard split
            split_idx = max_length

        chunks.append(text[:split_idx])
        text = text[split_idx:].lstrip()

    return chunks
