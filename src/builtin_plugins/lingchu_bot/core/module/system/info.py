from nonebot import logger, on_startswith
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot_plugin_alconna.uniseg import UniMessage

from ...utils.auth import check_feat_status, check_permission_and_status

status_cmd = on_startswith(("机器状态", "机器信息"), priority=5, block=True)


@status_cmd.handle()
async def handle_status(event: GroupMessageEvent) -> None:
    if not await check_permission_and_status(
        event, mode="permission", send_reply=False
    ):
        return
    logger.debug(
        f"{event.self_id}收到获取机器信息指令: {event.raw_message} "
        f"来自用户: {event.user_id}在群: {event.group_id}"
    )
    status = await check_feat_status(event.self_id)
    if status:
        await UniMessage.text("====机器信息====\n\n状态：已开机").send()
    else:
        await UniMessage.text("====机器信息====\n\n状态：已关机").send()
