from nonebot import logger
from nonebot.message import run_postprocessor

from ...middleware.public import MessageSentEvent


# TODO: 实现发送事件的后处理器
@run_postprocessor
async def handle_send(event: MessageSentEvent) -> None:
    """msg事件后处理"""
    logger.debug(f"后处理自我消息: {event.message}")
