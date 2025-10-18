# Jarvis Assistant MVP

Jarvis is a productivity copilot that combines FastAPI, PostgreSQL, Celery, and LLM tooling to orchestrate tasks, memory, and integrations. This repository ships an end-to-end MVP that can run entirely locally or switch to external SaaS services with a configuration flag.

## Быстрый старт
1. Скопируйте файл окружения и обновите значения:
   ```bash
   cp infra/env.example .env
   ```
2. Запустите стек:
   ```bash
   cd infra
   make up
   ```
3. Примените миграции и (опционально) данные:
   ```bash
   make migrate
   make seed
   ```
   Откройте http://localhost:8000/docs для просмотра OpenAPI.

## Архитектура
```
jarvis/
  backend/            # FastAPI + Celery приложение
  infra/              # Docker Compose, Makefile, env
  orchestrations/     # Готовые n8n workflows
  tests/              # pytest unit/integration
```

### Основные компоненты
- **FastAPI Brain** (`backend/app`): REST API, OpenAPI схема, интеграции и слой памяти.
- **PostgreSQL + pgvector**: хранение данных и эмбеддингов (опционально Qdrant).
- **Celery + Redis**: фоновая обработка напоминаний, дайджестов и переиндексации памяти.
- **LLM слой**: переключение между локальным Ollama и любым OpenAI-совместимым API через `LLM_PROVIDER`.
- **Интеграции**: Google Calendar, Notion, Telegram, Email (заглушка).
- **n8n**: коллекция workflow для автоматизации.

## Локальный запуск с Ollama
1. Убедитесь, что Docker может скачать образ `ollama/ollama`.
2. В `.env` укажите:
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://ollama:11434
   ```
3. Поднимите сервисы (Ollama стартует автоматически):
   ```bash
   cd infra
   make up
   ```
4. После миграций (см. ниже) API доступно на `http://localhost:8000`.

## Переключение на внешнее LLM API
1. Создайте ключ и укажите в `.env`:
   ```env
   LLM_PROVIDER=openai
   OPENAI_BASE_URL=https://api.openai.com
   OPENAI_API_KEY=sk-...
   ```
2. Перезапустите `api`, `worker`, `beat` контейнеры:
   ```bash
   docker compose -f infra/docker-compose.yaml restart api worker beat
   ```

## Миграции и сидинг
```bash
cd infra
make migrate      # alembic upgrade head
make seed         # создаёт demo-пользователя и задачи
```

## Подключение Google Calendar
1. Создайте сервисный аккаунт или OAuth-клиент.
2. В `.env` заполните `GOOGLE_SERVICE_ACCOUNT_JSON` (base64) или OAuth-поля (`GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`).
3. Укажите `GOOGLE_CALENDAR_ID` (primary или конкретный календарь).
4. Для продакшн-сценария настройте креды в `orchestrations/n8n/workflows/telegram_ingest.json` (узел Google Calendar).

## Подключение Notion
1. Создайте интеграцию в Notion и сохраните `NOTION_API_KEY`.
2. Поделитесь базой с интеграцией и сохраните `NOTION_DATABASE_ID`.
3. Обновите `.env` и перезапустите `api`.

## Подключение Telegram
1. Создайте бота через `@BotFather`, получите `TELEGRAM_BOT_TOKEN`.
2. Укажите `TELEGRAM_WEBHOOK_SECRET` для проверки вебхуков.
3. Настройте webhook на `https://<host>/integrations/telegram/webhook` с заголовком `X-Telegram-Secret`.
4. n8n workflow `telegram_ingest.json` использует эти параметры.

## Импорт n8n воркфлоу
1. Откройте n8n (локально или SaaS).
2. Импортируйте JSON из `orchestrations/n8n/workflows/`.
3. Настройте креды (Telegram, Google Calendar, Notion) согласно README в каталоге `orchestrations/n8n`.

## Команды Makefile
Находятся в `infra/Makefile`:
- `make up` / `make down`
- `make logs`
- `make migrate` / `make makemigration`
- `make lint` / `make test`
- `make seed`
- `make doctor`

## Тестирование и качество
```bash
poetry install
poetry run ruff check backend/app
poetry run mypy backend/app
poetry run pytest
```

## Лицензия
[MIT](LICENSE)
