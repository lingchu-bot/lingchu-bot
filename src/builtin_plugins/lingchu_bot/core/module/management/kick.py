from nonebot import logger, on_startswith
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot_plugin_alconna.uniseg import UniMessage

from ...utils.check import check_role_permission
from .utils.parse_id import (
    get_display,
    parse_ids_by_cmd,
)

# ================= 指令注册 =================

kick_cmd = on_startswith("踢", priority=5, block=True)

# ================= 事件处理 =================


@kick_cmd.handle()
async def handle_kick(bot: Bot, event: GroupMessageEvent) -> None:
    """
    处理踢人命令，支持多用户和单用户
    """
    user_ids = parse_ids_by_cmd(event.raw_message, ["踢"])
    if not user_ids:
        await UniMessage.text(
            "格式错误，请使用：踢@某人 或 踢[QQ号]\nTip: 多个请用空格分隔"
        ).send(reply_to=True)
        return
    # 检查是否为管理员或更高权限
    if not await check_role_permission(
        event, {"admin", "owner", "super"}, inherit=True
    ):
        return
    success = []
    failed = []
    for uid in user_ids:
        try:
            logger.debug(
                f"{event.self_id}收到踢人指令: {event.raw_message} "
                f"来自用户: {event.user_id} 目标用户: {uid} 在群: {event.group_id}"
            )
            await bot.set_group_kick(
                group_id=event.group_id, user_id=int(uid), reject_add_request=False
            )
            success.append(get_display(uid, event.raw_message))
        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"踢出用户{uid}失败: {e}")
            failed.append(get_display(uid, event.raw_message))
    msg = []
    if success:
        msg.append(f"踢出成功: {'、'.join(success)}")
    if failed:
        msg.append(f"踢出失败: {'、'.join(failed)}")
    await UniMessage.text("\n".join(msg) if msg else "无用户被踢出").send(reply_to=True)
