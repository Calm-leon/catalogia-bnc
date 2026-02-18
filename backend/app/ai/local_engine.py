import os
import base64

import httpx

from app.ai.base import DublinCoreInput


class LocalAIEngine:
    def __init__(self) -> None:
        self.base_url = os.getenv("LOCAL_AI_ENGINE_URL", "").strip().rstrip("/")
        self.timeout_seconds = float(os.getenv("AI_ENGINE_TIMEOUT_SECONDS", "20"))
        self.max_retries = int(os.getenv("AI_ENGINE_MAX_RETRIES", "2"))
        if not self.base_url:
            raise RuntimeError("Local provider is missing required configuration")

    def generate_dublin_core_xml(
        self,
        payload: DublinCoreInput,
        image_bytes: bytes | None = None,
        image_mime_type: str | None = None,
    ) -> str:
        request_payload = {
            "prompt": "Generate Dublin Core XML",
            "metadata": {
                "title": payload.title,
                "creator": payload.creator,
                "date": payload.date_value,
                "format": payload.format_value,
                "description": "Pendiente de revision",
            },
            "image": {
                "content_type": image_mime_type or "image/jpeg",
                "data_base64": base64.b64encode(image_bytes).decode("ascii")
                if image_bytes
                else None,
            },
        }
        last_error: Exception | None = None
        for _ in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    response = client.post(
                        f"{self.base_url}/generate/dublin-core",
                        headers={"Content-Type": "application/json"},
                        json=request_payload,
                    )
                if response.status_code >= 500:
                    raise RuntimeError("Local provider temporary failure")
                if response.status_code >= 400:
                    raise RuntimeError("Local provider request failed")
                body = response.json()
                content = (
                    body.get("xml_content")
                    or body.get("content")
                    or body.get("xml")
                    or ""
                ).strip()
                if not content:
                    raise RuntimeError("Local provider returned empty content")
                return content
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                last_error = exc
                continue
        raise RuntimeError("Local provider timed out or unreachable") from last_error
