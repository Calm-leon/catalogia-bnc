import os
from typing import Any, Dict, List

import httpx

from app.ai.base import DublinCoreInput


class OpenAIEngine:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
        self.timeout_seconds = float(os.getenv("AI_ENGINE_TIMEOUT_SECONDS", "20"))
        self.max_retries = int(os.getenv("AI_ENGINE_MAX_RETRIES", "2"))
        if not self.api_key:
            raise RuntimeError("OpenAI provider is missing required configuration")

    def generate_dublin_core_xml(self, payload: DublinCoreInput) -> str:
        messages = self._messages(payload)
        last_error: Exception | None = None
        for _ in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    response = client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": self.model,
                            "temperature": 0,
                            "messages": messages,
                        },
                    )
                if response.status_code >= 500:
                    raise RuntimeError("OpenAI provider temporary failure")
                if response.status_code >= 400:
                    raise RuntimeError("OpenAI provider request failed")
                body = response.json()
                content = (
                    body.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )
                if not content:
                    raise RuntimeError("OpenAI provider returned empty content")
                return content
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                last_error = exc
                continue
        raise RuntimeError("OpenAI provider timed out or unreachable") from last_error

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
