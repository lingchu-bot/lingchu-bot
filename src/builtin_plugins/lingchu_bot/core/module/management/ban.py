import re

from nonebot import logger, on_startswith
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot_plugin_alconna.uniseg import UniMessage

from ...utils.auth import check_permission_and_status

# ================= 工具函数 =================


def parse_ids_and_time(raw_message: str) -> tuple[list[str], int | None]:
    """
    解析禁言命令，返回用户id列表和禁言时长
    支持格式：
    1. 禁言[CQ:at,qq=123456,name=xxx] [CQ:at,qq=654321,name=yyy] 60
    2. 禁言123456 654321 60
    """
    pattern_at = r"禁言((?:\[CQ:at,qq=\d+(?:,name=[^\]]+)?\] ?)+)(\d+)"
    pattern_plain = r"禁言 ?((?:\d+ ?)+)(\d+)"
    match = re.search(pattern_at, raw_message)
    if match:
        at_block = match.group(1).strip()
        mute_time = int(match.group(2))
        return re.findall(r"\[CQ:at,qq=(\d+)", at_block), mute_time
    match = re.search(pattern_plain, raw_message)
    if match:
        ids_block = match.group(1).strip()
        mute_time = int(match.group(2))
        return [uid for uid in ids_block.split() if uid.isdigit()], mute_time
    return [], None


def parse_ids(raw_message: str) -> list[str]:
    """
    解析解禁命令，返回用户id列表
    支持格式：
    1. 解禁[CQ:at,qq=123456,name=xxx] [CQ:at,qq=654321,name=yyy]
    2. 解禁123456 654321
    """
    pattern_at = r"解禁((?:\[CQ:at,qq=\d+(?:,name=[^\]]+)?\] ?)+)"
    pattern_plain = r"解禁 ?((?:\d+ ?)+)"
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

ban_cmd = on_startswith("禁言", priority=5, block=True)
whole_ban_cmd = on_startswith("全体禁言", priority=5, block=True)
unban_cmd = on_startswith("解禁", priority=5, block=True)
whole_unban_cmd = on_startswith("全体解禁", priority=5, block=True)


# ================= 事件处理 =================


# TODO: 增强：请求数据库配置信息，拓展功能，避免硬编码
@ban_cmd.handle()
async def handle_mute(bot: Bot, event: GroupMessageEvent) -> None:
    """
    处理禁言命令，支持多用户和单用户
    """
    user_ids, mute_time = parse_ids_and_time(event.raw_message)
    if not user_ids or mute_time is None:
        await UniMessage.text(
            "格式错误，请使用：禁言@某人 时间（单位：秒）或 禁言[QQ号] 时间（单位：秒）"
            "\nTip: 多个请用空格分隔"
        ).send(reply_to=True)
        return
    if not await check_permission_and_status(event, "禁言"):
        return
    success = []
    failed = []
    for uid in user_ids:
        try:
            logger.debug(
                f"{event.self_id}收到禁言指令: {event.raw_message} "
                f"来自用户: {event.user_id} 目标用户: {uid} "
                f"时间：{mute_time} 在群: {event.group_id}"
            )
            await bot.set_group_ban(
                group_id=event.group_id, user_id=int(uid), duration=mute_time
            )
            success.append(get_display(uid, event.raw_message))
        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"禁言用户{uid}失败: {e}")
            failed.append(get_display(uid, event.raw_message))
    msg = []
    if success:
        msg.append(f"禁言成功: {'、'.join(success)}")
    if failed:
        msg.append(f"禁言失败: {'、'.join(failed)}")
    await UniMessage.text("\n".join(msg) if msg else "无用户被禁言").send(reply_to=True)


@whole_ban_cmd.handle()
async def handle_whole_mute(bot: Bot, event: GroupMessageEvent) -> None:
    """
    处理全体禁言命令
    """
    if not await check_permission_and_status(event, "全体禁言"):
        return
    await bot.set_group_whole_ban(group_id=event.group_id, enable=True)
    await UniMessage.text("全体禁言成功").send(reply_to=True)


@unban_cmd.handle()
async def handle_unmute(bot: Bot, event: GroupMessageEvent) -> None:
    """
    处理解禁命令，支持多用户和单用户
    """
    user_ids = parse_ids(event.raw_message)
    if not user_ids:
        await UniMessage.text(
            "格式错误，请使用：解禁@某人 或 解禁[QQ号]\nTip: 多个请用空格分隔"
        ).send(reply_to=True)
        return
    if not await check_permission_and_status(event, "解禁"):
        return
    success = []
    failed = []
    for uid in user_ids:
        try:
            logger.debug(
                f"{event.self_id}收到解禁指令: {event.raw_message} "
                f"来自用户: {event.user_id} 目标用户: {uid} 在群: {event.group_id}"
            )
            await bot.set_group_ban(
                group_id=event.group_id, user_id=int(uid), duration=0
            )
            success.append(get_display(uid, event.raw_message))
        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"解禁用户{uid}失败: {e}")
            failed.append(get_display(uid, event.raw_message))
    msg = []
    if success:
        msg.append(f"解禁成功: {'、'.join(success)}")
    if failed:
        msg.append(f"解禁失败: {'、'.join(failed)}")
    await UniMessage.text("\n".join(msg) if msg else "无用户被解禁").send(reply_to=True)


@whole_unban_cmd.handle()
async def handle_whole_unmute(bot: Bot, event: GroupMessageEvent) -> None:
    """
    处理全体解禁命令
    """
    if not await check_permission_and_status(event, "全体解禁"):
        return
    await bot.set_group_whole_ban(group_id=event.group_id, enable=False)
    await UniMessage.text("全体解禁成功").send(reply_to=True)


# from nonebot_plugin_alconna import on_alconna
