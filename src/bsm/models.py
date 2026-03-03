from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ServerStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


class ServerInfo(BaseModel):
    name: str
    status: ServerStatus = ServerStatus.UNKNOWN
    version: Optional[str] = None
    online_players: int = 0
    max_players: int = 0
    uptime: Optional[str] = None


class AllowlistPlayer(BaseModel):
    name: str
    ignores_player_limit: bool = False


class PermissionPlayer(BaseModel):
    xuid: str
    name: str
    permission_level: str = "member"


class TaskResult(BaseModel):
    status: str
    message: str
    details: Optional[str] = None
    task_id: Optional[str] = None


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: Optional[str] = None
