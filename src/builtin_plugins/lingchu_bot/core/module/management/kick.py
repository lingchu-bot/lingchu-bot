import re

from nonebot import logger, on_startswith
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot_plugin_alconna.uniseg import UniMessage

from ...utils.auth import check_permission_and_status

# ================= 工具函数 =================


def parse_kick_ids(raw_message: str) -> list[str]:
    """
    解析踢人命令，返回用户id列表
    支持格式：
    1. 踢[CQ:at,qq=123456,name=xxx] [CQ:at,qq=654321,name=yyy]
    2. 踢123456 654321
    """
    pattern_at = r"踢((?:\[CQ:at,qq=\d+(?:,name=[^\]]+)?\] ?)+)"
    pattern_plain = r"踢 ?((?:\d+ ?)+)"
    match = re.search(pattern_at, raw_message)
    if match:
        at_block = match.group(1).strip()
        return re.findall(r"\[CQ:at,qq=(\d+)", at_block)
    match = re.search(pattern_plain, raw_message)
    if match:
        ids_block = match.group(1).strip()
        return [uid for uid in ids_block.split() if uid.isdigit()]
    return []


def get_display(uid: str, raw_message: str) -> str:
    """
    优先返回@name，无name则返回qq号
    """
    pattern = rf"\[CQ:at,qq={uid}(?:,name=([^\]]+))?\]"
    match = re.search(pattern, raw_message)
    if match and match.group(1):
        return f"@{match.group(1)}"
    if uid:
        return uid
    return ""


# ================= 指令注册 =================

kick_cmd = on_startswith("踢", priority=5, block=True)

# ================= 事件处理 =================


@kick_cmd.handle()
async def handle_kick(bot: Bot, event: GroupMessageEvent) -> None:
    """
    处理踢人命令，支持多用户和单用户
    """
    user_ids = parse_kick_ids(event.raw_message)
    if not user_ids:
        await UniMessage.text(
            "格式错误，请使用：踢@某人 或 踢[QQ号]\nTip: 多个请用空格分隔"
        ).send(reply_to=True)
        return
    if not await check_permission_and_status(event, "踢人"):
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
