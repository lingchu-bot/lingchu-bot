from nonebot import logger, on_startswith
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot_plugin_alconna.uniseg import UniMessage

from ...database import client
from ...database.model import models
from ...utils.auth import check_permission_and_status

feat_status_cmd = on_startswith("开机", priority=1, block=True)
unfeat_status_cmd = on_startswith("关机", priority=1, block=True)


@feat_status_cmd.handle()
async def handle_feat_status(event: GroupMessageEvent) -> None:
    if not await check_permission_and_status(
        event, mode="permission", send_reply=False
    ):
        return
    result = await client.update(
        model=models.LoginInfo,
        filters={"login_id": event.self_id},
        values={"feat_status": True},
    )
    logger.debug(
        f"{event.self_id}收到系统功能开关指令: {event.raw_message} "
        f"来自用户: {event.user_id}在群: {event.group_id}"
    )
    if result:
        await UniMessage.text("已开机").send(reply_to=True)
    else:
        await UniMessage.text("开机失败，请重试或联系管理员").send(reply_to=True)


@unfeat_status_cmd.handle()
async def handle_unfeat_status(event: GroupMessageEvent) -> None:
    if not await check_permission_and_status(
        event, mode="permission", send_reply=False
    ):
        return
    result = await client.update(
        model=models.LoginInfo,
        filters={"login_id": event.self_id},
        values={"feat_status": False},
    )
    logger.debug(
        f"{event.self_id}收到系统功能开关指令: {event.raw_message} "
        f"来自用户: {event.user_id}在群: {event.group_id}"
    )
    if result:
        await UniMessage.text("已关机").send(reply_to=True)
    else:
        await UniMessage.text("关机失败，请重试或联系管理员").send(reply_to=True)
