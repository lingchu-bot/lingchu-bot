"""管理模块"""

from nonebot import on_command, require
from nonebot.permission import SUPERUSER
from nonebot.rule import RegexRule, Rule, StartswithRule

require("lingchu-bot")

MuteRule = Rule(StartswithRule(msg=("禁言", "解禁")), RegexRule(r"(?:^|\s|[^\d.])\d+$"))
MuteCmd = on_command(
    "禁言", rule=MuteRule, permission=SUPERUSER, priority=5, block=True
)
UnMuteCmd = on_command(
    "解禁", rule=MuteRule, permission=SUPERUSER, priority=5, block=True
)
