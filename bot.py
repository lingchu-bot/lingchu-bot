import nonebot

# from nonebot.adapters.telegram import Adapter as TELEGRAMAdapter
# from nonebot.adapters.console import Adapter as CONSOLEAdapter
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

init_config = {"LOCALSTORE_USE_CWD": "True", "DRIVER": "~fastapi+~httpx+~websockets"}
nonebot.init(**init_config)


driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)
# driver.register_adapter(TELEGRAMAdapter)
# driver.register_adapter(CONSOLEAdapter)


# nonebot.load_builtin_plugins("single_session")
# 单会话插件,与nonebot-plugin-waiter冲突
nonebot.load_from_toml("pyproject.toml")
nonebot.load_plugins("src/builtin_plugins")

if __name__ == "__main__":
    nonebot.run()
