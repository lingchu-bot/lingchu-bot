"""数据同步"""

from nonebot import require
from nonebot.adapters.onebot.v11 import Bot
from nonebot.log import logger
from tools import get_login_info

require("lingchu-bot")

from nonebot import get_driver

driver = get_driver()


@driver.on_bot_connect
async def sync(bot: Bot) -> None:
    logger.info("建立连接，开始更新数据库")
    await get_login_info(bot, "all")
