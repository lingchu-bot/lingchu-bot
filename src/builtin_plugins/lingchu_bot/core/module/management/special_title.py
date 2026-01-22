import re

from nonebot import logger, on_startswith
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot_plugin_alconna.uniseg import UniMessage

from ...utils.check import check_role_permission
from .utils import parse_id as parse

# ========== 指令注册 ==========
grant_title_cmd = on_startswith("授予头衔", priority=5, block=True)
revoke_title_cmd = on_startswith("剥夺头衔", priority=5, block=True)


@grant_title_cmd.handle()
async def handle_grant_title(bot: Bot, event: GroupMessageEvent) -> None:
    """
    处理授予头衔命令，支持多用户和单用户，格式：授予头衔@某人/QQ号 [头衔内容]
    """
    # 权限检查
    # 检查是否为管理员或更高权限
    if not await check_role_permission(
        event, {"admin", "owner", "super"}, inherit=True
    ):
        await UniMessage.text("仅管理员、群主和超管可用").send(reply_to=True)
        return
    # 机器人需为群主
    if (
        await bot.get_group_member_info(
            group_id=event.group_id, user_id=event.self_id, no_cache=True
        )
    )["role"] != "owner":
        await UniMessage.text("机器人不是群主，无法授予头衔！").send(reply_to=True)
        return
    # 解析用户id
    user_ids = parse.parse_ids_by_cmd(event.raw_message, ["授予头衔"])
    # 解析头衔内容
    # 支持格式：授予头衔@某人/QQ号 [头衔内容]
    # 头衔内容为命令最后一个空格后的内容，且必须为字符串
    special_title = ""
    # 优先匹配at格式，支持 [CQ:at,qq=...] 和 [at:qq=...] 两种格式
    pattern_at = r"(?:授予头衔)((?:\[(?:CQ:)?at,qq=\d+(?:,name=[^\]]+)?\]\s*)+)(.*)"
    match = re.match(pattern_at, event.raw_message)
    if match:
        special_title = match.group(2).strip()
    else:
        # 匹配纯数字格式
        pattern_plain = r"(?:授予头衔)\s*((?:\d+\s*)+)(.*)"
        match = re.match(pattern_plain, event.raw_message)
        if match:
            special_title = match.group(2).strip()
    if not user_ids or not special_title or special_title.isdigit():
        await UniMessage.text(
            "格式错误，请使用：授予头衔@某人/QQ号 [头衔内容]\nTip: 多个请用空格分隔"
        ).send(reply_to=True)
        return
    msg = []
    for uid in user_ids:
        try:
            await bot.set_group_special_title(
                group_id=event.group_id, user_id=int(uid), special_title=special_title
            )
            msg.append(
                f"授予头衔成功: {parse.get_display(uid, event.raw_message)}\
 → {special_title}"
            )
        except ActionFailed as e:
            logger.error(f"授予头衔{uid}失败: {e}")
            msg.append(f"授予头衔失败: {parse.get_display(uid, event.raw_message)}")
    await UniMessage.text("\n".join(msg) if msg else "无用户被授予头衔").send(
        reply_to=True
    )


@revoke_title_cmd.handle()
async def handle_revoke_title(bot: Bot, event: GroupMessageEvent) -> None:
    """
    处理剥夺头衔命令，支持多用户和单用户
    """
    if not await check_role_permission(
        event, {"admin", "owner", "super"}, inherit=True
    ):
        await UniMessage.text("仅管理员、群主和超管可用").send(reply_to=True)
        return
    if (
        await bot.get_group_member_info(
            group_id=event.group_id, user_id=event.self_id, no_cache=True
        )
    )["role"] != "owner":
        await UniMessage.text("机器人不是群主，无法剥夺头衔！").send(reply_to=True)
        return
    user_ids = parse.parse_ids_by_cmd(event.raw_message, ["剥夺头衔"])
    if not user_ids:
        await UniMessage.text(
            "格式错误，请使用：剥夺头衔@某人 或 剥夺头衔[QQ号]\nTip: 多个请用空格分隔"
        ).send(reply_to=True)
        return
    msg = []
    for uid in user_ids:
        try:
            await bot.set_group_special_title(
                group_id=event.group_id, user_id=int(uid), special_title=""
            )
            msg.append(f"剥夺头衔成功: {parse.get_display(uid, event.raw_message)}")
        except ActionFailed as e:
            logger.error(f"剥夺头衔{uid}失败: {e}")
            msg.append(f"剥夺头衔失败: {parse.get_display(uid, event.raw_message)}")
    await UniMessage.text("\n".join(msg) if msg else "无用户被剥夺头衔").send(
        reply_to=True
    )
