import importlib
from types import SimpleNamespace


def _prepare_settings(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://jarvis:jarvis@localhost:5432/jarvis")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    from backend.app.core import settings as settings_module

    settings_module.get_settings.cache_clear()  # type: ignore[attr-defined]


def test_provider_openai_monkeypatch(monkeypatch):
    _prepare_settings(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "DUMMY")

    from backend.app.llm import client

    importlib.reload(client)
    client._reset_openai_client()

    class DummyResponse:
        def __init__(self):
            self.choices = [SimpleNamespace(message=SimpleNamespace(content="ok"))]
            self.data = [SimpleNamespace(embedding=[0.1, 0.2])]

    class DummyChatCompletions:
        @staticmethod
        def create(**kwargs):
            return DummyResponse()

    class DummyChat:
        completions = DummyChatCompletions()

    class DummyEmbeddings:
        @staticmethod
        def create(**kwargs):
            return DummyResponse()

    class DummyClient:
        chat = DummyChat()
        embeddings = DummyEmbeddings()

    monkeypatch.setattr(client, "_get_openai_client", lambda: DummyClient())

    out = client.chat([{"role": "user", "content": "ping"}])
    assert out == "ok"

    emb = client.embed(["hello"])
    assert emb == [[0.1, 0.2]]


def test_provider_ollama_path(monkeypatch):
    _prepare_settings(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434")

    from backend.app.llm import client

    importlib.reload(client)

    monkeypatch.setattr(client, "_ollama_chat", lambda *_, **__: "pong")

    out = client.chat([{"role": "user", "content": "ping"}])
    assert out == "pong"
