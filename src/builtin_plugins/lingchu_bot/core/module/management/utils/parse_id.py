import re


def parse_ids_by_cmd(raw_message: str, cmd_keywords: list[str]) -> list[str]:
    """
    通用解析命令中的用户id，支持@和纯数字两种格式
    cmd_keywords: ["设置管理员", "禁言", "解禁", "踢", "授予头衔", "剥夺头衔"]
    """
    cmd_pattern = "|".join(cmd_keywords)
    # 兼容 [CQ:at,qq=xxx] 和 [at:qq=xxx]
    pattern_at = rf"(?:{cmd_pattern})((?:\[(?:CQ:)?at,qq=\d+(?:,name=[^\]]+)?\]\s?)+)"
    pattern_plain = rf"(?:{cmd_pattern})\s*((?:\d+\s?)+)"
    match = re.search(pattern_at, raw_message)
    if match:
        at_block = match.group(1).strip()
        return re.findall(r"\[(?:CQ:)?at,qq=(\d+)", at_block)
    match = re.search(pattern_plain, raw_message)
    if match:
        ids_block = match.group(1).strip()
        return [uid for uid in ids_block.split() if uid.isdigit()]
    return []


def get_display(uid: str, raw_message: str) -> str:
    """
    优先返回@name，无name则返回qq号
    """
    # 兼容 [CQ:at,qq=xxx,name=xxx] 和 [at:qq=xxx,name=xxx]
    pattern = rf"\[(?:CQ:)?at,qq={uid}(?:,name=([^\]]+))?\]"
    match = re.search(pattern, raw_message)
    if match and match.group(1):
        return f"@{match.group(1)}"
    if uid:
        return uid
    return ""


def parse_ids_and_time(
    raw_message: str, cmd_keywords: list[str]
) -> tuple[list[str], int | None]:
    """
    解析命令，返回用户id列表和时长
    支持格式：
    1. 命令[CQ:at,qq=123456,name=xxx] [CQ:at,qq=654321,name=yyy] 60
    2. 命令123456 654321 60
    cmd_keywords: ["禁言", ...]
    """
    cmd_pattern = "|".join(cmd_keywords)
    # 兼容 [CQ:at,qq=xxx] 和 [at:qq=xxx]
    pattern_at = (
        rf"(?:{cmd_pattern})((?:\[(?:CQ:)?at,qq=\d+(?:,name=[^\]]+)?\]\s?)+)\s*(\d+)"
    )
    pattern_plain = rf"(?:{cmd_pattern})\s*((?:\d+\s?)+)\s*(\d+)"
    match = re.search(pattern_at, raw_message)
    if match:
        at_block = match.group(1).strip()
        mute_time = int(match.group(2))
        return re.findall(r"\[(?:CQ:)?at,qq=(\d+)", at_block), mute_time
    match = re.search(pattern_plain, raw_message)
    if match:
        ids_block = match.group(1).strip()
        mute_time = int(match.group(2))
        return [uid for uid in ids_block.split() if uid.isdigit()], mute_time
    return [], None
