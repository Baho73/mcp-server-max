# mcp-server-max

[Model Context Protocol (MCP)](https://modelcontextprotocol.io) сервер для мессенджера [Max](https://max.ru) (ранее VK Teams / ICQ).

Позволяет любому MCP-совместимому AI-ассистенту (Claude, OpenClaw и др.) отправлять и читать сообщения, управлять чатами и взаимодействовать с API платформы Max.

## Возможности

| Инструмент | Описание |
|------------|----------|
| `send_message` | Отправить сообщение (текст, markdown или HTML) |
| `read_messages` | Прочитать историю чата (с фильтром по времени) |
| `list_chats` | Список групповых чатов бота |
| `get_chat_info` | Информация о чате — название, описание, количество участников |
| `get_chat_members` | Список участников чата |
| `edit_message` | Редактировать сообщение |
| `delete_message` | Удалить сообщение |
| `pin_message` | Закрепить сообщение |
| `unpin_message` | Открепить сообщение |
| `leave_chat` | Покинуть чат |
| `get_bot_info` | Информация о боте |

## Установка

```bash
pip install mcp-server-max
```

Или через [uv](https://docs.astral.sh/uv/):

```bash
uvx mcp-server-max
```

## Настройка

### Получение токена бота

1. Откройте мессенджер Max
2. Найдите `@MasterBot` (или раздел Чат-боты)
3. Создайте нового бота и скопируйте токен

### Переменные окружения

| Переменная | Обязательна | Описание |
|------------|-------------|----------|
| `MAX_BOT_TOKEN` | Да | Токен бота из @MasterBot |
| `MCP_LOG_LEVEL` | Нет | Уровень логирования: DEBUG, INFO, WARNING, ERROR (по умолчанию: INFO) |

## Использование

### Claude Desktop

Добавьте в `claude_desktop_config.json`:

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

Добавьте в `openclaw.json`:

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

### Напрямую (stdio)

```bash
export MAX_BOT_TOKEN=your-bot-token
mcp-server-max
```

## Примеры

После подключения AI-ассистент сможет:

- **Читать сообщения**: "Что нового в рабочем чате?"
- **Отправлять**: "Отправь 'Встреча в 15:00' в чат проекта"
- **Управлять чатами**: "Кто участники dev-чата?"
- **Закреплять**: "Закрепи последнее важное сообщение"

## API

Сервер использует [Max Bot API](https://dev.max.ru/docs-api) (`https://platform-api.max.ru`).

## Требования

- Python 3.10+
- Токен бота Max (из @MasterBot)

## Лицензия

MIT

## Ссылки

- [Model Context Protocol](https://modelcontextprotocol.io)
- [Max Bot API](https://dev.max.ru/docs-api)
- [Max Messenger](https://max.ru)
