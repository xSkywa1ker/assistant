# n8n Workflows for Jarvis

## Import Instructions
1. Open your n8n instance and navigate to **Workflows → Import from File**.
2. Choose any JSON file from `workflows/` and import it.
3. For each workflow, configure the referenced credentials:
   - **Telegram API** – match the placeholder name `Jarvis Telegram Bot`.
   - **Google Calendar** – placeholder `Jarvis Google Service`.
   - **Notion API** – placeholder `Jarvis Notion`.
4. Update HTTP node URLs to point at your running Jarvis API (default `http://api:8000`).
5. Activate the workflow.

## Workflow Overview
- `telegram_ingest.json` – Telegram message → cleanup → `/ingest` → optional Calendar event → Telegram confirmation.
- `daily_digest_cron.json` – Daily cron at 09:00 → `/plan/next` → Telegram summary.
- `email_ingest_stub.json` – Incoming email webhook → `/ingest` → Notion page → Telegram notification.

### Calling Groq from n8n

Вариант A: OpenAI Node с кастомным Base URL
- API Key: ваш GROQ_API_KEY
- Base URL: https://api.groq.com/openai/v1
- Модель: llama-3.3-70b-versatile (или своя)

Вариант B: HTTP Request node
- POST https://api.groq.com/openai/v1/chat/completions
- Headers:
    Authorization: Bearer {{$credentials.Groq.apiKey}}
    Content-Type: application/json
- Body (raw JSON):
  ```json
  {
    "model": "llama-3.3-70b-versatile",
    "messages": [
      {"role":"system","content":"You are a helpful assistant."},
      {"role":"user","content":"Normalize this task to strict JSON schema ..."}
    ],
    "temperature": 0.2
  }
  ```
Ответ совместим со схемой OpenAI (choices[0].message.content).
