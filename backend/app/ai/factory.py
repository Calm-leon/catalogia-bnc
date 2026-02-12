import os

from app.ai.base import AIEngine
from app.ai.mock_engine import MockAIEngine


def _provider() -> str:
    return os.getenv("AI_ENGINE_PROVIDER", "mock").strip().lower()


def get_ai_engine() -> AIEngine:
    provider = _provider()
    if provider == "mock":
        return MockAIEngine()
    if provider in {"openai", "azure", "local"}:
        raise RuntimeError(f"AI engine provider '{provider}' is not implemented yet")
    raise RuntimeError(f"Unsupported AI engine provider '{provider}'")