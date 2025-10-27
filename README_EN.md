# 🔔 Claude Code Discord Notifier

[한국어 버전 (Korean Version)](README.md)

An MCP-based system that automatically sends Discord notifications when Claude Code completes tasks.

## ✨ Key Features

- ✅ **Task Complete Notifications**: Automatic Discord alerts when coding tasks are completed
- 🏗️ **Build Complete Notifications**: Alerts for npm run build, test execution, etc.
- ❓ **User Decision Required**: Notifications when confirmation is needed before important operations
- 🚨 **Error Notifications**: Immediate alerts when errors occur during tasks
- 📊 **Rich Embeds**: Clean and informative notifications using Discord Embed format

## 📁 Project Structure

```
discord_mcp/
├── README.md                    # Korean version
├── README_EN.md                 # This file (English version)
├── MCP.md                       # Detailed MCP documentation (Korean)
├── .env                         # Environment variables (Webhook URL)
├── requirements.txt             # Python dependencies
├── discord-notify.mcp.json      # MCP server configuration
├── .claude/
│   └── CLAUDE.md               # Claude Code rules file
├── src/
│   └── discord_webhook.py      # Discord Webhook handler
└── examples/                    # Example files (coming soon)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd discord_mcp
pip install -r requirements.txt
```

### 2. Configure Discord Webhook URL

#### 2.1 Create Webhook in Discord

1. Go to Discord Server Settings → **Integrations**
2. Click **Webhooks** → **New Webhook**
3. Set webhook name (e.g., "Claude Code Notifier")
4. Select the channel to receive notifications
5. **Copy Webhook URL**

#### 2.2 Set Webhook URL in .env File

Create a `.env` file:

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
```

### 3. Run Test

```bash
cd discord_mcp
python3 src/discord_webhook.py
```

If successful, 4 test messages will be sent to your Discord channel:
1. ✅ Task complete notification
2. 🏗️ Build complete notification
3. ❓ User decision required notification
4. 📨 Simple message

## 📚 Usage

### Direct Use in Python Scripts

```python
from src.discord_webhook import DiscordNotifier
import os
from dotenv import load_dotenv

load_dotenv()

notifier = DiscordNotifier(os.getenv("DISCORD_WEBHOOK_URL"))

# Task complete notification
notifier.send_notification(
    message_type="task_complete",
    project_name="my-project",
    details="FastAPI backend implementation completed",
    metadata={
        "Execution Time": "3min 45sec",
        "Files Created": "8 files"
    }
)

# Build complete notification
notifier.send_notification(
    message_type="build_complete",
    project_name="react-frontend",
    details="Production build completed",
    metadata={
        "Build Type": "Production",
        "Bundle Size": "2.3MB"
    }
)

# User decision required
notifier.send_notification(
    message_type="user_decision",
    project_name="database-migration",
    details="Run database migration?\n\n• Modify users table\n• Estimated time: 5-10 minutes",
    metadata={
        "Risk Level": "Medium"
    }
)

