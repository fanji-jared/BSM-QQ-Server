import logging
from typing import Any, Dict, List, Optional

import httpx

from ..config import config
from .exceptions import (
    BSMAuthenticationError,
    BSMConnectionError,
    BSMError,
    BSMNotFoundError,
    BSMServerError,
)
from .models import AuthToken, ServerInfo, ServerStatus, TaskResult

logger = logging.getLogger(__name__)


class BSMClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.base_url = (base_url or config.BSM_API_URL).rstrip("/")
        self.username = username or config.BSM_USERNAME
        self.password = password or config.BSM_PASSWORD
        self._token: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "BSMClient":
        await self._get_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> Dict[str, Any]:
        client = await self._get_client()
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        try:
            response = await client.request(method, url, headers=headers, **kwargs)
            
            if response.status_code == 401:
                raise BSMAuthenticationError("Authentication failed or token expired")
            elif response.status_code == 404:
                raise BSMNotFoundError(f"Resource not found: {endpoint}")
            elif response.status_code >= 500:
                raise BSMServerError(f"Server error: {response.status_code}")
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except httpx.ConnectError as e:
            raise BSMConnectionError(f"Failed to connect to BSM API: {e}")
        except httpx.TimeoutException as e:
            raise BSMConnectionError(f"Request timeout: {e}")
        except httpx.HTTPStatusError as e:
            raise BSMError(f"HTTP error: {e}")

    async def authenticate(self) -> AuthToken:
        data = {
            "username": self.username,
            "password": self.password,
        }
        result = await self._request("POST", "/auth/token", json=data)
        token = AuthToken(**result)
        self._token = token.access_token
        logger.info("Successfully authenticated with BSM API")
        return token

    async def refresh_token(self) -> AuthToken:
        result = await self._request("GET", "/auth/refresh-token")
        token = AuthToken(**result)
        self._token = token.access_token
        return token

    async def logout(self):
        await self._request("GET", "/auth/logout")
        self._token = None
        logger.info("Logged out from BSM API")

    async def ensure_authenticated(self):
        if not self._token:
            await self.authenticate()

    async def start_server(self, server_name: str) -> TaskResult:
        await self.ensure_authenticated()
        result = await self._request("POST", f"/api/server/{server_name}/start")
        return TaskResult(**result)

    async def stop_server(self, server_name: str) -> TaskResult:
        await self.ensure_authenticated()
        result = await self._request("POST", f"/api/server/{server_name}/stop")
        return TaskResult(**result)

    async def restart_server(self, server_name: str) -> TaskResult:
        await self.ensure_authenticated()
        result = await self._request("POST", f"/api/server/{server_name}/restart")
        return TaskResult(**result)

    async def get_server_status(self, server_name: str) -> ServerInfo:
        await self.ensure_authenticated()
        result = await self._request("GET", f"/api/server/{server_name}/status")
        return ServerInfo(name=server_name, **result)

    async def list_servers(self) -> List[ServerInfo]:
        await self.ensure_authenticated()
        result = await self._request("GET", "/api/servers")
        servers = []
        for name, info in result.items():
            servers.append(ServerInfo(name=name, **info))
        return servers

    async def send_command(self, server_name: str, command: str) -> TaskResult:
        await self.ensure_authenticated()
        result = await self._request(
            "POST",
            f"/api/server/{server_name}/send_command",
            json={"command": command},
        )
        return TaskResult(**result)

    async def get_properties(self, server_name: str) -> Dict[str, Any]:
        await self.ensure_authenticated()
        return await self._request("GET", f"/api/server/{server_name}/properties/get")

    async def set_property(
        self, server_name: str, property_name: str, value: Any
    ) -> TaskResult:
        await self.ensure_authenticated()
        result = await self._request(
            "POST",
            f"/api/server/{server_name}/properties/set",
            json={"property": property_name, "value": value},
        )
        return TaskResult(**result)

    async def get_allowlist(self, server_name: str) -> List[str]:
        await self.ensure_authenticated()
        result = await self._request("GET", f"/api/server/{server_name}/allowlist/get")
        return result.get("allowlist", [])

    async def add_allowlist(
        self, server_name: str, player_name: str, ignores_limit: bool = False
    ) -> TaskResult:
        await self.ensure_authenticated()
        result = await self._request(
            "POST",
            f"/api/server/{server_name}/allowlist/add",
            json={"name": player_name, "ignoresPlayerLimit": ignores_limit},
        )
        return TaskResult(**result)

    async def remove_allowlist(self, server_name: str, player_name: str) -> TaskResult:
        await self.ensure_authenticated()
        result = await self._request(
            "DELETE",
            f"/api/server/{server_name}/allowlist/remove",
            json={"name": player_name},
        )
        return TaskResult(**result)

    async def get_permissions(self, server_name: str) -> List[Dict[str, Any]]:
        await self.ensure_authenticated()
        result = await self._request(
            "GET", f"/api/server/{server_name}/permissions/get"
        )
        return result.get("permissions", [])

    async def set_permission(
        self, server_name: str, xuid: str, name: str, level: str = "member"
    ) -> TaskResult:
        await self.ensure_authenticated()
        result = await self._request(
            "PUT",
            f"/api/server/{server_name}/permissions/set",
            json={"xuid": xuid, "name": name, "permissionLevel": level},
        )
        return TaskResult(**result)

    async def get_download_versions(self) -> List[Dict[str, Any]]:
        await self.ensure_authenticated()
        result = await self._request("GET", "/api/downloads/list")
        return result.get("versions", [])
