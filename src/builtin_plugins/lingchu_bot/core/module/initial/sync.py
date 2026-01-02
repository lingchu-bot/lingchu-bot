"""数据同步"""

from database import client
from nonebot import require
from nonebot.adapters.onebot.v11 import Bot
from nonebot.log import logger
from tools import get_login_info

from ...database.model import models

require("lingchu-bot")

from nonebot import get_driver

driver = get_driver()


@driver.on_bot_connect
async def sync(bot: Bot) -> None:
    logger.info("建立连接，开始更新数据库")
    login_id = await get_login_info(bot, "user_id")
    login_name = await get_login_info(bot, "nickname")
    await client.update_or_create(
        model=models.LoginInfo,
        filters={"login_id": login_id},
        defaults={
            "login_name": login_name,
            "core_version": "0.0.0",
            "login_status": 1,
            "sub_plugins": ["plugin_a", "plugin_b"],
            "core_plugins": ["core_plugin1", "core_plugin2"],
        },
    )
