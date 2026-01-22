from nonebot import logger, on_startswith
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot_plugin_alconna.uniseg import UniMessage

from ...utils.check import check_role_permission
from .utils.parse_id import (
    get_display,
    parse_ids_and_time,
    parse_ids_by_cmd,
)

# ================= 指令注册 =================

ban_cmd = on_startswith("禁言", priority=5, block=True)
whole_ban_cmd = on_startswith("全体禁言", priority=5, block=True)
unban_cmd = on_startswith("解禁", priority=5, block=True)
whole_unban_cmd = on_startswith("全体解禁", priority=5, block=True)


# ================= 事件处理 =================
@ban_cmd.handle()
async def handle_mute(bot: Bot, event: GroupMessageEvent) -> None:
    """
    处理禁言命令，支持多用户和单用户
    """
    user_ids, mute_time = parse_ids_and_time(event.raw_message, ["禁言"])
    if not user_ids or mute_time is None:
        await UniMessage.text(
            "格式错误，请使用：禁言@某人 时间（单位：秒）或 禁言[QQ号] 时间（单位：秒）"
            "\nTip: 多个请用空格分隔"
        ).send(reply_to=True)
        return
    if not await check_role_permission(
        event, {"admin", "owner", "super"}, inherit=True
    ):
        await UniMessage.text("权限不足，仅管理员及以上可执行此操作").send(
            reply_to=True
        )
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
        except ActionFailed as e:
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
    if not await check_role_permission(
        event, {"admin", "owner", "super"}, inherit=True
    ):
        await UniMessage.text("权限不足，仅管理员及以上可执行此操作").send(
            reply_to=True
        )
        return
    try:
        await bot.set_group_whole_ban(group_id=event.group_id, enable=True)
        await UniMessage.text("全体禁言成功").send(reply_to=True)
    except ActionFailed as e:
        logger.error(f"全体禁言失败: {e}")
        await UniMessage.text("全体禁言失败").send(reply_to=True)


@unban_cmd.handle()
async def handle_unmute(bot: Bot, event: GroupMessageEvent) -> None:
    """
    处理解禁命令，支持多用户和单用户
    """
    user_ids = parse_ids_by_cmd(event.raw_message, ["解禁"])
    if not user_ids:
        await UniMessage.text(
            "格式错误，请使用：解禁@某人 或 解禁[QQ号]\nTip: 多个请用空格分隔"
        ).send(reply_to=True)
        return
    if not await check_role_permission(
        event, {"admin", "owner", "super"}, inherit=True
    ):
        await UniMessage.text("权限不足，仅管理员及以上可执行此操作").send(
            reply_to=True
        )
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
        except ActionFailed as e:
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
    if not await check_role_permission(
        event, {"admin", "owner", "super"}, inherit=True
    ):
        await UniMessage.text("权限不足，仅管理员及以上可执行此操作").send(
            reply_to=True
        )
        return
    try:
        await bot.set_group_whole_ban(group_id=event.group_id, enable=False)
        await UniMessage.text("全体解禁成功").send(reply_to=True)
    except ActionFailed as e:
        logger.error(f"全体解禁失败: {e}")
        await UniMessage.text("全体解禁失败").send(reply_to=True)