# Simple message
notifier.send_simple_message("🎉 Task completed!")
```

### Use with Claude Code

Claude Code automatically sends Discord notifications when tasks complete by referencing `.claude/CLAUDE.md` rules.

#### Apply rules to Claude Code:

```bash
# Specify rules file path to Claude Code
export CLAUDE_RULES=discord_mcp/.claude/CLAUDE.md
```

Or create a symbolic link to `.claude/CLAUDE.md` in your project root:

```bash
ln -s discord_mcp/.claude/CLAUDE.md .claude/CLAUDE.md
```

## 🔧 MCP Server Configuration (Advanced)

The `discord-notify.mcp.json` file defines MCP (Model Context Protocol) server settings.

```json
{
  "mcpServers": {
    "discord-notifier": {
      "command": "python3",
      "args": ["-m", "src.discord_webhook"],
      "env": {
        "DISCORD_WEBHOOK_URL": "${DISCORD_WEBHOOK_URL}"
      }
    }
  },
  "notifications": {
    "task_complete": { "enabled": true },
    "build_complete": { "enabled": true },
    "user_decision": { "enabled": true },
    "error": { "enabled": true }
  }
}
```

## 📋 Notification Types

### 1. Task Complete (task_complete) - Green
- Coding task completed
- File creation/modification completed
- Refactoring completed

### 2. Build Complete (build_complete) - Blue
- npm run build completed
- Test execution completed
- CI/CD pipeline completed

### 3. User Decision (user_decision) - Orange
- File overwrite confirmation
- Database migration confirmation before execution
- Confirmation before important operations

### 4. Error (error) - Red
- Error occurred during task
- Build failed
- Test failed

## 🎨 Customizing Notification Messages

You can customize message format by modifying the `DiscordNotifier` class in `src/discord_webhook.py`.

### Change Embed Colors:

```python
templates = {
    "task_complete": {
        "title": "✅ Task Complete!",
        "color": 3066993,  # Green (Hex: 0x2ECC71)
        "emoji": "🎉"
    }
}
```

### Add Fields:

```python
embed["fields"].append({
    "name": "🔸 Custom Field",
    "value": "Value",
    "inline": True
})
```

## 🔍 Troubleshooting

### Notifications Not Being Sent

1. **Check Webhook URL**:
   ```bash
   cat .env
   ```
   Verify the Webhook URL is correct

2. **Check Discord Server Permissions**:
   - Verify webhook hasn't been deleted
   - Check if there are permissions to send messages to the channel

3. **Check Firewall/Network**:
   ```bash
   curl -X POST https://discord.com/api/webhooks/YOUR_WEBHOOK_URL \
     -H "Content-Type: application/json" \
     -d '{"content": "Test message"}'
   ```

### Test Script Not Running

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check Python path
which python3

# Run module directly
cd discord_mcp
python3 -m src.discord_webhook
```

## 📝 Example Scenarios

### Scenario 1: FastAPI Backend Setup

```python
notifier.send_notification(
    message_type="task_complete",
    project_name="fastapi-backend",
    details="FastAPI backend structure creation completed\n\n• Created 5 API endpoints\n• Defined database models\n• Implemented authentication middleware",
    metadata={
        "Execution Time": "3min 45sec",
        "Files Created": "8 files",
        "Lines of Code": "~450 lines"
    }
)
```

### Scenario 2: React Production Build

```python
notifier.send_notification(
    message_type="build_complete",
    project_name="react-frontend",
    details="Production build completed and optimized successfully",
    metadata={
        "Build Type": "Production",
        "Bundle Size": "2.3MB (gzip: 780KB)",
        "Build Time": "1min 23sec"
    }
)
```

### Scenario 3: Database Migration Confirmation

```python
notifier.send_notification(
    message_type="user_decision",
    project_name="database-migration",
    details="Run the following migration?\n\n• Add email_verified column to users table\n• Rebuild posts table index\n• Estimated time: 5-10 minutes",
    metadata={
        "Migration File": "20251027_add_email_verification.sql",
        "Affected Tables": "users, posts",
        "Risk Level": "Medium"
    }
)
```

## 🔧 Understanding MCP

For detailed information about how MCP (Model Context Protocol) works in this project, see [MCP.md](MCP.md) (Korean).

**Key Concepts:**
- MCP is a standardized protocol for connecting AI models (Claude) with external systems
- This project implements a custom MCP server for Discord notifications
- The MCP server acts as a bridge between Claude Code and Discord Webhook API

## 🤝 Contributing

This project is part of the 001_discord_to_notion project.

## 📄 License

MIT License

## 🔗 Related Links

- [Discord Webhook Documentation](https://discord.com/developers/docs/resources/webhook)
- [Claude Code Documentation](https://docs.claude.com/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Discord Embed Builder](https://discohook.org/) - Preview embed messages

---

**Created by**: Claude Code + Discord Integration
**Repository**: https://github.com/davidlikescat/016_discord_mcp
**Contact**: Open an issue on GitHub
