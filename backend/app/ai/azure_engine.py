import os
import base64
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

    def generate_dublin_core_xml(
        self,
        payload: DublinCoreInput,
        image_bytes: bytes | None = None,
        image_mime_type: str | None = None,
    ) -> str:
        messages = self._messages(payload, image_bytes=image_bytes, image_mime_type=image_mime_type)
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

    def _messages(
        self,
        payload: DublinCoreInput,
        image_bytes: bytes | None = None,
        image_mime_type: str | None = None,
    ) -> List[Dict[str, Any]]:
        content_parts: List[Dict[str, Any]] = [
            {
                "type": "text",
                "text": (
                    "Genera XML Dublin Core en formato RDF para catalogacion archivistica. "
                    "Devuelve solo XML valido."
                ),
            }
        ]
        if image_bytes:
            mime = image_mime_type or "image/jpeg"
            encoded = base64.b64encode(image_bytes).decode("ascii")
            content_parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{encoded}"},
                }
            )
        return [
            {
                "role": "system",
                "content": "Eres catalogador experto y respondes solo XML Dublin Core RDF.",
            },
            {
                "role": "user",
                "content": content_parts,
            },
        ]
