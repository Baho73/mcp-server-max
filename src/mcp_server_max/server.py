"""
MODULE_CONTRACT:
  PURPOSE: MCP server for Max messenger — send/read messages, manage chats via Max Bot API
  SCOPE: stdio MCP server exposing Max platform-api.max.ru as MCP tools
  DEPENDS: mcp (Python SDK), httpx
  INPUTS: MCP tool calls via stdio (JSON-RPC)
  OUTPUTS: Tool results — messages, chat lists, bot info, updates
  LINKS: https://dev.max.ru/docs-api
  MODULE_MAP: main, serve, _send_message, _read_messages, _list_chats,
              _get_chat_info, _get_chat_members, _send_file, _edit_message,
              _delete_message, _pin_message, _get_pinned_message, _get_bot_info,
              _send_typing, _get_updates
  CHANGE_SUMMARY:
    - 0.1.0: Initial release — 11 tools for Max messenger interaction
    - 0.2.0: Add get_pinned_message, send_typing, get_updates; enhance send_message with reply_to and format
"""

# START_BLOCK_IMPORTS
from __future__ import annotations

import asyncio
import json
import logging
import os

import httpx
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server
# END_BLOCK_IMPORTS

logger = logging.getLogger("mcp-server-max")

# START_BLOCK_CONFIG
BASE_URL = "https://platform-api.max.ru"
# END_BLOCK_CONFIG


# START_BLOCK_CLIENT
_http: httpx.AsyncClient | None = None


def _get_token() -> str:
    """Read MAX_BOT_TOKEN from environment."""
    token = os.environ.get("MAX_BOT_TOKEN", "")
    if not token:
        raise EnvironmentError(
            "MAX_BOT_TOKEN is not set. "
            "Get a token from @MasterBot in Max messenger."
        )
    return token


async def _get_http() -> httpx.AsyncClient:
    """Return a cached httpx client with auth header."""
    global _http
    if _http is not None:
        return _http
    token = _get_token()
    _http = httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Authorization": token},
        timeout=30.0,
    )
    return _http


async def _close_http() -> None:
    """Close the cached httpx client."""
    global _http
    if _http is not None:
        await _http.aclose()
        _http = None


async def _api(method: str, path: str, **kwargs) -> dict:
    """Make an API call and return parsed JSON.

    Raises RuntimeError on non-2xx responses with detailed error info.
    """
    http = await _get_http()
    resp = await http.request(method, path, **kwargs)
    data = resp.json()
    if resp.status_code >= 400:
        error = data.get("message", data.get("error", str(data)))
        code = data.get("code", "")
        detail = f"Max API {resp.status_code}"
        if code:
            detail += f" [{code}]"
        detail += f": {error}"
        raise RuntimeError(detail)
    return data
# END_BLOCK_CLIENT


# START_BLOCK_HELPERS
def _ok(text: str) -> list[types.TextContent]:
    return [types.TextContent(type="text", text=text)]


def _error(msg: str) -> list[types.TextContent]:
    return [types.TextContent(type="text", text=f"ERROR: {msg}")]
# END_BLOCK_HELPERS


