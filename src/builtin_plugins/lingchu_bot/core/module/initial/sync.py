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
    """
    在 Bot 建立连接时更新或创建对应的 LoginInfo 记录，标记为已登录并记录登录昵称与已加载插件列表。
    
    该处理器从 bot 获取登录昵称，然后在数据库中更新或创建 models.LoginInfo 条目：以 bot.self_id 作为过滤条件，设置 login_status 为 True、login_name 为 bot 的昵称，并保存当前已加载插件列表。
    
    Parameters:
        bot (Bot): 触发连接事件的 Bot 实例。
    """
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
    # logger.info("建立连接，开始更新数据库")
    # friend_list: str = (await bot.get_friend_list())["nickname"]
    # await client.update_or_create(
    #     model=models.ChatList,
    #     filters={"login_id": bot.self_id},
    #     defaults={
    #         "login_id": bot.self_id,
    #         "login_name": friend_list,
    #         "login_status": True,
    #         "loaded_plugins": plugins,
    #     },
    # )


@driver.on_bot_disconnect
async def disconnect_sync(bot: Bot) -> None:
    """
    处理机器人断开连接时的数据同步，将对应登录记录标记为离线。
    
    Parameters:
        bot (Bot): 发生断开连接的机器人实例，用于定位并更新对应的登录记录。
    """
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
    """
    在系统关闭时将所有标记为已登录的记录更新为未登录状态。
    
    将 LoginInfo 表中 login_status 为 True 的记录设为 False，以在应用退出时把登录状态同步到数据库。
    """
    logger.info("退出准备，开始处理数据库事项")
    await client.update(
        model=models.LoginInfo,
        filters={"login_status": True},
        values={
            "login_status": False,
        },
    )