import logging
from typing import Any, Callable, Dict, Optional

from botpy.message import GroupMessage, Message, DirectMessage

from ...bsm import BSMClient, BSMError
from ...config import config
from ...utils import format_server_status, parse_command, validate_player_name

logger = logging.getLogger(__name__)


class CommandHandler:
    def __init__(self):
        self.bsm_client = BSMClient()
        self.commands: Dict[str, Callable] = {
            "help": self._cmd_help,
            "status": self._cmd_status,
            "list": self._cmd_list,
            "start": self._cmd_start,
            "stop": self._cmd_stop,
            "restart": self._cmd_restart,
            "cmd": self._cmd_command,
            "whitelist": self._cmd_whitelist,
            "op": self._cmd_op,
            "deop": self._cmd_deop,
            "config": self._cmd_config,
        }

    async def handle(self, message):
        content = self._extract_content(message)
        parsed = parse_command(content, config.BOT_PREFIX)
        
        if parsed is None:
            return
        
        command, args, kwargs = parsed
        
        handler = self.commands.get(command)
        if handler is None:
            await self._reply(message, f"❌ 未知命令: {command}\n使用 {config.BOT_PREFIX} help 查看帮助")
            return
        
        try:
            await handler(message, args, kwargs)
        except BSMError as e:
            logger.error(f"BSM API error: {e}")
            await self._reply(message, f"❌ 服务器错误: {e}")
        except Exception as e:
            logger.error(f"Command error: {e}", exc_info=True)
            await self._reply(message, f"❌ 执行失败: {e}")

    def _extract_content(self, message) -> str:
        if hasattr(message, "content"):
            content = message.content
            if hasattr(message, "mentions"):
                for mention in message.mentions or []:
                    content = content.replace(f"<@{mention}>", "").strip()
            return content
        return ""

    async def _reply(self, message, content: str):
        if hasattr(message, "reply"):
            await message.reply(content=content)
        elif isinstance(message, GroupMessage):
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0,
                msg_id=message.id,
                content=content,
            )
        elif isinstance(message, DirectMessage):
            await message._api.post_dms(
                guild_id=message.guild_id,
                msg_type=0,
                msg_id=message.id,
                content=content,
            )

    def _get_user_id(self, message) -> str:
        if hasattr(message, "author"):
            return message.author.id
        elif hasattr(message, "member"):
            return message.member.id
        return ""

    def _check_admin(self, message) -> bool:
        user_id = self._get_user_id(message)
        return config.is_admin(user_id)

    async def _cmd_help(self, message, args, kwargs):
        help_text = f"""📖 BSM-QQ-Server 帮助

【服务器管理】
{config.BOT_PREFIX} status [服务器名] - 查看服务器状态
{config.BOT_PREFIX} list - 列出所有服务器
{config.BOT_PREFIX} start <服务器名> - 启动服务器 [管理员]
{config.BOT_PREFIX} stop <服务器名> - 停止服务器 [管理员]
{config.BOT_PREFIX} restart <服务器名> - 重启服务器 [管理员]

【玩家管理】
{config.BOT_PREFIX} whitelist list [服务器名] - 查看白名单
{config.BOT_PREFIX} whitelist add <玩家名> [服务器名] - 添加白名单 [管理员]
{config.BOT_PREFIX} whitelist remove <玩家名> [服务器名] - 移除白名单 [管理员]
{config.BOT_PREFIX} op <玩家名> [服务器名] - 设置管理员 [管理员]
{config.BOT_PREFIX} deop <玩家名> [服务器名] - 取消管理员 [管理员]

【服务器配置】
{config.BOT_PREFIX} config get [属性名] [服务器名] - 查看配置 [管理员]
{config.BOT_PREFIX} config set <属性名> <值> [服务器名] - 设置配置 [管理员]
{config.BOT_PREFIX} cmd <命令> [服务器名] - 执行服务器命令 [管理员]"""
        await self._reply(message, help_text)

    async def _cmd_status(self, message, args, kwargs):
        server_name = args[0] if args else "default"
        
        async with self.bsm_client as client:
            server = await client.get_server_status(server_name)
            status_text = format_server_status(server)
        
        await self._reply(message, status_text)

    async def _cmd_list(self, message, args, kwargs):
        async with self.bsm_client as client:
            servers = await client.list_servers()
        
        if not servers:
            await self._reply(message, "📭 没有找到任何服务器")
            return
        
        lines = ["📋 服务器列表:\n"]
        for server in servers:
            status_emoji = "🟢" if server.status.value == "running" else "🔴"
            lines.append(f"  {status_emoji} {server.name} ({server.status.value})")
        
        await self._reply(message, "\n".join(lines))

    async def _cmd_start(self, message, args, kwargs):
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足，此命令仅限管理员使用")
            return
        
        if not args:
            await self._reply(message, "❌ 请指定服务器名称")
            return
        
        server_name = args[0]
        async with self.bsm_client as client:
            result = await client.start_server(server_name)
        
        await self._reply(message, f"✅ 服务器 {server_name} 启动命令已发送\n{result.message}")

    async def _cmd_stop(self, message, args, kwargs):
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足，此命令仅限管理员使用")
            return
        
        if not args:
            await self._reply(message, "❌ 请指定服务器名称")
            return
        
        server_name = args[0]
        async with self.bsm_client as client:
            result = await client.stop_server(server_name)
        
        await self._reply(message, f"✅ 服务器 {server_name} 停止命令已发送\n{result.message}")

    async def _cmd_restart(self, message, args, kwargs):
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足，此命令仅限管理员使用")
            return
        
        if not args:
            await self._reply(message, "❌ 请指定服务器名称")
            return
        
        server_name = args[0]
        async with self.bsm_client as client:
            result = await client.restart_server(server_name)
        
        await self._reply(message, f"✅ 服务器 {server_name} 重启命令已发送\n{result.message}")

    async def _cmd_command(self, message, args, kwargs):
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足，此命令仅限管理员使用")
            return
        
        if not args:
            await self._reply(message, "❌ 请输入要执行的命令")
            return
        
        server_name = kwargs.get("server", "default")
        command = " ".join(args)
        
        async with self.bsm_client as client:
            result = await client.send_command(server_name, command)
        
        await self._reply(message, f"✅ 命令已发送\n{result.message}")

    async def _cmd_whitelist(self, message, args, kwargs):
        if not args:
            await self._reply(message, "❌ 请指定操作: list, add, remove")
            return
        
        action = args[0].lower()
        server_name = kwargs.get("server", "default")
        
        if action == "list":
            async with self.bsm_client as client:
                allowlist = await client.get_allowlist(server_name)
            
            if not allowlist:
                await self._reply(message, "📭 白名单为空")
                return
            
            lines = ["📋 白名单列表:\n"]
            for player in allowlist:
                lines.append(f"  • {player}")
            
            await self._reply(message, "\n".join(lines))
        
        elif action == "add":
            if not self._check_admin(message):
                await self._reply(message, "❌ 权限不足，此命令仅限管理员使用")
                return
            
            if len(args) < 2:
                await self._reply(message, "❌ 请指定玩家名称")
                return
            
            player_name = args[1]
            if not validate_player_name(player_name):
                await self._reply(message, "❌ 无效的玩家名称")
                return
            
            async with self.bsm_client as client:
                result = await client.add_allowlist(server_name, player_name)
            
            await self._reply(message, f"✅ 已将 {player_name} 添加到白名单\n{result.message}")
        
        elif action == "remove":
            if not self._check_admin(message):
                await self._reply(message, "❌ 权限不足，此命令仅限管理员使用")
                return
            
            if len(args) < 2:
                await self._reply(message, "❌ 请指定玩家名称")
                return
            
            player_name = args[1]
            
            async with self.bsm_client as client:
                result = await client.remove_allowlist(server_name, player_name)
            
            await self._reply(message, f"✅ 已将 {player_name} 从白名单移除\n{result.message}")
        
        else:
            await self._reply(message, f"❌ 未知操作: {action}")

    async def _cmd_op(self, message, args, kwargs):
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足，此命令仅限管理员使用")
            return
        
        if not args:
            await self._reply(message, "❌ 请指定玩家名称")
            return
        
        player_name = args[0]
        server_name = kwargs.get("server", "default")
        
        async with self.bsm_client as client:
            result = await client.send_command(server_name, f"op {player_name}")
        
        await self._reply(message, f"✅ 已将 {player_name} 设置为管理员\n{result.message}")

    async def _cmd_deop(self, message, args, kwargs):
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足，此命令仅限管理员使用")
            return
        
        if not args:
            await self._reply(message, "❌ 请指定玩家名称")
            return
        
        player_name = args[0]
        server_name = kwargs.get("server", "default")
        
        async with self.bsm_client as client:
            result = await client.send_command(server_name, f"deop {player_name}")
        
        await self._reply(message, f"✅ 已取消 {player_name} 的管理员权限\n{result.message}")

    async def _cmd_config(self, message, args, kwargs):
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足，此命令仅限管理员使用")
            return
        
        if not args:
            await self._reply(message, "❌ 请指定操作: get, set")
            return
        
        action = args[0].lower()
        server_name = kwargs.get("server", "default")
        
        if action == "get":
            async with self.bsm_client as client:
                properties = await client.get_properties(server_name)
            
            if len(args) >= 2:
                prop_name = args[1]
                value = properties.get(prop_name, "未找到")
                await self._reply(message, f"📋 {prop_name} = {value}")
            else:
                lines = ["📋 服务器配置:\n"]
                for key, value in sorted(properties.items()):
                    lines.append(f"  {key} = {value}")
                await self._reply(message, "\n".join(lines)[:2000])
        
        elif action == "set":
            if len(args) < 3:
                await self._reply(message, "❌ 请指定属性名和值")
                return
            
            prop_name = args[1]
            prop_value = args[2]
            
            async with self.bsm_client as client:
                result = await client.set_property(server_name, prop_name, prop_value)
            
            await self._reply(message, f"✅ 已设置 {prop_name} = {prop_value}\n{result.message}")
        
        else:
            await self._reply(message, f"❌ 未知操作: {action}")
