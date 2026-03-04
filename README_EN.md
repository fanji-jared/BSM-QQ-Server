# BSM-QQ-Server

🤖 A QQ bot for managing Minecraft Bedrock servers, enabling remote server management through the Bedrock Server Manager (BSM) API.

> 💡 This project is built on [bsm-api-client](https://github.com/DMedina559/bsm-api-client), the official Python asynchronous API client library for BSM.

[中文文档](README.md)

## ✨ Features

- 🔧 **Server Management**: Start, stop, restart, and update servers
- 📊 **Status Monitoring**: View server status, version, and process information
- 👥 **Player Management**: Allowlist management, permission settings, player scanning
- ⚙️ **Configuration Management**: Query and modify server properties
- 💾 **Backup Management**: Create backups, list backups, export worlds
- 🌍 **World Management**: List and install world templates
- 📱 **Multi-scenario Support**: Supports QQ groups, QQ channels, and direct messages

## 📋 Table of Contents

- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)
- [Commands](#commands)
- [Project Structure](#project-structure)
- [Development Guide](#development-guide)
- [FAQ](#faq)

## Requirements

- Python 3.10 or higher
- Bedrock Server Manager (BSM) service
- QQ Open Platform bot account

## Quick Start

### 1. Clone the Project

```bash
git clone https://github.com/fanji-jared/BSM-QQ-Server.git
cd BSM-QQ-Server
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# QQ Bot Configuration
QQ_BOT_APPID=your-bot-appid
QQ_BOT_SECRET=your-bot-secret

# BSM API Configuration
BSM_API_URL=http://your-bsm-server:11325/api
BSM_USERNAME=your-bsm-username
BSM_PASSWORD=your-bsm-password

# Bot Configuration
BOT_PREFIX=/
ADMIN_USERS=admin-qq-id-1,admin-qq-id-2

# Log Level
LOG_LEVEL=INFO
```

### 4. Run the Bot

```bash
python -m src.main
```

## Docker Deployment

### Option 1: Pull from Docker Hub (Recommended)

1. Create `.env` configuration file:
```bash
# Create .env file
cat > .env << EOF
QQ_BOT_APPID=your-bot-appid
QQ_BOT_SECRET=your-bot-secret
BSM_API_URL=http://your-bsm-server:11325/api
BSM_USERNAME=your-bsm-username
BSM_PASSWORD=your-bsm-password
BOT_PREFIX=/
ADMIN_USERS=
LOG_LEVEL=INFO
EOF
```

2. Download docker-compose config and start:
```bash
# Download config file
curl -O https://raw.githubusercontent.com/fanji-jared/BSM-QQ-Server/main/docker-compose.hub.yml

# Start service
docker-compose -f docker-compose.hub.yml up -d
```

3. Or use docker run directly:
```bash
docker run -d \
  --name bsm-qq-server \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  fanjis/bsm-qq-server:latest
```

### Option 2: Build from Source

1. Clone the project:
```bash
git clone https://github.com/fanji-jared/BSM-QQ-Server.git
cd BSM-QQ-Server
cp .env.example .env
# Edit .env file with your configuration
```

2. Build and start with Docker Compose:
```bash
docker-compose up -d
```

3. Or use Docker commands:
```bash
# Build image
docker build -t bsm-qq-server .

# Run container
docker run -d \
  --name bsm-qq-server \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  bsm-qq-server
```

### Common Commands

```bash
# View logs
docker-compose logs -f

# Stop service
docker-compose down

# Restart service
docker-compose restart
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `QQ_BOT_APPID` | ✅ | QQ bot AppID |
| `QQ_BOT_SECRET` | ✅ | QQ bot AppSecret |
| `BSM_API_URL` | ✅ | BSM API URL |
| `BSM_USERNAME` | ✅ | BSM username |
| `BSM_PASSWORD` | ✅ | BSM password |
| `BOT_PREFIX` | ❌ | Command prefix, default: `/` |
| `ADMIN_USERS` | ❌ | Admin QQ IDs |
| `LOG_LEVEL` | ❌ | Log level, default: `INFO` |

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `QQ_BOT_APPID` | ✅ | QQ bot AppID from QQ Open Platform |
| `QQ_BOT_SECRET` | ✅ | QQ bot AppSecret from QQ Open Platform |
| `BSM_API_URL` | ✅ | BSM API URL, default: `http://localhost:11325/api` |
| `BSM_USERNAME` | ✅ | BSM login username |
| `BSM_PASSWORD` | ✅ | BSM login password |
| `BOT_PREFIX` | ❌ | Bot command prefix, default: `/` |
| `ADMIN_USERS` | ❌ | Admin QQ IDs, comma-separated |
| `LOG_LEVEL` | ❌ | Log level, default: `INFO` |

### Getting QQ Bot Credentials

1. Visit [QQ Open Platform](https://bot.q.qq.com/)
2. Register and login as a developer
3. Create a bot application
4. Get `AppID` and `AppSecret` from the bot management page

## Commands

### 📖 Help

| Command | Description | Permission |
|---------|-------------|------------|
| `/help` | View help information | Everyone |

### 📊 Server Information

| Command | Description | Permission |
|---------|-------------|------------|
| `/list` | List all servers | Everyone |
| `/status <server>` | View server status (version, players, process info) | Everyone |
| `/info` | View system information (OS, BSM version) | Everyone |

### 🔧 Server Operations

| Command | Description | Permission |
|---------|-------------|------------|
| `/start <server>` | Start server | Admin |
| `/stop <server>` | Stop server | Admin |
| `/restart <server>` | Restart server | Admin |
| `/cmd <server> <command>` | Execute server console command | Admin |
| `/update <server>` | Update server version | Admin |

### ⚙️ Configuration Management

| Command | Description | Permission |
|---------|-------------|------------|
| `/prop get <server> [property]` | View server properties | Admin |
| `/prop set <server> <property> <value>` | Set server property | Admin |

### 👥 Allowlist Management

| Command | Description | Permission |
|---------|-------------|------------|
| `/allowlist list <server>` | View allowlist | Everyone |
| `/allowlist add <server> <player>` | Add player to allowlist | Admin |
| `/allowlist remove <server> <player>` | Remove player from allowlist | Admin |

### 🔐 Permission Management

| Command | Description | Permission |
|---------|-------------|------------|
| `/perm list <server>` | View permission list | Admin |
| `/perm set <server> <XUID> <player> <level>` | Set player permission level | Admin |

Permission levels: `visitor`, `member`, `operator`

### 🎮 Player Management

| Command | Description | Permission |
|---------|-------------|------------|
| `/players` | List all known players | Everyone |
| `/players scan` | Scan server logs for player info | Admin |

### 💾 Backup Management

| Command | Description | Permission |
|---------|-------------|------------|
| `/backup list <server> [type]` | List backup files | Admin |
| `/backup create <server> [type]` | Create backup | Admin |
| `/backup export <server>` | Export world | Admin |

Backup types: `world`, `server`, `all`

### 🌍 World Management

| Command | Description | Permission |
|---------|-------------|------------|
| `/world list` | List available world templates | Admin |
| `/world install <server> <filename>` | Install world template | Admin |

### Usage Examples

```
# View help
/help

# List all servers
/list

# View server status
/status myserver

# Start server
/start myserver

# Execute server command
/cmd myserver say Hello World!

# View server properties
/prop get myserver

# View specific property
/prop get myserver max-players

# Set property
/prop set myserver max-players 20

# Add to allowlist
/allowlist add myserver Steve

# Set player as operator
/perm set myserver 1234567890123456 Steve operator

# Create world backup
/backup create myserver world
```

## Project Structure

```
BSM-QQ-Server/
├── src/                        # Source code
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── config.py               # Configuration management
│   ├── bot/                    # QQ bot module
│   │   ├── __init__.py
│   │   ├── client.py           # Bot client
│   │   └── handlers/           # Event handlers
│   │       ├── __init__.py
│   │       └── command.py      # Command handler
│   ├── bsm/                    # BSM API module
│   │   ├── __init__.py
│   │   └── client.py           # API client wrapper
│   └── utils/                  # Utility module
│       ├── __init__.py
│       └── helpers.py          # Utility functions
├── requirements.txt            # Dependencies
├── .env.example                # Environment variable example
└── README.md                   # Documentation
```

## Development Guide

### Running Tests

```bash
# Install test dependencies
pip install pytest

# Run all tests
python -m pytest tests/ -v
```

### Code Style

This project follows PEP 8 code style. Recommended tools:

```bash
# Install linting tools
pip install flake8 black

# Format code
black src/

# Lint code
flake8 src/
```

### Adding New Commands

1. Add a new handler method in `src/bot/handlers/command.py`:

```python
async def _cmd_newcmd(self, message, args):
    """New command handler"""
    # Implement command logic
    await self._reply(message, "Command executed successfully")
```

2. Register in the `commands` dictionary in `__init__`:

```python
self.commands: Dict[str, Callable] = {
    # ... other commands
    "newcmd": self._cmd_newcmd,
}
```

### Extending BSM API

This project uses the official `bsm-api-client` library. To add new API interfaces:

1. Add a new wrapper method in `src/bsm/client.py`:

```python
async def new_api_method(self, server_name: str) -> SomeResult:
    """New API method"""
    return await self.api.async_new_method(server_name)
```

## FAQ

### Q: Bot cannot connect to BSM API?

**A:** Check the following:
1. Is BSM service running?
2. Is `BSM_API_URL` configured correctly (must include `/api` path)?
3. Can the network access the BSM API address?
4. Are BSM username and password correct?

### Q: Bot not responding to messages?

**A:** Check the following:
1. Did the bot start successfully (check logs)?
2. Are Intents configured correctly on QQ Open Platform?
3. Is the correct command prefix being used?
4. Are you testing in a sandbox environment (bot must be added to sandbox)?

### Q: How to add multiple admins?

**A:** In `.env` file, separate multiple QQ IDs with commas:

```env
ADMIN_USERS=123456789,987654321,111222333
```

### Q: How to change command prefix?

**A:** Modify `BOT_PREFIX` in `.env`:

```env
BOT_PREFIX=/minecraft
```

### Q: Where is the log file?

**A:** Log file `bot.log` is located in the project root directory, and also outputs to console.

## Tech Stack

- **Python 3.10+** - Programming language
- **qq-botpy** - Official Tencent QQ bot SDK
- **bsm-api-client** - Official BSM Python API client
- **pydantic** - Data validation
- **python-dotenv** - Environment variable management

## Related Links

- [QQ Bot Documentation](https://bot.q.qq.com/wiki/)
- [qq-botpy GitHub](https://github.com/tencent-connect/botpy)
- [Bedrock Server Manager](https://github.com/Bedrock-OSS/bedrock-server-manager)
- [bsm-api-client](https://github.com/DMedina559/bsm-api-client)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Issues and Pull Requests are welcome!

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

---

⭐ If this project helps you, please give it a Star!
