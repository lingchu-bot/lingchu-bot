from ..database import client
from ..database.model import models


async def check_feat_status(login_id: int) -> bool:
    """检查功能开关状态，返回True表示开启，False表示关闭"""
    _, found = await client.get_one(
        model=models.LoginInfo, filters={"login_id": login_id, "feat_status": True}
    )
    return found
