import os
import base64
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

    def generate_dublin_core_xml(
        self,
        payload: DublinCoreInput,
        image_bytes: bytes | None = None,
        image_mime_type: str | None = None,
    ) -> str:
        messages = self._messages(payload, image_bytes=image_bytes, image_mime_type=image_mime_type)
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
                normalized = self._normalize_xml(content)
                if "<rdf:RDF" not in normalized:
                    raise RuntimeError("OpenAI provider returned invalid XML structure")
                return normalized
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                last_error = exc
                continue
        raise RuntimeError("OpenAI provider timed out or unreachable") from last_error

    def _messages(
        self,
        payload: DublinCoreInput,
        image_bytes: bytes | None = None,
        image_mime_type: str | None = None,
    ) -> List[Dict[str, Any]]:
        system_prompt = os.getenv(
            "AI_ENGINE_SYSTEM_PROMPT",
            (
                "Eres un catalogador experto de la Biblioteca Nacional de Colombia especializado "
                "en descripcion archivistica y fotografica. Responde solo XML Dublin Core en RDF. "
                "No inventes nombres propios ni fechas no verificables visualmente."
            ),
        ).strip()
        user_text = self._user_prompt(payload)
        content_parts: List[Dict[str, Any]] = [{"type": "text", "text": user_text}]
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
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": content_parts,
            },
        ]

    def _user_prompt(self, payload: DublinCoreInput) -> str:
        return (
            "Analiza la imagen y genera registro catalografico XML Dublin Core en formato RDF.\n"
            "Responde solo XML valido con: dc:title, dc:creator, dc:type, dc:publisher, dc:date, "
            "dc:language, dc:format (repetible), dc:description (repetible), dc:subject (repetible), "
            "dc:coverage, dc:identifier, dc:rights.\n"
            "Si un campo no puede deducirse con seguridad visual, omitirlo.\n"
            "Usar espanol neutro, redaccion formal y objetiva.\n"
            f"Contexto tecnico: filename={payload.title}, creator_hint={payload.creator}, "
            f"date_hint={payload.date_value}, format_hint={payload.format_value}\n"
            "Usar exactamente dc:identifier=URL_DEL_OBJETO y dc:rights=Biblioteca Nacional de Colombia "
            "solo cuando corresponda a la politica definida."
        )

    def _normalize_xml(self, content: str) -> str:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("xml"):
                cleaned = cleaned[3:]
            cleaned = cleaned.strip()
        return cleaned
