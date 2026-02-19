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


def test_openai_uses_image_payload(monkeypatch):
    captured_json = {"value": None}

    class _Response:
        status_code = 200

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": (
                                '<?xml version="1.0" encoding="utf-8"?>\n'
                                "<rdf:RDF><rdf:Description><dc:title>x</dc:title></rdf:Description></rdf:RDF>"
                            )
                        }
                    }
                ]
            }

    class _Client:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def post(self, _url, headers=None, json=None):
            captured_json["value"] = json
            return _Response()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("app.ai.openai_engine.httpx.Client", _Client)

    engine = OpenAIEngine()
    xml = engine.generate_dublin_core_xml(
        DublinCoreInput(
            title="x",
            creator="y",
            date_value="2026-02-18",
            format_value="image/jpeg",
        ),
        image_bytes=b"fake-image",
        image_mime_type="image/jpeg",
    )

    assert "<rdf:RDF>" in xml
    message_content = captured_json["value"]["messages"][1]["content"]
    assert isinstance(message_content, list)
    assert any(item.get("type") == "image_url" for item in message_content)


def test_unknown_provider(monkeypatch):
    monkeypatch.setenv("AI_ENGINE_PROVIDER", "foo")
    with pytest.raises(RuntimeError, match="Unsupported"):
        get_ai_engine()


def test_local_uses_ollama_generate(monkeypatch):
    captured_json = {"value": None}

    class _Response:
        status_code = 200

        def json(self):
            return {
                "response": (
                    '<?xml version="1.0" encoding="utf-8"?>\n'
                    "<rdf:RDF><rdf:Description><dc:title>x</dc:title></rdf:Description></rdf:RDF>"
                )
            }

    class _Client:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def post(self, _url, headers=None, json=None):
            captured_json["value"] = json
            return _Response()

    monkeypatch.setenv("LOCAL_AI_ENGINE_URL", "http://localhost:11434")
    monkeypatch.setenv("LOCAL_AI_ENGINE_MODEL", "qwen2.5vl:3b")
    monkeypatch.setattr("app.ai.local_engine.httpx.Client", _Client)

    engine = LocalAIEngine()
    xml = engine.generate_dublin_core_xml(
        DublinCoreInput(
            title="x",
            creator="y",
            date_value="2026-02-19",
            format_value="image/jpeg",
        ),
        image_bytes=b"fake-image",
        image_mime_type="image/jpeg",
    )

    assert "<rdf:RDF>" in xml
    assert captured_json["value"]["model"] == "qwen2.5vl:3b"
    assert captured_json["value"]["stream"] is False
    assert isinstance(captured_json["value"]["images"], list)
    assert len(captured_json["value"]["images"]) == 1


def test_local_coerces_plain_text_to_rdf(monkeypatch):
    class _Response:
        status_code = 200

        def json(self):
            return {"response": "Se observa un retrato en blanco y negro de una persona en exterior."}

    class _Client:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def post(self, _url, headers=None, json=None):
            return _Response()

    monkeypatch.setenv("LOCAL_AI_ENGINE_URL", "http://localhost:11434")
    monkeypatch.setenv("LOCAL_AI_ENGINE_MODEL", "moondream:latest")
    monkeypatch.setattr("app.ai.local_engine.httpx.Client", _Client)

    engine = LocalAIEngine()
    xml = engine.generate_dublin_core_xml(
        DublinCoreInput(
            title="imagen.jpg",
            creator="Catalogador",
            date_value="2026-02-19",
            format_value="image/jpeg",
        ),
        image_bytes=b"fake-image",
        image_mime_type="image/jpeg",
    )

    assert "<rdf:RDF" in xml
    assert "<dc:title>imagen.jpg</dc:title>" in xml
    assert "<dc:description>Se observa un retrato en blanco y negro de una persona en exterior.</dc:description>" in xml


def test_local_coerces_json_to_rdf(monkeypatch):
    class _Response:
        status_code = 200

        def json(self):
            return {
                "response": (
                    '{"title":"Leon macho rugiendo en paisaje montanoso",'
                    '"type":"Image",'
                    '"descriptions":["Fotografia de un leon macho recostado en entorno natural.",'
                    '"Al fondo se observa una montana con nieve en la cumbre."],'
                    '"subjects":["Leones","Fauna silvestre","Paisajes"]}'
                )
            }

    class _Client:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def post(self, _url, headers=None, json=None):
            return _Response()

    monkeypatch.setenv("LOCAL_AI_ENGINE_URL", "http://localhost:11434")
    monkeypatch.setenv("LOCAL_AI_ENGINE_MODEL", "moondream:latest")
    monkeypatch.setattr("app.ai.local_engine.httpx.Client", _Client)

    engine = LocalAIEngine()
    xml = engine.generate_dublin_core_xml(
        DublinCoreInput(
            title="imagen.jpg",
            creator="Catalogador",
            date_value="2026-02-19",
            format_value="image/jpeg",
        ),
        image_bytes=b"fake-image",
        image_mime_type="image/jpeg",
    )

    assert "<dc:title>Leon macho rugiendo en paisaje montanoso</dc:title>" in xml
    assert "<dc:type>Image</dc:type>" in xml
    assert "<dc:description>Fotografia de un leon macho recostado en entorno natural.</dc:description>" in xml
    assert "<dc:subject>Leones</dc:subject>" in xml


def test_local_rejects_placeholder_json_values(monkeypatch):
    class _Response:
        status_code = 200

        def json(self):
            return {
                "response": (
                    '{"title":"imagen1.jpg","type":"text","descriptions":["..."],"subjects":["..."]}'
                )
            }

    class _Client:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def post(self, _url, headers=None, json=None):
            return _Response()

    monkeypatch.setenv("LOCAL_AI_ENGINE_URL", "http://localhost:11434")
    monkeypatch.setenv("LOCAL_AI_ENGINE_MODEL", "moondream:latest")
    monkeypatch.setattr("app.ai.local_engine.httpx.Client", _Client)

    engine = LocalAIEngine()
    xml = engine.generate_dublin_core_xml(
        DublinCoreInput(
            title="imagen1.jpg",
            creator="Desconocido",
            date_value="2026-02-19",
            format_value="image/jpeg",
        ),
        image_bytes=b"fake-image",
        image_mime_type="image/jpeg",
    )

    assert "<dc:type>Image</dc:type>" in xml
    assert "<dc:description>...</dc:description>" not in xml
