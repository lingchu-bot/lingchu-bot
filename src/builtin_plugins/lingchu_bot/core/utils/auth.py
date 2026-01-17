from ..database import client
from ..database.model import models


async def check_feat_status() -> bool:
    """检查功能开关状态，返回True表示开启，False表示关闭"""
    return bool(
        await client.get_one(model=models.LoginInfo, filters={"feat_status": True})
        is not None
    )
