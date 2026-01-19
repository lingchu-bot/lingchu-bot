from nonebot import logger
from nonebot.adapters.onebot.v11 import Event
from nonebot.message import event_postprocessor


# TODO: 实现发送事件的后处理器
@event_postprocessor
async def handle_send(event: Event) -> None:
    """msg事件后处理"""
    match event.post_type:
        case "message_sent":
            logger.debug(f"后处理自我消息: {event}")
        case "message":
            logger.debug(f"后处理用户消息: {event}")
        case _:
            pass
