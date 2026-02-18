import os

from app.ai.base import AIEngine
from app.ai.azure_engine import AzureAIEngine
from app.ai.local_engine import LocalAIEngine
from app.ai.mock_engine import MockAIEngine
from app.ai.openai_engine import OpenAIEngine


def _provider() -> str:
    return os.getenv("AI_ENGINE_PROVIDER", "mock").strip().lower()


def _env_name() -> str:
    return os.getenv("APP_ENV", "development").strip().lower()


def _fallback_to_mock_enabled() -> bool:
    return os.getenv("AI_ENGINE_FALLBACK_TO_MOCK", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _build_real_engine(provider: str) -> AIEngine:
    if provider == "openai":
        return OpenAIEngine()
    if provider == "azure":
        return AzureAIEngine()
    if provider == "local":
        return LocalAIEngine()
    raise RuntimeError(f"Unsupported AI engine provider '{provider}'")


def get_ai_engine() -> AIEngine:
    provider = _provider()
    if provider == "mock":
        return MockAIEngine()
    try:
        return _build_real_engine(provider)
    except RuntimeError as exc:
        if not _fallback_to_mock_enabled():
            raise
        if _env_name() not in {"dev", "development", "local"}:
            raise RuntimeError("AI fallback to mock is disabled outside local development") from exc
        return MockAIEngine()
