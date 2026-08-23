import pytest

from app.services.ai_client import AIClient


def test_ai_client_requires_api_key(monkeypatch):
    monkeypatch.setattr(
        "app.services.ai_client.settings.OPENAI_API_KEY",
        None,
    )

    with pytest.raises(
        ValueError,
        match="OPENAI_API_KEY não configurada",
    ):
        AIClient()

def test_ai_client_accepts_injected_api_key():
    client = AIClient(
        api_key="sk-test-key"
    )

    assert client.api_key == "sk-test-key"
    assert client.get_client() is not None