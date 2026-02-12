from app.ai.base import DublinCoreInput


class MockAIEngine:
    def generate_dublin_core_xml(self, payload: DublinCoreInput) -> str:
        return (
            "<dc:title>{}</dc:title>\n"
            "<dc:creator>{}</dc:creator>\n"
            "<dc:date>{}</dc:date>\n"
            "<dc:format>{}</dc:format>\n"
        ).format(
            payload.title,
            payload.creator,
            payload.date_value,
            payload.format_value,
        )