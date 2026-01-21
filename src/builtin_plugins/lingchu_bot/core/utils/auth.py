from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot_plugin_alconna.uniseg import UniMessage

from ..database import client
from ..database.model import models


async def check_feat_status(login_id: int) -> bool:
    """检查功能开关状态，返回True表示开启，False表示关闭"""
    obj, status = await client.get_one(
        model=models.LoginInfo, filters={"login_id": login_id}
    )
    if not status or obj is None:
        return False
    return getattr(obj, "feat_status", False) is True


# 公共辅助函数：权限和功能状态检查
async def check_permission_and_status(
    event: GroupMessageEvent,
    mode: str = "all",  # 可选: "all"(默认)、"permission"、"status"
    *,
    send_reply: bool = True,  # 是否发送回复消息
    only_owner: bool = False,  # 是否仅群主可用
) -> bool:
    """
    检查权限和/或功能开关状态
    mode: "all" 检查两项，"permission" 只检查权限，"status" 只检查功能开关
    """
    # 权限检查
    if mode in ("all", "permission"):
        role = getattr(event.sender, "role", None)
        if only_owner:
            if role != "owner":
                if send_reply:
                    await UniMessage.text("权限不足，仅群主可用").send(reply_to=True)
                return False
        elif role not in ("owner", "admin"):
            if send_reply:
                await UniMessage.text("权限不足，仅群主和管理员可用").send(
                    reply_to=True
                )
            return False

    # 功能开关检查
    if mode in ("all", "status"):
        feat_on = await check_feat_status(event.self_id)
        if not feat_on:
            return False

    return True
