import os
import base64
import json
import re

import httpx

from app.ai.base import DublinCoreInput
from app.dublin_core_xml import build_dublin_core_rdf_xml


class LocalAIEngine:
    def __init__(self) -> None:
        self.base_url = os.getenv("LOCAL_AI_ENGINE_URL", "").strip().rstrip("/")
        self.model = os.getenv("LOCAL_AI_ENGINE_MODEL", "qwen2.5vl:3b").strip()
        self.timeout_seconds = float(os.getenv("AI_ENGINE_TIMEOUT_SECONDS", "20"))
        self.max_retries = int(os.getenv("AI_ENGINE_MAX_RETRIES", "2"))
        if not self.base_url:
            raise RuntimeError("Local provider is missing required configuration")
        if not self.model:
            raise RuntimeError("Local provider is missing required configuration")

    def generate_dublin_core_xml(
        self,
        payload: DublinCoreInput,
        image_bytes: bytes | None = None,
        image_mime_type: str | None = None,
    ) -> str:
        prompt = self._build_prompt(payload)
        request_payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "images": [base64.b64encode(image_bytes).decode("ascii")] if image_bytes else [],
        }
        last_error: Exception | None = None
        for _ in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    response = client.post(
                        f"{self.base_url}/api/generate",
                        headers={"Content-Type": "application/json"},
                        json=request_payload,
                    )
                if response.status_code >= 500:
                    details = response.text[:400].strip()
                    raise RuntimeError(f"Local provider temporary failure: {details}")
                if response.status_code >= 400:
                    details = response.text[:400].strip()
                    raise RuntimeError(f"Local provider request failed: {details}")
                body = response.json()
                content = (
                    body.get("response")
                    or body.get("xml_content")
                    or body.get("content")
                    or body.get("xml")
                    or ""
                ).strip()
                if not content:
                    raise RuntimeError("Local provider returned empty content")
                normalized = self._extract_xml(content)
                if "<rdf:RDF" in normalized:
                    return normalized
                return self._coerce_content_to_rdf(payload=payload, content=content)
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                last_error = exc
                continue
        raise RuntimeError("Local provider timed out or unreachable") from last_error

    def _build_prompt(self, payload: DublinCoreInput) -> str:
        return (
            "Eres catalogador experto de la Biblioteca Nacional de Colombia. "
            "Analiza la imagen y devuelve exclusivamente JSON valido, sin markdown, sin explicaciones.\n"
            "Si un dato no se puede inferir visualmente con seguridad, omitirlo.\n"
            "Devuelve objeto JSON con esta estructura:\n"
            '{"title":"...", "type":"...", "descriptions":["..."], "subjects":["..."]}\n'
            "Reglas:\n"
            "- title: breve y descriptivo segun contenido visual.\n"
            "- type: para una fotografia usa exactamente Image.\n"
            "- descriptions: 1 o 2 descripciones objetivas del contenido visual (no usar '...' ni placeholders).\n"
            "- subjects: lista corta de temas visibles (idealmente 3 o mas).\n"
            "- No inventar nombres propios ni lugares no evidentes.\n"
            f"Contexto: filename={payload.title}, "
            f"date_hint={payload.date_value}, format_hint={payload.format_value}"
        )

    def _extract_xml(self, content: str) -> str:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("xml"):
                cleaned = cleaned[3:]
            cleaned = cleaned.strip()
        start = cleaned.find("<?xml")
        if start != -1:
            cleaned = cleaned[start:]
        end = cleaned.rfind("</rdf:RDF>")
        if end != -1:
            cleaned = cleaned[: end + len("</rdf:RDF>")]
        return cleaned

    def _coerce_content_to_rdf(self, payload: DublinCoreInput, content: str) -> str:
        title = payload.title
        type_values: list[str] = []
        description_values: list[str] = []
        subject_values: list[str] = []

        parsed = self._try_parse_json(content)
        if parsed:
            maybe_title = self._safe_text(parsed.get("title"))
            maybe_type = self._safe_text(parsed.get("type"))
            maybe_descriptions = self._safe_list(parsed.get("descriptions"))
            maybe_subjects = self._safe_list(parsed.get("subjects"))

            if maybe_title:
                title = maybe_title
            if maybe_type and maybe_type.lower() not in {"text", "texto", "txt"}:
                type_values = [maybe_type]
            elif maybe_type:
                type_values = ["Image"]
            description_values = maybe_descriptions
            subject_values = maybe_subjects
        else:
            plain = self._sanitize_plain_text(content)
            if plain:
                description_values = [plain]

        if not description_values:
            description_values = ["Pendiente de revision"]

        return build_dublin_core_rdf_xml(
            title=title,
            creator=payload.creator,
            date_value=payload.date_value,
            format_values=payload.format_value,
            type_values=type_values,
            description_values=description_values,
            subject_values=subject_values,
        )

    def _try_parse_json(self, content: str) -> dict | None:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()
        try:
            parsed = json.loads(cleaned)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            pass

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        snippet = cleaned[start : end + 1]
        try:
            parsed = json.loads(snippet)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None

    def _safe_text(self, value: object) -> str:
        if not isinstance(value, str):
            return ""
        text = " ".join(value.split())
        # Filter common hallucinated key-value fragments that are not catalog descriptions.
        if "dc:author" in text.lower():
            return ""
        if self._is_placeholder_text(text):
            return ""
        return text

    def _safe_list(self, value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        result: list[str] = []
        for item in value:
            text = self._safe_text(item)
            if text:
                result.append(text)
        return result

    def _sanitize_plain_text(self, content: str) -> str:
        text = " ".join(content.split())
        text = re.sub(r"^```(?:xml|json)?", "", text, flags=re.IGNORECASE).strip("` ").strip()
        if "dc:author" in text.lower():
            return ""
        if self._is_placeholder_text(text):
            return ""
        return text

    def _is_placeholder_text(self, text: str) -> bool:
        t = text.strip().lower()
        return t in {
            "...",
            ".",
            "n/a",
            "na",
            "none",
            "sin descripcion",
            "sin descripción",
            "pendiente",
            "pendiente de revision",
            "pendiente de revisión",
        }
