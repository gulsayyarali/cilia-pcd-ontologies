#!/usr/bin/env python3
"""
Phase 5: SHACL validation with pyshacl.

Canonical pattern: OWL defines semantics; SHACL enforces data shape at release time.
"""
from __future__ import annotations

import sys
from pathlib import Path

from pyshacl import validate
from rdflib import Graph

from utils import ONTOLOGY_DIR, RDF_DIR, DOCS_DIR

REPORT_PATH = DOCS_DIR / "validation_report.txt"


def main() -> int:
    data = Graph()
    data.parse(RDF_DIR / "cta_data.ttl", format="turtle")
    data.parse(ONTOLOGY_DIR / "cta.ttl", format="turtle")
    data.parse(ONTOLOGY_DIR / "schemes.ttl", format="turtle")

    shapes = Graph()
    shapes.parse(ONTOLOGY_DIR / "shapes.ttl", format="turtle")

    conforms, report_graph, report_text = validate(
        data_graph=data,
        shacl_graph=shapes,
        inference="none",
        abort_on_first=False,
        meta_shacl=False,
        advanced=False,
    )

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report_text, encoding="utf-8")

    status = "CONFORMS" if conforms else "VIOLATIONS FOUND"
    print(f"SHACL validation: {status}")
    print(f"Report: {REPORT_PATH}")
    if not conforms:
        # Print summary for debugging
        print(report_text[:3000])
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