# START_BLOCK_TOOLS
TOOLS = [
    types.Tool(
        name="send_message",
        description="Send a text message to a Max chat or user. Supports markdown/html formatting and replies.",
        inputSchema={
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "integer",
                    "description": "Chat ID to send to (group chat)",
                },
                "user_id": {
                    "type": "integer",
                    "description": "User ID to send to (direct message)",
                },
                "text": {
                    "type": "string",
                    "description": "Message text (max 4000 characters)",
                },
                "format": {
                    "type": "string",
                    "enum": ["markdown", "html"],
                    "description": "Text format: 'markdown' or 'html' (default: plain text)",
                },
                "reply_to": {
                    "type": "string",
                    "description": "Message ID to reply to",
                },
            },
            "required": ["text"],
        },
    ),
    types.Tool(
        name="read_messages",
        description="Read messages from a Max chat. Returns up to 100 messages.",
        inputSchema={
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "integer",
                    "description": "Chat ID to read from",
                },
                "message_ids": {
                    "type": "string",
                    "description": "Comma-separated message IDs to fetch specific messages",
                },
                "count": {
                    "type": "integer",
                    "description": "Number of messages to return (1-100, default 50)",
                    "default": 50,
                },
                "from_ts": {
                    "type": "integer",
                    "description": "Start timestamp (Unix seconds)",
                },
                "to_ts": {
                    "type": "integer",
                    "description": "End timestamp (Unix seconds)",
                },
            },
        },
    ),
    types.Tool(
        name="list_chats",
        description="List group chats the bot is a member of.",
        inputSchema={
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "description": "Max chats to return (default 50)",
                    "default": 50,
                },
            },
        },
    ),
    types.Tool(
        name="get_chat_info",
        description="Get detailed information about a Max chat.",
        inputSchema={
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "integer",
                    "description": "Chat ID",
                },
            },
            "required": ["chat_id"],
        },
    ),
    types.Tool(
        name="get_chat_members",
        description="List members of a Max chat.",
        inputSchema={
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "integer",
                    "description": "Chat ID",
                },
            },
            "required": ["chat_id"],
        },
    ),
    types.Tool(
        name="edit_message",
        description="Edit an existing message in a Max chat.",
        inputSchema={
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "Message ID to edit",
                },
                "text": {
                    "type": "string",
                    "description": "New message text",
                },
            },
            "required": ["message_id", "text"],
        },
    ),
    types.Tool(
        name="delete_message",
        description="Delete a message from a Max chat.",
        inputSchema={
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "Message ID to delete",
                },
            },
            "required": ["message_id"],
        },
    ),
    types.Tool(
        name="pin_message",
        description="Pin a message in a Max chat.",
        inputSchema={
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "integer",
                    "description": "Chat ID",
                },
                "message_id": {
                    "type": "string",
                    "description": "Message ID to pin",
                },
            },
            "required": ["chat_id", "message_id"],
        },
    ),
    types.Tool(
        name="unpin_message",
        description="Unpin the pinned message in a Max chat.",
        inputSchema={
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "integer",
                    "description": "Chat ID",
                },
            },
            "required": ["chat_id"],
        },
    ),
    types.Tool(
        name="get_bot_info",
        description="Get information about the bot itself.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    types.Tool(
        name="leave_chat",
        description="Leave a Max group chat.",
        inputSchema={
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "integer",
                    "description": "Chat ID to leave",
                },
            },
            "required": ["chat_id"],
        },
    ),
    types.Tool(
        name="get_pinned_message",
        description="Get the currently pinned message in a Max chat.",
        inputSchema={
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "integer",
                    "description": "Chat ID",
                },
            },
            "required": ["chat_id"],
        },
    ),
    types.Tool(
        name="send_typing",
        description="Send a typing indicator to a Max chat. The indicator disappears after ~10 seconds or when a message is sent.",
        inputSchema={
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "integer",
                    "description": "Chat ID",
                },
            },
            "required": ["chat_id"],
        },
    ),
    types.Tool(
        name="get_updates",
        description="Get recent events/updates via long polling. Returns new messages, edits, callbacks, etc.",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of updates to return (default 100)",
                    "default": 100,
                },
                "timeout": {
                    "type": "integer",
                    "description": "Long polling timeout in seconds (default 5, keep low to avoid blocking)",
                    "default": 5,
                },
                "marker": {
                    "type": "integer",
                    "description": "Marker from previous response to get only new updates",
                },
            },
        },
    ),
]
# END_BLOCK_TOOLS


# START_BLOCK_SERVER
app = Server("mcp-server-max")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        handler = _HANDLERS.get(name)
        if handler is None:
            return _error(f"Unknown tool: {name}")
        return await handler(arguments)
    except EnvironmentError as exc:
        return _error(f"ConfigError: {exc}")
    except Exception as exc:
        logger.exception("Tool '%s' failed", name)
        return _error(f"{type(exc).__name__}: {exc}")
# END_BLOCK_SERVER


# START_BLOCK_HANDLERS
async def _send_message(args: dict) -> list[types.TextContent]:
    params = {}
    if "chat_id" in args:
        params["chat_id"] = args["chat_id"]
    elif "user_id" in args:
        params["user_id"] = args["user_id"]
    else:
        return _error("Provide either chat_id or user_id")

    body: dict = {"text": args["text"]}
    if "format" in args:
        body["format"] = args["format"]
    if "reply_to" in args:
        body["link"] = {"type": "reply", "mid": args["reply_to"]}

    data = await _api("POST", "/messages", params=params, json=body)
    return _ok(json.dumps(data, ensure_ascii=False))


async def _read_messages(args: dict) -> list[types.TextContent]:
    params = {}
    if "chat_id" in args:
        params["chat_id"] = args["chat_id"]
    if "message_ids" in args:
        params["message_ids"] = args["message_ids"]
    if "count" in args:
        params["count"] = min(args["count"], 100)
    if "from_ts" in args:
        params["from"] = args["from_ts"]
    if "to_ts" in args:
        params["to"] = args["to_ts"]

    if not params.get("chat_id") and not params.get("message_ids"):
        return _error("Provide either chat_id or message_ids")

    data = await _api("GET", "/messages", params=params)
    return _ok(json.dumps(data, ensure_ascii=False))


