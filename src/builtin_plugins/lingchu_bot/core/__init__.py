from .api.apimount import *  # noqa: F403


def check_init_status() -> bool:
    """机器人初次启动检查和配置"""
    from .module.initial import sync as sync

    return True


def index_init() -> None:
    """机器人核心部分初始化索引"""
    check_init_status()
