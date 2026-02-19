from typing import Iterable
from xml.sax.saxutils import escape


def _as_iterable(value: str | Iterable[str]) -> Iterable[str]:
    if isinstance(value, str):
        return [value]
    return value


def build_dublin_core_rdf_xml(
    *,
    title: str,
    creator: str,
    date_value: str,
    format_values: str | Iterable[str],
    description_values: str | Iterable[str] | None = None,
    type_values: str | Iterable[str] | None = None,
    publisher_values: str | Iterable[str] | None = None,
    language_values: str | Iterable[str] | None = None,
    subject_values: str | Iterable[str] | None = None,
    coverage_values: str | Iterable[str] | None = None,
    identifier_values: str | Iterable[str] | None = None,
    rights_values: str | Iterable[str] | None = None,
) -> str:
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/">',
        "  <rdf:Description>",
        f"    <dc:title>{escape(title)}</dc:title>",
        f"    <dc:creator>{escape(creator)}</dc:creator>",
    ]

    for value in _as_iterable(type_values or []):
        lines.append(f"    <dc:type>{escape(value)}</dc:type>")
    for value in _as_iterable(publisher_values or []):
        lines.append(f"    <dc:publisher>{escape(value)}</dc:publisher>")

    lines.append(f"    <dc:date>{escape(date_value)}</dc:date>")

    for value in _as_iterable(language_values or []):
        lines.append(f"    <dc:language>{escape(value)}</dc:language>")
    for value in _as_iterable(format_values):
        lines.append(f"    <dc:format>{escape(value)}</dc:format>")
    for value in _as_iterable(description_values or []):
        lines.append(f"    <dc:description>{escape(value)}</dc:description>")
    for value in _as_iterable(subject_values or []):
        lines.append(f"    <dc:subject>{escape(value)}</dc:subject>")
    for value in _as_iterable(coverage_values or []):
        lines.append(f"    <dc:coverage>{escape(value)}</dc:coverage>")
    for value in _as_iterable(identifier_values or []):
        lines.append(f"    <dc:identifier>{escape(value)}</dc:identifier>")
    for value in _as_iterable(rights_values or []):
        lines.append(f"    <dc:rights>{escape(value)}</dc:rights>")

    lines.extend(["  </rdf:Description>", "</rdf:RDF>", ""])
    return "\n".join(lines)
