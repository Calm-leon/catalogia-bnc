import pytest

from app.ai.factory import get_ai_engine
from app.ai.mock_engine import MockAIEngine


def test_default_engine_is_mock(monkeypatch):
    monkeypatch.delenv("AI_ENGINE_PROVIDER", raising=False)
    engine = get_ai_engine()
    assert isinstance(engine, MockAIEngine)


def test_known_unimplemented_provider(monkeypatch):
    monkeypatch.setenv("AI_ENGINE_PROVIDER", "openai")
    with pytest.raises(RuntimeError, match="not implemented"):
        get_ai_engine()


def test_unknown_provider(monkeypatch):
    monkeypatch.setenv("AI_ENGINE_PROVIDER", "foo")
    with pytest.raises(RuntimeError, match="Unsupported"):
        get_ai_engine()