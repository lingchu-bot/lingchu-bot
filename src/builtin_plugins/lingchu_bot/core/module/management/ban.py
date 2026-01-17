from nonebot import logger, on_startswith
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot_plugin_alconna.uniseg import UniMessage

ban_cmd = on_startswith("禁言", priority=5, block=True)
whole_ban_cmd = on_startswith("全体禁言", priority=5, block=True)
unban_cmd = on_startswith("解禁", priority=5, block=True)
whole_unban_cmd = on_startswith("全体解禁", priority=5, block=True)


# TODO: 增强：请求开关机状态、权限验证等
@ban_cmd.handle()
async def handle_mute(bot: Bot, event: GroupMessageEvent) -> None:
    import re

    pattern = r"禁言\[CQ:at,qq=(\d+),name=[^\]]+\] (\d+)"
    match = re.search(pattern, event.raw_message)
    if not match:
        await UniMessage.text("格式错误，请使用：禁言@某人 时间（单位：秒）").send(
            at_sender=True, reply_to=True
        )
        return
    target_user = int(match.group(1))
    mute_time = int(match.group(2))
    logger.debug(
        f"{event.self_id}收到禁言指令: {event.raw_message}\
来自用户: {event.user_id}目标用户: {target_user}时间：{mute_time}在群: {event.group_id}"
    )
    if await bot.set_group_ban(
        group_id=event.group_id, user_id=target_user, duration=mute_time
    ):
        await UniMessage.text("禁言成功").send(at_sender=True, reply_to=True)


@whole_ban_cmd.handle()
async def handle_whole_mute(bot: Bot, event: GroupMessageEvent) -> None:
    if await bot.set_group_whole_ban(group_id=event.group_id, enable=True):
        await UniMessage.text("全体禁言成功").send(at_sender=True, reply_to=True)


@unban_cmd.handle()
async def handle_unmute(bot: Bot, event: GroupMessageEvent) -> None:
    import re

    # 匹配格式: 禁言[CQ:at,qq=123456,name=xxx] 60
    pattern = r"解禁\[CQ:at,qq=(\d+),name=[^\]]+\] "
    match = re.search(pattern, event.raw_message)
    if not match:
        await UniMessage.text("格式错误，请使用：解禁@某人").send(
            at_sender=True, reply_to=True
        )
        return
    target_user = int(match.group(1))
    logger.debug(
        f"{event.self_id}收到解禁指令: {event.raw_message}\
来自用户: {event.user_id}目标用户: {target_user}在群: {event.group_id}"
    )
    if await bot.set_group_ban(
        group_id=event.group_id, user_id=target_user, duration=0
    ):
        await UniMessage.text("解禁成功").send(at_sender=True, reply_to=True)


@whole_unban_cmd.handle()
async def handle_whole_unmute(bot: Bot, event: GroupMessageEvent) -> None:
    if await bot.set_group_whole_ban(group_id=event.group_id, enable=False):
        await UniMessage.text("全体解禁成功").send(at_sender=True, reply_to=True)


# from nonebot_plugin_alconna import on_alconna
