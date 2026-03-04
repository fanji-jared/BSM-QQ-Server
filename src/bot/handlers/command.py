"""QQ 机器人指令处理器"""

import logging
import re
from typing import Any, Callable, Dict, Optional

from botpy.message import GroupMessage, Message, DirectMessage

from ...bsm import BSMClient, APIError, ServerNotFoundError, ServerNotRunningError
from ...config import config

logger = logging.getLogger(__name__)


def _sanitize_message(msg: str) -> str:
    """清理消息，移除 URL 并限制长度"""
    msg = re.sub(r'https?://[^\s]+', '[链接]', msg)
    return msg[:500]


def _get_message(result: Any) -> str:
    """从结果中提取消息"""
    if hasattr(result, "message"):
        return result.message or "成功"
    if isinstance(result, dict):
        return result.get("message", "成功")
    return "成功"


class CommandHandler:
    """指令处理器"""

    def __init__(self):
        self.bsm_client = BSMClient()
        self.commands: Dict[str, Callable] = {
            "help": self._cmd_help,
            "list": self._cmd_list,
            "status": self._cmd_status,
            "info": self._cmd_info,
            "start": self._cmd_start,
            "stop": self._cmd_stop,
            "restart": self._cmd_restart,
            "cmd": self._cmd_command,
            "update": self._cmd_update,
            "prop": self._cmd_properties,
            "allowlist": self._cmd_allowlist,
            "perm": self._cmd_permissions,
            "players": self._cmd_players,
            "backup": self._cmd_backup,
            "world": self._cmd_world,
        }

    async def handle(self, message):
        """处理消息"""
        content = message.content.strip()
        prefix = config.BOT_PREFIX

        if not content.startswith(prefix):
            return

        # 解析指令
        parts = content[len(prefix):].strip().split()
        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        # 查找指令处理器
        handler = self.commands.get(cmd)
        if not handler:
            await self._reply(message, f"❌ 未知指令: {cmd}\n输入 {prefix}help 查看帮助")
            return

        try:
            await handler(message, args)
        except ServerNotFoundError as e:
            logger.error(f"Server not found: {e}")
            await self._reply(message, _sanitize_message(f"❌ 服务器不存在: {e}"))
        except ServerNotRunningError as e:
            logger.error(f"Server not running: {e}")
            await self._reply(message, _sanitize_message(f"❌ 服务器未运行: {e}"))
        except APIError as e:
            logger.error(f"BSM API error: {e}")
            await self._reply(message, _sanitize_message(f"❌ API 错误: {e}"))
        except Exception as e:
            logger.error(f"Command error: {e}", exc_info=True)
            await self._reply(message, _sanitize_message(f"❌ 执行失败: {e}"))

    async def _reply(self, message, content: str):
        """回复消息"""
        if not content.startswith("\n"):
            content = "\n" + content
        if isinstance(message, Message):
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

    def _check_admin(self, message) -> bool:
        """检查管理员权限（临时：所有人都是管理员）"""
        return True

    # ========== 指令实现 ==========

    async def _cmd_help(self, message, args):
        """帮助指令"""
        prefix = config.BOT_PREFIX
        help_text = f"""📖 BSM-QQ-Server 帮助

🔹 服务器信息
  {prefix}list - 列出所有服务器
  {prefix}status <服务器名> - 查看服务器状态
  {prefix}info - 查看系统信息

🔹 服务器操作 (管理员)
  {prefix}start <服务器名> - 启动服务器
  {prefix}stop <服务器名> - 停止服务器
  {prefix}restart <服务器名> - 重启服务器
  {prefix}cmd <服务器名> <命令> - 执行服务器命令
  {prefix}update <服务器名> - 更新服务器

🔹 配置管理 (管理员)
  {prefix}prop get <服务器名> [属性名] - 查看属性
  {prefix}prop set <服务器名> <属性名> <值> - 设置属性

🔹 白名单管理 (管理员)
  {prefix}allowlist list <服务器名> - 查看白名单
  {prefix}allowlist add <服务器名> <玩家名> - 添加白名单
  {prefix}allowlist remove <服务器名> <玩家名> - 移除白名单

🔹 权限管理 (管理员)
  {prefix}perm list <服务器名> - 查看权限
  {prefix}perm set <服务器名> <XUID> <玩家名> <等级> - 设置权限

🔹 玩家管理
  {prefix}players - 列出所有已知玩家
  {prefix}players scan - 扫描玩家日志

🔹 备份管理 (管理员)
  {prefix}backup list <服务器名> [类型] - 列出备份
  {prefix}backup create <服务器名> [类型] - 创建备份
  {prefix}backup export <服务器名> - 导出世界

🔹 世界管理 (管理员)
  {prefix}world list - 列出可用世界模板
  {prefix}world install <服务器名> <文件名> - 安装世界"""
        await self._reply(message, help_text)

    async def _cmd_list(self, message, args):
        """列出服务器"""
        async with self.bsm_client as client:
            servers = await client.list_servers()

        if not servers:
            await self._reply(message, "📭 没有找到任何服务器")
            return

        lines = ["📋 服务器列表:\n"]
        for server in servers:
            status = server.get("status", "UNKNOWN")
            emoji = "🟢" if status == "RUNNING" else "🔴"
            name = server.get("name", "unknown")
            version = server.get("version", "unknown")
            players = server.get("player_count", 0)
            lines.append(f"  {emoji} {name}")
            lines.append(f"     版本: {version} | 玩家: {players}")

        await self._reply(message, "\n".join(lines))

    async def _cmd_status(self, message, args):
        """查看服务器状态"""
        if not args:
            await self._reply(message, "❌ 请指定服务器名称")
            return

        server_name = args[0]
        async with self.bsm_client as client:
            servers = await client.list_servers()
            process_info = await client.get_server_process_info(server_name)

        # 从列表中查找服务器
        server = None
        for s in servers:
            if s.get("name") == server_name:
                server = s
                break

        if not server:
            await self._reply(message, f"❌ 服务器 '{server_name}' 不存在")
            return

        status = server.get("status", "UNKNOWN")
        emoji = "🟢" if status == "RUNNING" else "🔴"
        version = server.get("version", "unknown")
        players = server.get("player_count", 0)

        lines = [
            f"📊 服务器状态: {server_name}",
            f"  状态: {emoji} {status}",
            f"  版本: {version}",
            f"  玩家: {players}",
        ]

        if process_info:
            pid = process_info.get("pid", "N/A")
            cpu = process_info.get("cpu_percent", 0)
            mem = process_info.get("memory_mb", 0)
            uptime = process_info.get("uptime", "N/A")
            lines.extend([
                f"  PID: {pid}",
                f"  CPU: {cpu}%",
                f"  内存: {mem} MB",
                f"  运行时间: {uptime}",
            ])

        await self._reply(message, "\n".join(lines))

    async def _cmd_info(self, message, args):
        """查看系统信息"""
        async with self.bsm_client as client:
            info = await client.get_info()

        data = info.data or {}
        lines = ["💻 系统信息:"]
        
        if "os_type" in data:
            lines.append(f"  操作系统: {data['os_type']}")
        if "app_version" in data:
            lines.append(f"  BSM 版本: {data['app_version']}")
        if "python_version" in data:
            lines.append(f"  Python: {data['python_version']}")

        await self._reply(message, "\n".join(lines))

    async def _cmd_start(self, message, args):
        """启动服务器"""
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足")
            return

        if not args:
            await self._reply(message, "❌ 请指定服务器名称")
            return

        server_name = args[0]
        async with self.bsm_client as client:
            result = await client.start_server(server_name)

        await self._reply(message, f"✅ 服务器 {server_name} 启动命令已发送\n{_get_message(result)}")

    async def _cmd_stop(self, message, args):
        """停止服务器"""
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足")
            return

        if not args:
            await self._reply(message, "❌ 请指定服务器名称")
            return

        server_name = args[0]
        async with self.bsm_client as client:
            result = await client.stop_server(server_name)

        await self._reply(message, f"✅ 服务器 {server_name} 停止命令已发送\n{_get_message(result)}")

    async def _cmd_restart(self, message, args):
        """重启服务器"""
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足")
            return

        if not args:
            await self._reply(message, "❌ 请指定服务器名称")
            return

        server_name = args[0]
        async with self.bsm_client as client:
            result = await client.restart_server(server_name)

        await self._reply(message, f"✅ 服务器 {server_name} 重启命令已发送\n{_get_message(result)}")

    async def _cmd_command(self, message, args):
        """执行服务器命令"""
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足")
            return

        if len(args) < 2:
            await self._reply(message, "❌ 用法: cmd <服务器名> <命令>")
            return

        server_name = args[0]
        command = " ".join(args[1:])

        async with self.bsm_client as client:
            result = await client.send_command(server_name, command)

        await self._reply(message, f"✅ 命令已发送\n{_get_message(result)}")

    async def _cmd_update(self, message, args):
        """更新服务器"""
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足")
            return

        if not args:
            await self._reply(message, "❌ 请指定服务器名称")
            return

        server_name = args[0]
        async with self.bsm_client as client:
            result = await client.update_server(server_name)

        await self._reply(message, f"✅ 服务器 {server_name} 更新命令已发送\n{_get_message(result)}")

    async def _cmd_properties(self, message, args):
        """配置管理"""
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足")
            return

        if len(args) < 2:
            await self._reply(message, "❌ 用法:\n  prop get <服务器名> [属性名]\n  prop set <服务器名> <属性名> <值>")
            return

        action = args[0].lower()
        server_name = args[1]

        async with self.bsm_client as client:
            if action == "get":
                props = await client.get_properties(server_name)
                if len(args) > 2:
                    key = args[2]
                    value = props.get(key, "未设置")
                    await self._reply(message, f"📝 {key} = {value}")
                else:
                    lines = [f"📝 {server_name} 的属性:"]
                    for key, value in list(props.items())[:20]:
                        lines.append(f"  {key}: {value}")
                    if len(props) > 20:
                        lines.append(f"  ... 共 {len(props)} 个属性")
                    await self._reply(message, "\n".join(lines))

            elif action == "set":
                if len(args) < 4:
                    await self._reply(message, "❌ 用法: prop set <服务器名> <属性名> <值>")
                    return
                key = args[2]
                value = " ".join(args[3:])
                result = await client.set_property(server_name, key, value)
                await self._reply(message, f"✅ 已设置 {key} = {value}\n{_get_message(result)}")

            else:
                await self._reply(message, f"❌ 未知操作: {action}")

    async def _cmd_allowlist(self, message, args):
        """白名单管理"""
        if len(args) < 2:
            await self._reply(message, "❌ 用法:\n  allowlist list <服务器名>\n  allowlist add <服务器名> <玩家名>\n  allowlist remove <服务器名> <玩家名>")
            return

        action = args[0].lower()
        server_name = args[1]

        async with self.bsm_client as client:
            if action == "list":
                allowlist = await client.get_allowlist(server_name)
                if not allowlist:
                    await self._reply(message, "📭 白名单为空")
                    return

                lines = [f"📋 {server_name} 的白名单:"]
                for player in allowlist:
                    if isinstance(player, dict):
                        name = player.get("name", str(player))
                    else:
                        name = str(player)
                    lines.append(f"  • {name}")

                await self._reply(message, "\n".join(lines))

            elif action == "add":
                if not self._check_admin(message):
                    await self._reply(message, "❌ 权限不足")
                    return
                if len(args) < 3:
                    await self._reply(message, "❌ 请指定玩家名称")
                    return
                player_name = args[2]
                result = await client.add_allowlist(server_name, player_name)
                await self._reply(message, f"✅ 已将 {player_name} 添加到白名单\n{_get_message(result)}")

            elif action == "remove":
                if not self._check_admin(message):
                    await self._reply(message, "❌ 权限不足")
                    return
                if len(args) < 3:
                    await self._reply(message, "❌ 请指定玩家名称")
                    return
                player_name = args[2]
                result = await client.remove_allowlist(server_name, player_name)
                await self._reply(message, f"✅ 已将 {player_name} 从白名单移除\n{_get_message(result)}")

            else:
                await self._reply(message, f"❌ 未知操作: {action}")

    async def _cmd_permissions(self, message, args):
        """权限管理"""
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足")
            return

        if len(args) < 2:
            await self._reply(message, "❌ 用法:\n  perm list <服务器名>\n  perm set <服务器名> <XUID> <玩家名> <等级>")
            return

        action = args[0].lower()
        server_name = args[1]

        async with self.bsm_client as client:
            if action == "list":
                perms = await client.get_permissions(server_name)
                if not perms:
                    await self._reply(message, "📭 权限列表为空")
                    return

                lines = [f"📋 {server_name} 的权限列表:"]
                for perm in perms:
                    if isinstance(perm, dict):
                        name = perm.get("name", "unknown")
                        xuid = perm.get("xuid", "unknown")
                        level = perm.get("permissionLevel", "member")
                        lines.append(f"  • {name} ({xuid}): {level}")

                await self._reply(message, "\n".join(lines))

            elif action == "set":
                if len(args) < 5:
                    await self._reply(message, "❌ 用法: perm set <服务器名> <XUID> <玩家名> <等级>")
                    return
                xuid = args[2]
                player_name = args[3]
                level = args[4]
                result = await client.set_permission(server_name, xuid, player_name, level)
                await self._reply(message, f"✅ 已设置 {player_name} 的权限为 {level}\n{_get_message(result)}")

            else:
                await self._reply(message, f"❌ 未知操作: {action}")

    async def _cmd_players(self, message, args):
        """玩家管理"""
        action = args[0].lower() if args else "list"

        async with self.bsm_client as client:
            if action == "list":
                players = await client.get_players()
                if not players:
                    await self._reply(message, "📭 没有已知玩家")
                    return

                lines = ["📋 已知玩家列表:"]
                for player in players[:20]:
                    if isinstance(player, dict):
                        name = player.get("name", "unknown")
                        xuid = player.get("xuid", "unknown")
                        lines.append(f"  • {name} ({xuid})")
                    else:
                        lines.append(f"  • {player}")

                if len(players) > 20:
                    lines.append(f"  ... 共 {len(players)} 个玩家")

                await self._reply(message, "\n".join(lines))

            elif action == "scan":
                if not self._check_admin(message):
                    await self._reply(message, "❌ 权限不足")
                    return
                result = await client.scan_players()
                await self._reply(message, f"✅ 玩家扫描完成\n{_get_message(result)}")

            else:
                await self._reply(message, f"❌ 未知操作: {action}")

    async def _cmd_backup(self, message, args):
        """备份管理"""
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足")
            return

        if len(args) < 2:
            await self._reply(message, "❌ 用法:\n  backup list <服务器名> [类型]\n  backup create <服务器名> [类型]\n  backup export <服务器名>")
            return

        action = args[0].lower()
        server_name = args[1]

        async with self.bsm_client as client:
            if action == "list":
                backup_type = args[2] if len(args) > 2 else "all"
                backups = await client.list_backups(server_name, backup_type)
                if not backups:
                    await self._reply(message, "📭 没有备份")
                    return

                lines = [f"📋 {server_name} 的备份 ({backup_type}):"]
                for backup in backups[:15]:
                    lines.append(f"  • {backup}")
                if len(backups) > 15:
                    lines.append(f"  ... 共 {len(backups)} 个备份")

                await self._reply(message, "\n".join(lines))

            elif action == "create":
                backup_type = args[2] if len(args) > 2 else "world"
                result = await client.create_backup(server_name, backup_type)
                await self._reply(message, f"✅ 备份创建成功\n{_get_message(result)}")

            elif action == "export":
                result = await client.export_world(server_name)
                await self._reply(message, f"✅ 世界导出成功\n{_get_message(result)}")

            else:
                await self._reply(message, f"❌ 未知操作: {action}")

    async def _cmd_world(self, message, args):
        """世界管理"""
        if not self._check_admin(message):
            await self._reply(message, "❌ 权限不足")
            return

        if not args:
            await self._reply(message, "❌ 用法:\n  world list\n  world install <服务器名> <文件名>")
            return

        action = args[0].lower()

        async with self.bsm_client as client:
            if action == "list":
                worlds = await client.list_worlds()
                if not worlds:
                    await self._reply(message, "📭 没有可用的世界模板")
                    return

                lines = ["📋 可用世界模板:"]
                for world in worlds[:15]:
                    lines.append(f"  • {world}")
                if len(worlds) > 15:
                    lines.append(f"  ... 共 {len(worlds)} 个")

                await self._reply(message, "\n".join(lines))

            elif action == "install":
                if len(args) < 3:
                    await self._reply(message, "❌ 用法: world install <服务器名> <文件名>")
                    return
                server_name = args[1]
                filename = args[2]
                result = await client.install_world(server_name, filename)
                await self._reply(message, f"✅ 世界安装成功\n{_get_message(result)}")

            else:
                await self._reply(message, f"❌ 未知操作: {action}")
