import logging
from typing import Optional

import botpy
from botpy.message import GroupMessage, Message, DirectMessage

from ..config import config
from .handlers.command import CommandHandler

logger = logging.getLogger(__name__)


class BotClient(botpy.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler: Optional[CommandHandler] = None

    async def on_ready(self):
        logger.info(f"Bot {self.robot.name} is ready!")
        self.command_handler = CommandHandler()

    async def on_at_message_create(self, message: Message):
        logger.debug(f"Received channel message: {message.content}")
        await self._handle_message(message)

    async def on_group_at_message_create(self, message: GroupMessage):
        logger.debug(f"Received group message: {message.content}")
        await self._handle_message(message)

    async def on_direct_message_create(self, message: DirectMessage):
        logger.debug(f"Received direct message: {message.content}")
        await self._handle_message(message)

    async def _handle_message(self, message):
        if self.command_handler is None:
            logger.warning("Command handler not initialized")
            return
        
        try:
            await self.command_handler.handle(message)
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await self._send_error_reply(message, str(e))

    async def _send_error_reply(self, message, error: str):
        try:
            reply = f"❌ 处理请求时发生错误: {error}"
            if hasattr(message, "reply"):
                await message.reply(content=reply)
            else:
                await self._send_fallback_reply(message, reply)
        except Exception as e:
            logger.error(f"Failed to send error reply: {e}")

    async def _send_fallback_reply(self, message, content: str):
        if isinstance(message, GroupMessage):
            await self.api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0,
                msg_id=message.id,
                content=content,
            )
        elif isinstance(message, DirectMessage):
            await self.api.post_dms(
                guild_id=message.guild_id,
                msg_type=0,
                msg_id=message.id,
                content=content,
            )
        elif isinstance(message, Message):
            await message.reply(content=content)


def run_bot():
    if not config.QQ_BOT_APPID or not config.QQ_BOT_TOKEN:
        raise ValueError("QQ_BOT_APPID and QQ_BOT_TOKEN must be configured")
    
    intents = botpy.Intents(
        public_messages=True,
        public_guild_messages=True,
        guild_messages=True,
        direct_message=True,
        groups=True,
    )
    
    client = BotClient(intents=intents)
    
    logger.info("Starting QQ Bot...")
    client.run(appid=config.QQ_BOT_APPID, token=config.QQ_BOT_TOKEN)
