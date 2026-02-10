from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class PipelineMetrics:
    total_runs: int = 0
    last_run_ts: float = 0.0
    last_xml_size: int = 0
    xml_fields_present: Dict[str, int] = field(default_factory=dict)


_METRICS = PipelineMetrics()


def record_pipeline_run(xml_content: str) -> None:
    _METRICS.total_runs += 1
    _METRICS.last_run_ts = time.time()
    _METRICS.last_xml_size = len(xml_content.encode("utf-8"))
    _METRICS.xml_fields_present = {
        "dc:title": int("<dc:title>" in xml_content),
        "dc:creator": int("<dc:creator>" in xml_content),
        "dc:date": int("<dc:date>" in xml_content),
        "dc:format": int("<dc:format>" in xml_content),
    }


def export_metrics() -> Dict[str, object]:
    return {
        "pipeline": {
            "total_runs": _METRICS.total_runs,
            "last_run_ts": _METRICS.last_run_ts,
        },
        "xml_quality": {
            "last_xml_size": _METRICS.last_xml_size,
            "fields_present": _METRICS.xml_fields_present,
        },
    }