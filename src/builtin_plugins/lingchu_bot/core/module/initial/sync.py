"""数据库同步"""

from nonebot import require
from nonebot.adapters.onebot.v11 import Bot

require("lingchu-bot")


async def get_group_list(bot: Bot) -> list:
    return await bot.get_group_list()
