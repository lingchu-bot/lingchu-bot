# import re

# from nonebot import logger, on_startswith
# from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
# from nonebot_plugin_alconna.uniseg import UniMessage

# from ...utils.auth import check_permission_and_status

# # ================= 工具函数 =================


# def parse_ids(raw_message: str, action: str) -> list[str]:
#     """
#     解析设置/取消管理员命令，返回用户id列表
#     支持格式：
#     1. {action}[CQ:at,qq=123456,name=xxx] [CQ:at,qq=654321,name=yyy]
#     2. {action}123456 654321
#     """
#     pattern_at = rf"{re.escape(action)}((?:\[CQ:at,qq=\d+(?:,name=[^\]]+)?\] ?)+)"
#     pattern_plain = rf"{re.escape(action)} ?((?:\d+ ?)+)"
#     match = re.search(pattern_at, raw_message)
#     if match:
#         at_block = match.group(1).strip()
#         return re.findall(r"\[CQ:at,qq=(\d+)", at_block)
#     match = re.search(pattern_plain, raw_message)
#     if match:
#         ids_block = match.group(1).strip()
#         return [uid for uid in ids_block.split() if uid.isdigit()]
#     return []


# def get_display(uid: str, raw_message: str) -> str:
#     """
#     优先返回@name，无name则返回qq号
#     """
#     pattern = rf"\[CQ:at,qq={uid}(?:,name=([^\]]+))?\]"
#     match = re.search(pattern, raw_message)
#     if match and match.group(1):
#         return f"@{match.group(1)}"
#     if uid:
#         return uid
#     return ""


# # ================= 指令注册 =================

# set_admin_cmd = on_startswith("设置管理员", priority=5, block=True)
# unset_admin_cmd = on_startswith("取消管理员", priority=5, block=True)


# # ================= 事件处理 =================


# @set_admin_cmd.handle()
# async def handle_set_admin(bot: Bot, event: GroupMessageEvent) -> None:
#     """
#     处理设置管理员命令，支持多用户和单用户
#     """
#     user_ids = parse_ids(event.raw_message, "设置管理员")
#     if not user_ids:
#         await UniMessage.text(
#             "格式错误，请使用：设置管理员@某人 或 设置管理员[QQ号]\nTip: 多个请用空格分隔"
#         ).send(reply_to=True)
#         return
#     if not await check_permission_and_status(event, "设置管理员"):
#         return
#     success = []
#     failed = []
#     for uid in user_ids:
#         try:
#             logger.debug(
#                 f"{event.self_id}收到设置管理员指令: {event.raw_message} "
#                 f"来自用户: {event.user_id} 目标用户: {uid} 在群: {event.group_id}"
#             )
#             await bot.set_group_admin(
#                 group_id=event.group_id, user_id=int(uid), enable=True
#             )
#             success.append(get_display(uid, event.raw_message))
#         except (ValueError, TypeError, RuntimeError) as e:
#             logger.error(f"设置管理员{uid}失败: {e}")
#             failed.append(get_display(uid, event.raw_message))
#     msg = []
#     if success:
#         msg.append(f"设置管理员成功: {'、'.join(success)}")
#     if failed:
#         msg.append(f"设置管理员失败: {'、'.join(failed)}")
#     await UniMessage.text("\n".join(msg) if msg else "无用户被设置管理员").send(
#         reply_to=True
#     )


# @unset_admin_cmd.handle()
# async def handle_unset_admin(bot: Bot, event: GroupMessageEvent) -> None:
#     """
#     处理取消管理员命令，支持多用户和单用户
#     """
#     user_ids = parse_ids(event.raw_message, "取消管理员")
#     if not user_ids:
#         await UniMessage.text(
#             "格式错误，请使用：取消管理员@某人 或 取消管理员[QQ号]\nTip: 多个请用空格分隔"
#         ).send(reply_to=True)
#         return
#     if not await check_permission_and_status(event, "取消管理员"):
#         return
#     success = []
#     failed = []
#     for uid in user_ids:
#         try:
#             logger.debug(
#                 f"{event.self_id}收到取消管理员指令: {event.raw_message} "
#                 f"来自用户: {event.user_id} 目标用户: {uid} 在群: {event.group_id}"
#             )
#             await bot.set_group_admin(
#                 group_id=event.group_id, user_id=int(uid), enable=False
#             )
#             success.append(get_display(uid, event.raw_message))
#         except (ValueError, TypeError, RuntimeError) as e:
#             logger.error(f"取消管理员{uid}失败: {e}")
#             failed.append(get_display(uid, event.raw_message))
#     msg = []
#     if success:
#         msg.append(f"取消管理员成功: {'、'.join(success)}")
#     if failed:
#         msg.append(f"取消管理员失败: {'、'.join(failed)}")
#     await UniMessage.text("\n".join(msg) if msg else "无用户被取消管理员").send(
#         reply_to=True
#     )
