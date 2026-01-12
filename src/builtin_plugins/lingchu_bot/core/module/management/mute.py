from nonebot import on_command

from .rule.mute import MuteRuleHandler

mute_cmd = on_command(
    "禁言", rule=MuteRuleHandler().mute(value="禁言"), priority=5, block=True
)
