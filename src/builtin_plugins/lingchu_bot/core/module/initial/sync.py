"""数据同步"""

from nonebot import get_driver, get_loaded_plugins
from nonebot.adapters.onebot.v11 import Bot
from nonebot.log import logger

from ...database import client
from ...database.model import models

driver = get_driver()

plugins: list[str] = [plugin.name for plugin in get_loaded_plugins()]


@driver.on_bot_connect
async def connect_sync(bot: Bot) -> None:
    logger.info("建立连接，开始更新数据库")
    login_name: str = (await bot.get_login_info())["nickname"]
    await client.update_or_create(
        model=models.LoginInfo,
        filters={"login_id": bot.self_id},
        defaults={
            "login_id": bot.self_id,
            "login_name": login_name,
            "login_status": True,
            "loaded_plugins": plugins,
        },
    )


@driver.on_bot_disconnect
async def disconnect_sync(bot: Bot) -> None:
    logger.info("断开连接，开始更新数据库")
    await client.update_or_create(
        model=models.LoginInfo,
        filters={"login_id": bot.self_id},
        defaults={
            "login_status": False,
        },
    )


@driver.on_shutdown
async def shutdown_sync() -> None:
    logger.info("退出准备，开始处理数据库事项")
    await client.update(
        model=models.LoginInfo,
        filters={"login_status": True},
        values={
            "login_status": False,
        },
    )
