import pytest
import httpx

from app.ai.factory import get_ai_engine
from app.ai.local_engine import LocalAIEngine
from app.ai.mock_engine import MockAIEngine
from app.ai.openai_engine import OpenAIEngine
from app.ai.azure_engine import AzureAIEngine
from app.ai.base import DublinCoreInput


def test_default_engine_is_mock(monkeypatch):
    monkeypatch.delenv("AI_ENGINE_PROVIDER", raising=False)
    engine = get_ai_engine()
    assert isinstance(engine, MockAIEngine)
    xml = engine.generate_dublin_core_xml(
        DublinCoreInput(
            title="Titulo",
            creator="Autor",
            date_value="2026-02-18",
            format_value="image/jpeg",
        )
    )
    assert xml.startswith('<?xml version="1.0" encoding="utf-8"?>')
    assert "<rdf:RDF" in xml
    assert "<dc:title>Titulo</dc:title>" in xml


def test_openai_provider_selected(monkeypatch):
    monkeypatch.setenv("AI_ENGINE_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    engine = get_ai_engine()
    assert isinstance(engine, OpenAIEngine)


def test_azure_provider_selected(monkeypatch):
    monkeypatch.setenv("AI_ENGINE_PROVIDER", "azure")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt")
    engine = get_ai_engine()
    assert isinstance(engine, AzureAIEngine)


def test_local_provider_selected(monkeypatch):
    monkeypatch.setenv("AI_ENGINE_PROVIDER", "local")
    monkeypatch.setenv("LOCAL_AI_ENGINE_URL", "http://localhost:8080")
    engine = get_ai_engine()
    assert isinstance(engine, LocalAIEngine)


def test_provider_missing_configuration(monkeypatch):
    monkeypatch.setenv("AI_ENGINE_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="missing required configuration"):
        get_ai_engine()


def test_fallback_to_mock_enabled_in_development(monkeypatch):
    monkeypatch.setenv("AI_ENGINE_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AI_ENGINE_FALLBACK_TO_MOCK", "true")
    monkeypatch.setenv("APP_ENV", "development")
    engine = get_ai_engine()
    assert isinstance(engine, MockAIEngine)


def test_fallback_to_mock_rejected_in_production(monkeypatch):
    monkeypatch.setenv("AI_ENGINE_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AI_ENGINE_FALLBACK_TO_MOCK", "true")
    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(RuntimeError, match="disabled outside local development"):
        get_ai_engine()


def test_openai_timeout_error_is_controlled(monkeypatch):
    class _TimeoutClient:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def post(self, *_args, **_kwargs):
            raise httpx.TimeoutException("boom")

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("app.ai.openai_engine.httpx.Client", _TimeoutClient)

    engine = OpenAIEngine()
    with pytest.raises(RuntimeError, match="timed out or unreachable"):
        engine.generate_dublin_core_xml(
            DublinCoreInput(
                title="a",
                creator="b",
                date_value="2026-02-18",
                format_value="image/jpeg",
            )
        )


def test_unknown_provider(monkeypatch):
    monkeypatch.setenv("AI_ENGINE_PROVIDER", "foo")
    with pytest.raises(RuntimeError, match="Unsupported"):
        get_ai_engine()
