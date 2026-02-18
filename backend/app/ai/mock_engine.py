from app.ai.base import DublinCoreInput
from app.dublin_core_xml import build_dublin_core_rdf_xml


class MockAIEngine:
    def generate_dublin_core_xml(self, payload: DublinCoreInput) -> str:
        return build_dublin_core_rdf_xml(
            title=payload.title,
            creator=payload.creator,
            date_value=payload.date_value,
            format_values=payload.format_value,
            description_values="Pendiente de revision",
        )
