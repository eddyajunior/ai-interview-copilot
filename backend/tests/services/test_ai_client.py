import pytest

from app.services.ai_client import AIClient


def test_ai_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError):
        AIClient()