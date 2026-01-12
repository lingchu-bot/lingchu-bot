from pathlib import Path

import nonebot
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="lingchu-bot-core",
    description="lingchu-bot核心插件",
    usage="",
    type="application",
    supported_adapters={"nonebot.adapters.onebot.v11"},
    homepage="https://github.com/lingchu-bot/lingchu-bot",
    config=Config,
)

config = get_plugin_config(Config)

from . import core

core.index_init()

sub_plugins = nonebot.load_plugins(
    str(Path(__file__).parent.joinpath("plugins").resolve())
)


# 公共接口
from .core.api import apimount as apimount
