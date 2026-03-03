# BSM-QQ-Server

🤖 一个用于管理 Minecraft 基岩版服务器的 QQ 机器人，通过对接 Bedrock Server Manager (BSM) API 实现远程服务器管理。

> 💡 本项目基于 [bsm-api-client](https://github.com/DMedina559/bsm-api-client) 构建，这是 BSM 官方提供的 Python 异步 API 客户端库。

[English](README_EN.md) | 中文

## ✨ 功能特性

- 🔧 **服务器管理**: 启动、停止、重启、更新服务器
- 📊 **状态监控**: 查看服务器运行状态、版本、进程信息
- 👥 **玩家管理**: 白名单管理、权限设置、玩家扫描
- ⚙️ **配置管理**: 查询和修改服务器属性
- 💾 **备份管理**: 创建备份、列出备份、导出世界
- 🌍 **世界管理**: 列出和安装世界模板
- 📱 **多场景支持**: 支持 QQ 群、QQ 频道、私信

## 📋 目录

- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [指令列表](#指令列表)
- [项目结构](#项目结构)
- [开发指南](#开发指南)
- [常见问题](#常见问题)

## 环境要求

- Python 3.10 或更高版本
- Bedrock Server Manager (BSM) 服务
- QQ 开放平台机器人账号

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/fanji-jared/BSM-QQ-Server.git
cd BSM-QQ-Server
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必要的配置信息：

```env
# QQ机器人配置
QQ_BOT_APPID=你的机器人AppID
QQ_BOT_SECRET=你的机器人AppSecret

# BSM API配置
BSM_API_URL=http://your-bsm-server:11325/api
BSM_USERNAME=你的BSM用户名
BSM_PASSWORD=你的BSM密码

# 机器人配置
BOT_PREFIX=/
ADMIN_USERS=管理员QQ号1,管理员QQ号2

# 日志级别
LOG_LEVEL=INFO
```

### 4. 运行机器人

```bash
python -m src.main
```

## 配置说明

### 环境变量详解

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `QQ_BOT_APPID` | ✅ | QQ 机器人的 AppID，从 QQ 开放平台获取 |
| `QQ_BOT_SECRET` | ✅ | QQ 机器人的 AppSecret，从 QQ 开放平台获取 |
| `BSM_API_URL` | ✅ | BSM API 服务地址，默认为 `http://localhost:11325/api` |
| `BSM_USERNAME` | ✅ | BSM 登录用户名 |
| `BSM_PASSWORD` | ✅ | BSM 登录密码 |
| `BOT_PREFIX` | ❌ | 机器人指令前缀，默认为 `/` |
| `ADMIN_USERS` | ❌ | 管理员 QQ 号列表，用逗号分隔 |
| `LOG_LEVEL` | ❌ | 日志级别，默认为 `INFO`，可选 `DEBUG`、`WARNING`、`ERROR` |

### 获取 QQ 机器人凭证

1. 访问 [QQ 开放平台](https://bot.q.qq.com/)
2. 注册并登录开发者账号
3. 创建机器人应用
4. 在机器人管理页面获取 `AppID` 和 `AppSecret`

### 配置沙箱环境

在正式上线前，建议配置沙箱环境进行测试：

1. 在 QQ 开放平台配置沙箱频道/群
2. 将机器人添加到沙箱环境
3. 测试所有功能正常后提交审核

## 指令列表

### 📖 帮助信息

| 指令 | 说明 | 权限 |
|------|------|------|
| `/help` | 查看帮助信息 | 所有人 |

### 📊 服务器信息

| 指令 | 说明 | 权限 |
|------|------|------|
| `/list` | 列出所有服务器 | 所有人 |
| `/status <服务器名>` | 查看服务器状态（版本、玩家、进程信息） | 所有人 |
| `/info` | 查看系统信息（操作系统、BSM版本） | 所有人 |

### 🔧 服务器操作

| 指令 | 说明 | 权限 |
|------|------|------|
| `/start <服务器名>` | 启动服务器 | 管理员 |
| `/stop <服务器名>` | 停止服务器 | 管理员 |
| `/restart <服务器名>` | 重启服务器 | 管理员 |
| `/cmd <服务器名> <命令>` | 执行服务器控制台命令 | 管理员 |
| `/update <服务器名>` | 更新服务器版本 | 管理员 |

### ⚙️ 配置管理

| 指令 | 说明 | 权限 |
|------|------|------|
| `/prop get <服务器名> [属性名]` | 查看服务器属性 | 管理员 |
| `/prop set <服务器名> <属性名> <值>` | 设置服务器属性 | 管理员 |

### 👥 白名单管理

| 指令 | 说明 | 权限 |
|------|------|------|
| `/allowlist list <服务器名>` | 查看白名单列表 | 所有人 |
| `/allowlist add <服务器名> <玩家名>` | 添加玩家到白名单 | 管理员 |
| `/allowlist remove <服务器名> <玩家名>` | 从白名单移除玩家 | 管理员 |

### 🔐 权限管理

| 指令 | 说明 | 权限 |
|------|------|------|
| `/perm list <服务器名>` | 查看权限列表 | 管理员 |
| `/perm set <服务器名> <XUID> <玩家名> <等级>` | 设置玩家权限等级 | 管理员 |

权限等级: `visitor`、`member`、`operator`

### 🎮 玩家管理

| 指令 | 说明 | 权限 |
|------|------|------|
| `/players` | 列出所有已知玩家 | 所有人 |
| `/players scan` | 扫描服务器日志获取玩家信息 | 管理员 |

### 💾 备份管理

| 指令 | 说明 | 权限 |
|------|------|------|
| `/backup list <服务器名> [类型]` | 列出备份文件 | 管理员 |
| `/backup create <服务器名> [类型]` | 创建备份 | 管理员 |
| `/backup export <服务器名>` | 导出世界 | 管理员 |

备份类型: `world`（世界）、`server`（服务器）、`all`（全部）

### 🌍 世界管理

| 指令 | 说明 | 权限 |
|------|------|------|
| `/world list` | 列出可用世界模板 | 管理员 |
| `/world install <服务器名> <文件名>` | 安装世界模板 | 管理员 |

### 使用示例

```
# 查看帮助
/help

# 列出所有服务器
/list

# 查看服务器状态
/status myserver

# 启动服务器
/start myserver

# 执行服务器命令
/cmd myserver say Hello World!

# 查看服务器属性
/prop get myserver

# 查看特定属性
/prop get myserver max-players

# 设置属性
/prop set myserver max-players 20

# 添加白名单
/allowlist add myserver Steve

# 设置玩家为管理员
/perm set myserver 1234567890123456 Steve operator

# 创建世界备份
/backup create myserver world
```

## 项目结构

```
BSM-QQ-Server/
├── src/                        # 源代码目录
│   ├── __init__.py
│   ├── main.py                 # 程序入口
│   ├── config.py               # 配置管理
│   ├── bot/                    # QQ 机器人模块
│   │   ├── __init__.py
│   │   ├── client.py           # 机器人客户端
│   │   └── handlers/           # 事件处理器
│   │       ├── __init__.py
│   │       └── command.py      # 指令处理器
│   ├── bsm/                    # BSM API 模块
│   │   ├── __init__.py
│   │   └── client.py           # API 客户端包装器
│   └── utils/                  # 工具模块
│       ├── __init__.py
│       └── helpers.py          # 工具函数
├── requirements.txt            # 依赖列表
├── .env.example                # 环境变量示例
└── README.md                   # 项目说明
```

## 开发指南

### 运行测试

```bash
# 安装测试依赖
pip install pytest

# 运行所有测试
python -m pytest tests/ -v
```

### 代码风格

项目遵循 PEP 8 代码风格规范，建议使用以下工具：

```bash
# 安装代码检查工具
pip install flake8 black

# 代码格式化
black src/

# 代码检查
flake8 src/
```

### 添加新指令

1. 在 `src/bot/handlers/command.py` 中添加新的处理方法：

```python
async def _cmd_newcmd(self, message, args):
    """新指令处理函数"""
    # 实现指令逻辑
    await self._reply(message, "指令执行成功")
```

2. 在 `__init__` 方法的 `commands` 字典中注册：

```python
self.commands: Dict[str, Callable] = {
    # ... 其他指令
    "newcmd": self._cmd_newcmd,
}
```

### 扩展 BSM API

本项目使用官方 `bsm-api-client` 库，如需添加新的 API 接口：

1. 在 `src/bsm/client.py` 中添加新的包装方法：

```python
async def new_api_method(self, server_name: str) -> SomeResult:
    """新的 API 方法"""
    return await self.api.async_new_method(server_name)
```

## 常见问题

### Q: 机器人无法连接到 BSM API？

**A:** 请检查以下几点：
1. BSM 服务是否正在运行
2. `BSM_API_URL` 配置是否正确（需要包含 `/api` 路径）
3. 网络是否可以访问 BSM API 地址
4. BSM 用户名和密码是否正确

### Q: 机器人没有响应消息？

**A:** 请检查以下几点：
1. 机器人是否成功启动（查看日志）
2. QQ 开放平台的 Intents 配置是否正确
3. 消息是否使用了正确的指令前缀
4. 是否在沙箱环境中测试（需要将机器人添加到沙箱）

### Q: 如何添加多个管理员？

**A:** 在 `.env` 文件中，用逗号分隔多个管理员 QQ 号：

```env
ADMIN_USERS=123456789,987654321,111222333
```

### Q: 如何修改指令前缀？

**A:** 修改 `.env` 文件中的 `BOT_PREFIX`：

```env
BOT_PREFIX=/minecraft
```

### Q: 日志文件在哪里？

**A:** 日志文件 `bot.log` 位于项目根目录，同时也会输出到控制台。

## 技术栈

- **Python 3.10+** - 开发语言
- **qq-botpy** - 腾讯官方 QQ 机器人 SDK
- **bsm-api-client** - BSM 官方 Python API 客户端
- **pydantic** - 数据验证
- **python-dotenv** - 环境变量管理

## 相关链接

- [QQ 机器人文档](https://bot.q.qq.com/wiki/)
- [qq-botpy GitHub](https://github.com/tencent-connect/botpy)
- [Bedrock Server Manager](https://github.com/Bedrock-OSS/bedrock-server-manager)
- [bsm-api-client](https://github.com/DMedina559/bsm-api-client)

## 许可证

本项目采用 GNU GPL v3.0 许可证，详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

⭐ 如果这个项目对你有帮助，请给一个 Star！
