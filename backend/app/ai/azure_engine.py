import os
from typing import Any, Dict, List

import httpx

from app.ai.base import DublinCoreInput


class AzureAIEngine:
    def __init__(self) -> None:
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip().rstrip("/")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview").strip()
        self.timeout_seconds = float(os.getenv("AI_ENGINE_TIMEOUT_SECONDS", "20"))
        self.max_retries = int(os.getenv("AI_ENGINE_MAX_RETRIES", "2"))
        if not self.endpoint or not self.api_key or not self.deployment:
            raise RuntimeError("Azure provider is missing required configuration")

    def generate_dublin_core_xml(self, payload: DublinCoreInput) -> str:
        messages = self._messages(payload)
        url = (
            f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions"
            f"?api-version={self.api_version}"
        )
        last_error: Exception | None = None
        for _ in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    response = client.post(
                        url,
                        headers={
                            "api-key": self.api_key,
                            "Content-Type": "application/json",
                        },
                        json={
                            "temperature": 0,
                            "messages": messages,
                        },
                    )
                if response.status_code >= 500:
                    raise RuntimeError("Azure provider temporary failure")
                if response.status_code >= 400:
                    raise RuntimeError("Azure provider request failed")
                body = response.json()
                content = (
                    body.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )
                if not content:
                    raise RuntimeError("Azure provider returned empty content")
                return content
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                last_error = exc
                continue
        raise RuntimeError("Azure provider timed out or unreachable") from last_error

    def _messages(self, payload: DublinCoreInput) -> List[Dict[str, Any]]:
        return [
            {
                "role": "system",
                "content": (
                    "You generate only Dublin Core XML tags. "
                    "Return plain XML with dc:title, dc:creator, dc:date, dc:format, dc:description."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"title={payload.title}\n"
                    f"creator={payload.creator}\n"
                    f"date={payload.date_value}\n"
                    f"format={payload.format_value}\n"
                    "description=Pendiente de revision\n"
                ),
            },
        ]
