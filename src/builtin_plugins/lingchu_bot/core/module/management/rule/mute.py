from typing import Any

from nonebot import on_startswith
from nonebot.rule import RegexRule, Rule, StartswithRule


class MuteRuleHandler:
    def __init__(self) -> None:
        self.mute_rule = Rule(
            StartswithRule(msg=("禁言", "解禁")), RegexRule(r"(?:^|\s|[^\d.])\d+$")
        )

    def mute(self, value: str) -> Any:
        if value == "禁言":
            return on_startswith("禁言", rule=self.mute_rule, priority=5, block=True)
        if value == "解禁":
            return on_startswith("解禁", rule=self.mute_rule, priority=5, block=True)
        return None

    def whole_mute(self, value: str) -> Any:
        if value == "禁言":
            return on_startswith("禁言", rule=self.mute_rule, priority=5, block=True)
        if value == "解禁":
            return on_startswith("解禁", rule=self.mute_rule, priority=5, block=True)
        return None
