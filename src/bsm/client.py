"""BSM API 客户端包装器，基于官方 bsm-api-client"""

import logging
from typing import Any, Dict, List, Optional

from bsm_api_client import BedrockServerManagerApi
from bsm_api_client.exceptions import (
    APIError,
    AuthError,
    CannotConnectError,
    ServerNotFoundError,
    ServerNotRunningError,
)
from bsm_api_client.models import (
    ActionResponse,
    AllowlistAddPayload,
    AllowlistRemovePayload,
    BackupActionPayload,
    CommandPayload,
    FileNamePayload,
    GeneralApiResponse,
    PermissionsSetPayload,
    PlayerPermission,
    PropertiesPayload,
)

from ..config import config

logger = logging.getLogger(__name__)


class BSMClient:
    """BSM API 客户端包装器"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.base_url = base_url or config.BSM_API_URL
        self.username = username or config.BSM_USERNAME
        self.password = password or config.BSM_PASSWORD
        self._client: Optional[BedrockServerManagerApi] = None

    async def __aenter__(self) -> "BSMClient":
        self._client = BedrockServerManagerApi(
            base_url=self.base_url,
            username=self.username,
            password=self.password,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.close()
            self._client = None

    @property
    def api(self) -> BedrockServerManagerApi:
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        return self._client

    # ========== 管理器信息 ==========
    
    async def get_info(self) -> GeneralApiResponse:
        """获取系统信息"""
        return await self.api.async_get_info()

    # ========== 服务器列表和状态 ==========
    
    async def list_servers(self) -> List[dict]:
        """获取所有服务器列表"""
        result = await self.api.async_get_servers()
        return result.servers or []

    async def get_server_names(self) -> List[str]:
        """获取服务器名称列表"""
        return await self.api.async_get_server_names()

    async def get_server_status(self, server_name: str) -> dict:
        """获取服务器运行状态"""
        result = await self.api.async_get_server_running_status(server_name)
        return {
            "name": server_name,
            "running": result.data.get("running", False) if result.data else False,
        }

    async def get_server_process_info(self, server_name: str) -> dict:
        """获取服务器进程信息"""
        result = await self.api.async_get_server_process_info(server_name)
        return result.data.get("process_info", {}) if result.data else {}

    async def get_server_version(self, server_name: str) -> str:
        """获取服务器版本"""
        result = await self.api.async_get_server_version(server_name)
        return result.data.get("version", "unknown") if result.data else "unknown"

    # ========== 服务器操作 ==========
    
    async def start_server(self, server_name: str) -> ActionResponse:
        """启动服务器"""
        return await self.api.async_start_server(server_name)

    async def stop_server(self, server_name: str) -> ActionResponse:
        """停止服务器"""
        return await self.api.async_stop_server(server_name)

    async def restart_server(self, server_name: str) -> ActionResponse:
        """重启服务器"""
        return await self.api.async_restart_server(server_name)

    async def send_command(self, server_name: str, command: str) -> ActionResponse:
        """发送服务器命令"""
        return await self.api.async_send_server_command(
            server_name, CommandPayload(command=command)
        )

    async def update_server(self, server_name: str) -> ActionResponse:
        """更新服务器"""
        return await self.api.async_update_server(server_name)

    # ========== 配置管理 ==========
    
    async def get_properties(self, server_name: str) -> dict:
        """获取服务器属性"""
        result = await self.api.async_get_server_properties(server_name)
        return result.properties or result.data or {}

    async def set_property(self, server_name: str, key: str, value: str) -> ActionResponse:
        """设置服务器属性"""
        return await self.api.async_update_server_properties(
            server_name, PropertiesPayload(properties={key: value})
        )

    # ========== 白名单管理 ==========
    
    async def get_allowlist(self, server_name: str) -> List[dict]:
        """获取白名单"""
        result = await self.api.async_get_server_allowlist(server_name)
        return result.players or result.data or []

    async def add_allowlist(
        self, server_name: str, player_name: str, ignores_limit: bool = False
    ) -> ActionResponse:
        """添加白名单"""
        return await self.api.async_add_server_allowlist(
            server_name,
            AllowlistAddPayload(players=[player_name], ignoresPlayerLimit=ignores_limit),
        )

    async def remove_allowlist(self, server_name: str, player_name: str) -> ActionResponse:
        """移除白名单"""
        return await self.api.async_remove_server_allowlist_players(
            server_name, AllowlistRemovePayload(players=[player_name])
        )

    # ========== 权限管理 ==========
    
    async def get_permissions(self, server_name: str) -> List[dict]:
        """获取权限列表"""
        result = await self.api.async_get_server_permissions_data(server_name)
        return result.permissions or result.data or []

    async def set_permission(
        self, server_name: str, xuid: str, name: str, level: str = "member"
    ) -> ActionResponse:
        """设置权限"""
        return await self.api.async_set_server_permissions(
            server_name,
            PermissionsSetPayload(
                permissions=[PlayerPermission(name=name, xuid=xuid, permission_level=level)]
            ),
        )

    # ========== 玩家管理 ==========
    
    async def get_players(self) -> List[dict]:
        """获取所有已知玩家"""
        result = await self.api.async_get_players()
        if isinstance(result, dict):
            return result.get("players", [])
        return result.players if hasattr(result, "players") else []

    async def scan_players(self) -> Dict[str, Any]:
        """扫描玩家日志"""
        return await self.api.async_scan_players()

    # ========== 备份管理 ==========
    
    async def list_backups(self, server_name: str, backup_type: str = "all") -> List[str]:
        """列出备份"""
        result = await self.api.async_list_server_backups(server_name, backup_type)
        return result.files or result.data or []

    async def create_backup(self, server_name: str, backup_type: str = "world") -> Dict[str, Any]:
        """创建备份"""
        result = await self.api.async_trigger_server_backup(
            server_name, BackupActionPayload(backup_type=backup_type)
        )
        return result.model_dump()

    async def export_world(self, server_name: str) -> ActionResponse:
        """导出世界"""
        return await self.api.async_export_server_world(server_name)

    # ========== 内容管理 ==========
    
    async def list_worlds(self) -> List[str]:
        """列出可用世界模板"""
        result = await self.api.async_get_content_worlds()
        return result.files or []

    async def list_addons(self) -> List[str]:
        """列出可用插件"""
        result = await self.api.async_get_content_addons()
        return result.files or []

    async def install_world(self, server_name: str, filename: str) -> ActionResponse:
        """安装世界"""
        return await self.api.async_install_server_world(
            server_name, FileNamePayload(filename=filename)
        )

    async def install_addon(self, server_name: str, filename: str) -> ActionResponse:
        """安装插件"""
        return await self.api.async_install_server_addon(
            server_name, FileNamePayload(filename=filename)
        )
