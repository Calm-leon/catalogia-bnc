from __future__ import annotations

from pathlib import Path
import os
from typing import Iterable, List
from xml.etree import ElementTree

from app.schemas import XmlQualityCheck, XmlQualitySummary

RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
DC_NS = "http://purl.org/dc/elements/1.1/"

REQUIRED_INFERABLE_FIELDS = ("title", "description", "type", "format")


def evaluate_xml_quality(xml_content: str) -> XmlQualitySummary:
    checks: List[XmlQualityCheck] = []
    root = None
    description = None

    try:
        root = ElementTree.fromstring(xml_content)
        checks.append(
            XmlQualityCheck(
                key="well_formed_xml",
                passed=True,
                detail="XML es sintacticamente valido",
            )
        )
    except ElementTree.ParseError as exc:
        checks.append(
            XmlQualityCheck(
                key="well_formed_xml",
                passed=False,
                detail=f"XML invalido: {exc}",
            )
        )
        return _finalize(checks)

    expected_root = f"{{{RDF_NS}}}RDF"
    root_ok = root.tag == expected_root
    checks.append(
        XmlQualityCheck(
            key="rdf_root",
            passed=root_ok,
            detail="Estructura rdf:RDF presente" if root_ok else "Falta raiz rdf:RDF",
        )
    )

    description = root.find(f"{{{RDF_NS}}}Description")
    description_ok = description is not None
    checks.append(
        XmlQualityCheck(
            key="rdf_description",
            passed=description_ok,
            detail=(
                "Estructura rdf:Description presente"
                if description_ok
                else "Falta rdf:Description"
            ),
        )
    )

    if description is None:
        for field in REQUIRED_INFERABLE_FIELDS:
            checks.append(
                XmlQualityCheck(
                    key=f"required_{field}",
                    passed=False,
                    detail=f"Falta dc:{field}",
                )
            )
        return _finalize(checks)

    for field in REQUIRED_INFERABLE_FIELDS:
        values = list(_iter_dc_values(description, field))
        has_value = any(value.strip() for value in values)
        checks.append(
            XmlQualityCheck(
                key=f"required_{field}",
                passed=has_value,
                detail=(
                    f"Campo dc:{field} con valor"
                    if has_value
                    else f"Falta contenido en dc:{field}"
                ),
            )
        )

    return _finalize(checks)


def evaluate_xml_quality_from_relative_path(relative_path: str) -> XmlQualitySummary:
    storage_base = Path(os.getenv("STORAGE_PATH", "/data"))
    absolute_path = storage_base / Path(relative_path)
    if not absolute_path.exists():
        return XmlQualitySummary(
            passed=False,
            score=0,
            checks=[
                XmlQualityCheck(
                    key="xml_file_exists",
                    passed=False,
                    detail=f"No existe archivo en storage: {relative_path}",
                )
            ],
        )

    xml_content = absolute_path.read_text(encoding="utf-8")
    return evaluate_xml_quality(xml_content)


def _iter_dc_values(description: ElementTree.Element, field: str) -> Iterable[str]:
    tag = f"{{{DC_NS}}}{field}"
    for node in description.findall(tag):
        yield node.text or ""


def _finalize(checks: List[XmlQualityCheck]) -> XmlQualitySummary:
    if not checks:
        return XmlQualitySummary(passed=False, score=0, checks=[])
    passed_count = sum(1 for item in checks if item.passed)
    score = round((passed_count / len(checks)) * 100, 2)
    return XmlQualitySummary(
        passed=all(item.passed for item in checks),
        score=score,
        checks=checks,
    )
