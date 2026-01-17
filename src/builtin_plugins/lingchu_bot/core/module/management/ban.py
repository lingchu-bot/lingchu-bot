from nonebot import logger, on_startswith
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot_plugin_alconna.uniseg import UniMessage

from ...utils.auth import check_feat_status

ban_cmd = on_startswith("禁言", priority=5, block=True)
whole_ban_cmd = on_startswith("全体禁言", priority=5, block=True)
unban_cmd = on_startswith("解禁", priority=5, block=True)
whole_unban_cmd = on_startswith("全体解禁", priority=5, block=True)


# TODO: 增强：请求开关机(feat_status)状态、权限验证等
@ban_cmd.handle()
async def handle_mute(bot: Bot, event: GroupMessageEvent) -> None:
    import re

    # 支持两种格式：
    # 1. 禁言[CQ:at,qq=123456,name=xxx] 60
    # 2. 禁言123456 60
    pattern_at = r"禁言\[CQ:at,qq=(\d+),name=[^\]]+\] (\d+)"
    pattern_plain = r"禁言(\d+) (\d+)"
    match = re.search(pattern_at, event.raw_message)
    if not match:
        match = re.search(pattern_plain, event.raw_message)
    if not match:
        await UniMessage.text(
            "格式错误，请使用：禁言@某人 时间（单位：秒）或 禁言QQ号 时间（单位：秒）"
        ).send(reply_to=True)
        return
    role_user = event.sender.role  # 获取用户角色(权限等级)，owner 或 admin 或 member

    # 权限验证：仅群主和管理员可用
    if role_user not in ("owner", "admin"):
        await UniMessage.text("权限不足，仅群主和管理员可用").send(reply_to=True)
        return

    if not await check_feat_status():
        await UniMessage.text("禁言功能未开启").send(reply_to=True)
        return

    target_user = int(match.group(1))
    mute_time = int(match.group(2))
    logger.debug(
        f"{event.self_id}收到禁言指令: {event.raw_message} "
        f"来自用户: {event.user_id} 目标用户: {target_user} "
        f"时间：{mute_time} 在群: {event.group_id}"
    )
    if await bot.set_group_ban(
        group_id=event.group_id, user_id=target_user, duration=mute_time
    ):
        await UniMessage.text("禁言成功").send(reply_to=True)


@whole_ban_cmd.handle()
async def handle_whole_mute(bot: Bot, event: GroupMessageEvent) -> None:
    if await bot.set_group_whole_ban(group_id=event.group_id, enable=True):
        await UniMessage.text("全体禁言成功").send(reply_to=True)


@unban_cmd.handle()
async def handle_unmute(bot: Bot, event: GroupMessageEvent) -> None:
    import re

    # 支持两种格式：
    # 1. 解禁[CQ:at,qq=123456,name=xxx]
    # 2. 解禁123456
    pattern_at = r"解禁\[CQ:at,qq=(\d+),name=[^\]]+\]"
    pattern_plain = r"解禁(\d+)"
    match = re.search(pattern_at, event.raw_message)
    if not match:
        match = re.search(pattern_plain, event.raw_message)
    if not match:
        await UniMessage.text("格式错误，请使用：解禁@某人 或 解禁QQ号").send(
            reply_to=True
        )
        return
    target_user = int(match.group(1))
    logger.debug(
        f"{event.self_id}收到解禁指令: {event.raw_message} "
        f"来自用户: {event.user_id} 目标用户: {target_user} 在群: {event.group_id}"
    )
    if await bot.set_group_ban(
        group_id=event.group_id, user_id=target_user, duration=0
    ):
        await UniMessage.text("解禁成功").send(reply_to=True)


@whole_unban_cmd.handle()
async def handle_whole_unmute(bot: Bot, event: GroupMessageEvent) -> None:
    if await bot.set_group_whole_ban(group_id=event.group_id, enable=False):
        await UniMessage.text("全体解禁成功").send(reply_to=True)


# from nonebot_plugin_alconna import on_alconna
