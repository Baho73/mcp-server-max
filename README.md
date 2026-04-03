# mcp-server-max

[![README на русском](https://img.shields.io/badge/README-на_русском-blue)](README.ru.md)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for [Max](https://max.ru) messenger (formerly VK Teams / ICQ).

Lets any MCP-compatible AI assistant (Claude, OpenClaw, etc.) send and read messages, manage chats, and interact with the Max platform API.

## Features

| Tool | Description |
|------|-------------|
| `send_message` | Send a text message (plain, markdown, or HTML) |
| `read_messages` | Read chat history (with time range and pagination) |
| `list_chats` | List group chats the bot is a member of |
| `get_chat_info` | Chat details — title, description, members count |
| `get_chat_members` | List members of a chat |
| `edit_message` | Edit an existing message |
| `delete_message` | Delete a message |
| `pin_message` | Pin a message in a chat |
| `unpin_message` | Unpin the pinned message |
| `leave_chat` | Leave a group chat |
| `get_bot_info` | Get information about the bot |

## Installation

```bash
pip install mcp-server-max
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uvx mcp-server-max
```

## Configuration

### Getting a bot token

1. Open Max messenger
2. Find `@MasterBot` (or go to Chat-bots section)
3. Create a new bot and copy the token

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MAX_BOT_TOKEN` | Yes | Bot token from @MasterBot |
| `MCP_LOG_LEVEL` | No | Log level: DEBUG, INFO, WARNING, ERROR (default: INFO) |

## Usage

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "max": {
      "command": "mcp-server-max",
      "env": {
        "MAX_BOT_TOKEN": "your-bot-token"
      }
    }
  }
}
```

### Claude Code

```json
{
  "mcpServers": {
    "max": {
      "command": "mcp-server-max",
      "env": {
        "MAX_BOT_TOKEN": "your-bot-token"
      }
    }
  }
}
```

### OpenClaw

Add to `openclaw.json`:

```json
{
  "mcp": {
    "servers": {
      "max": {
        "command": "mcp-server-max",
        "env": {
          "MAX_BOT_TOKEN": "your-bot-token"
        }
      }
    }
  }
}
```

### Direct (stdio)

```bash
export MAX_BOT_TOKEN=your-bot-token
mcp-server-max
```

## Examples

Once connected, your AI assistant can:

- **Read messages**: "What are the latest messages in the team chat?"
- **Send messages**: "Send 'Meeting at 3pm' to the project chat"
- **Manage chats**: "Who are the members of the dev chat?"
- **Pin messages**: "Pin the last important message"

## API

This server uses the [Max Bot API](https://dev.max.ru/docs-api) (`https://platform-api.max.ru`).

## Requirements

- Python 3.10+
- A Max bot token (from @MasterBot)

## License

MIT

## Links

- [Model Context Protocol](https://modelcontextprotocol.io)
- [Max Bot API Docs](https://dev.max.ru/docs-api)
- [Max Messenger](https://max.ru)
