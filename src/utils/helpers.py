import re
from typing import Optional, Tuple

from ..bsm.models import ServerInfo, ServerStatus


def format_server_status(server: ServerInfo) -> str:
    status_emoji = {
        ServerStatus.RUNNING: "🟢",
        ServerStatus.STOPPED: "🔴",
        ServerStatus.STARTING: "🟡",
        ServerStatus.STOPPING: "🟠",
        ServerStatus.UNKNOWN: "⚪",
    }
    
    emoji = status_emoji.get(server.status, "⚪")
    lines = [
        f"{emoji} 服务器: {server.name}",
        f"   状态: {server.status.value}",
    ]
    
    if server.version:
        lines.append(f"   版本: {server.version}")
    
    if server.status == ServerStatus.RUNNING:
        lines.append(f"   玩家: {server.online_players}/{server.max_players}")
        if server.uptime:
            lines.append(f"   运行时间: {server.uptime}")
    
    return "\n".join(lines)


def parse_command(
    message: str, prefix: str = "/mc"
) -> Optional[Tuple[str, list, dict]]:
    message = message.strip()
    
    if not message.startswith(prefix):
        return None
    
    content = message[len(prefix):].strip()
    if not content:
        return ("help", [], {})
    
    parts = content.split()
    command = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    
    kwargs = {}
    clean_args = []
    
    for arg in args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            kwargs[key.lower()] = value
        else:
            clean_args.append(arg)
    
    return (command, clean_args, kwargs)


def validate_player_name(name: str) -> bool:
    if not name or len(name) < 3 or len(name) > 16:
        return False
    
    pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, name))


def format_uptime(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}分钟"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}小时{minutes}分钟"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}天{hours}小时"
