from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class DublinCoreInput:
    title: str
    creator: str
    date_value: str
    format_value: str


class AIEngine(Protocol):
    def generate_dublin_core_xml(self, payload: DublinCoreInput) -> str:
        ...