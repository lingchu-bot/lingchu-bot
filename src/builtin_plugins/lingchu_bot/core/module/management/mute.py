from nonebot import logger, on_startswith
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.rule import Rule, StartswithRule
from nonebot_plugin_alconna.uniseg import UniMessage

ban_cmd = on_startswith(
    "禁言",
    rule=Rule(StartswithRule(msg=("禁言", "解禁", "全体禁言", "全体解禁"))),
    priority=5,
    block=True,
)
whole_ban_cmd = on_startswith(
    "全体禁言",
    rule=Rule(StartswithRule(msg=("禁言", "解禁", "全体禁言", "全体解禁"))),
    priority=5,
    block=True,
)
unban_cmd = on_startswith(
    "解禁",
    rule=Rule(StartswithRule(msg=("禁言", "解禁", "全体禁言", "全体解禁"))),
    priority=5,
    block=True,
)
whole_unban_cmd = on_startswith(
    "全体解禁",
    rule=Rule(StartswithRule(msg=("禁言", "解禁", "全体禁言", "全体解禁"))),
    priority=5,
    block=True,
)


# TODO: 实现具体功能
@ban_cmd.handle()
async def handle_mute(event: GroupMessageEvent) -> None:
    logger.debug(
        f"{event.self_id}收到禁言指令: {event.raw_message}\
来自用户: {event.user_id} 在群: {event.group_id}"
    )
    # 禁言\[CQ:at,qq=(\d+),name=([^\]]+)\] (\d+)
    await UniMessage.text("禁言成功").send(at_sender=True, reply_to=True)


@whole_ban_cmd.handle()
async def handle_whole_mute() -> None:
    message = UniMessage.text("全体禁言成功")
    await message.send(at_sender=True, reply_to=True)


@unban_cmd.handle()
async def handle_unmute() -> None:
    message = UniMessage.text("解禁成功")
    await message.send(at_sender=True, reply_to=True)


@whole_unban_cmd.handle()
async def handle_whole_unmute() -> None:
    message = UniMessage.text("全体解禁成功")
    await message.send(at_sender=True, reply_to=True)


# from nonebot_plugin_alconna import on_alconna
