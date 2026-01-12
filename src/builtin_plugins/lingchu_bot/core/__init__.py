from nonebot.log import logger


def check_init_status() -> bool:
    """机器人初次启动检查和配置"""
    # 检查逻辑
    return True


def index_init() -> None:
    """机器人核心部分初始化索引"""
    match check_init_status():
        case True:
            logger.info("使用用户配置启动")
            try:
                logger.debug("开始载入初始化模块")
                from .module.initial import sync as sync
            except Exception as e:  # noqa: BLE001
                logger.error(f"载入初始化模块失败: {e}")
            try:
                logger.debug("开始载入管理模块")
                from .module import management as management
            except Exception as e:  # noqa: BLE001
                logger.error(f"载入管理模块失败: {e}")
        case False:
            logger.info("首次使用，正在引导配置\n")
            # from .module.initial import guide as guide
        case None:
            logger.error("配置错误或损坏\n")
