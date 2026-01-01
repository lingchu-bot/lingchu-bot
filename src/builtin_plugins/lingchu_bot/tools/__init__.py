from typing import Any, Literal


async def get_login_info(
    bot: Any,
    field: Literal["user_id", "nickname", "all"] = "all",
) -> dict[str, Any] | int | str:
    """
    获取登录信息函数

    Args:
        bot: 机器人实例
        field: 指定返回的字段

    Returns:
        根据field返回对应数据
    """
    # 获取原始数据
    login_info = await bot.get_login_info()

    # 提取数据
    user_id: int = login_info["user_id"]
    nickname: str = login_info["nickname"]

    # 根据field返回
    match field:
        case "all":
            return {"user_id": user_id, "nickname": nickname}
        case "user_id":
            return user_id
        case "nickname":
            return nickname
        case _:
            raise TypeError