async def _list_chats(args: dict) -> list[types.TextContent]:
    params = {}
    if "count" in args:
        params["count"] = args["count"]

    data = await _api("GET", "/chats", params=params)
    return _ok(json.dumps(data, ensure_ascii=False))


async def _get_chat_info(args: dict) -> list[types.TextContent]:
    chat_id = args["chat_id"]
    data = await _api("GET", f"/chats/{chat_id}")
    return _ok(json.dumps(data, ensure_ascii=False))


async def _get_chat_members(args: dict) -> list[types.TextContent]:
    chat_id = args["chat_id"]
    data = await _api("GET", f"/chats/{chat_id}/members")
    return _ok(json.dumps(data, ensure_ascii=False))


async def _edit_message(args: dict) -> list[types.TextContent]:
    body = {"message_id": args["message_id"], "text": args["text"]}
    data = await _api("PUT", "/messages", json=body)
    return _ok(json.dumps(data, ensure_ascii=False))


async def _delete_message(args: dict) -> list[types.TextContent]:
    params = {"message_id": args["message_id"]}
    data = await _api("DELETE", "/messages", params=params)
    return _ok(json.dumps({"status": "ok"}, ensure_ascii=False))


async def _pin_message(args: dict) -> list[types.TextContent]:
    chat_id = args["chat_id"]
    body = {"message_id": args["message_id"]}
    data = await _api("PUT", f"/chats/{chat_id}/pin", json=body)
    return _ok(json.dumps(data, ensure_ascii=False))


async def _unpin_message(args: dict) -> list[types.TextContent]:
    chat_id = args["chat_id"]
    data = await _api("DELETE", f"/chats/{chat_id}/pin")
    return _ok(json.dumps({"status": "ok"}, ensure_ascii=False))


async def _get_bot_info(args: dict) -> list[types.TextContent]:
    data = await _api("GET", "/me")
    return _ok(json.dumps(data, ensure_ascii=False))


async def _leave_chat(args: dict) -> list[types.TextContent]:
    chat_id = args["chat_id"]
    data = await _api("DELETE", f"/chats/{chat_id}/members/me")
    return _ok(json.dumps({"status": "ok"}, ensure_ascii=False))


async def _get_pinned_message(args: dict) -> list[types.TextContent]:
    chat_id = args["chat_id"]
    data = await _api("GET", f"/chats/{chat_id}/pin")
    return _ok(json.dumps(data, ensure_ascii=False))


async def _send_typing(args: dict) -> list[types.TextContent]:
    chat_id = args["chat_id"]
    body = {"action": "typing_on"}
    data = await _api("POST", f"/chats/{chat_id}/actions", json=body)
    return _ok(json.dumps({"status": "ok"}, ensure_ascii=False))


async def _get_updates(args: dict) -> list[types.TextContent]:
    params = {}
    if "limit" in args:
        params["limit"] = args["limit"]
    if "timeout" in args:
        params["timeout"] = args["timeout"]
    else:
        params["timeout"] = 5
    if "marker" in args:
        params["marker"] = args["marker"]

    data = await _api("GET", "/updates", params=params)
    return _ok(json.dumps(data, ensure_ascii=False))


_HANDLERS = {
    "send_message": _send_message,
    "read_messages": _read_messages,
    "list_chats": _list_chats,
    "get_chat_info": _get_chat_info,
    "get_chat_members": _get_chat_members,
    "edit_message": _edit_message,
    "delete_message": _delete_message,
    "pin_message": _pin_message,
    "unpin_message": _unpin_message,
    "get_bot_info": _get_bot_info,
    "leave_chat": _leave_chat,
    "get_pinned_message": _get_pinned_message,
    "send_typing": _send_typing,
    "get_updates": _get_updates,
}
# END_BLOCK_HANDLERS


# START_BLOCK_MAIN
async def serve() -> None:
    """Run the MCP server over stdio."""
    logger.info("Starting mcp-server-max (stdio)")
    async with stdio_server() as (read, write):
        try:
            await app.run(read, write, app.create_initialization_options())
        finally:
            await _close_http()


def main() -> None:
    """CLI entry point."""
    logging.basicConfig(
        level=os.environ.get("MCP_LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    asyncio.run(serve())
# END_BLOCK_MAIN
