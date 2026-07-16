#!/usr/bin/env python3
"""Phase 7: Build RO-Crate research object package."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from utils import PROJECT_ROOT, CTA

CRATE_PATH = PROJECT_ROOT / "ro-crate-metadata.json"


def main() -> None:
    crate = {
        "@context": "https://w3id.org/ro/crate/1.1/context",
        "@graph": [
            {
                "@id": "./",
                "@type": "Dataset",
                "name": "PCD Ciliary Transport Assay Knowledge Graph",
                "description": (
                    "FAIR package: CTA trajectories, CBF summaries, OWL ontology, "
                    "SHACL shapes, RDF knowledge graph for Primary Ciliary Dyskinesia."
                ),
                "datePublished": datetime.utcnow().strftime("%Y-%m-%d"),
                "license": "https://creativecommons.org/licenses/by/4.0/",
                "url": CTA,
                "creator": {"@id": "https://orcid.org/0000-0002-1825-0097"},
                "hasPart": [
                    {"@id": "data/processed/insert_summary.parquet"},
                    {"@id": "rdf/cta_data.ttl"},
                    {"@id": "ontology/cta.ttl"},
                    {"@id": "src/build_graph.py"},
                ],
            },
            {
                "@id": "https://orcid.org/0000-0002-1825-0097",
                "@type": "Person",
                "name": "Gul Sayyar",
            },
            {
                "@id": "data/processed/insert_summary.parquet",
                "@type": "File",
                "name": "Insert summary table",
                "encodingFormat": "application/parquet",
                "license": "https://creativecommons.org/licenses/by/4.0/",
            },
            {
                "@id": "rdf/cta_data.ttl",
                "@type": "File",
                "name": "RDF knowledge graph",
                "encodingFormat": "text/turtle",
                "license": "https://creativecommons.org/licenses/by/4.0/",
            },
            {
                "@id": "ontology/cta.ttl",
                "@type": "File",
                "name": "CTA ontology TBox",
                "encodingFormat": "text/turtle",
                "license": "https://creativecommons.org/licenses/by/4.0/",
            },
            {
                "@id": "src/build_graph.py",
                "@type": "File",
                "name": "Graph builder",
                "encodingFormat": "text/x-python",
                "license": "https://opensource.org/licenses/MIT",
            },
            {
                "@id": "txt/",
                "@type": "File",
                "name": "Raw trajectory exports (controlled access)",
                "additionalProperty": {
                    "@type": "PropertyValue",
                    "name": "DUO",
                    "value": "http://purl.obolibrary.org/obo/DUO_0000007",
                },
            },
        ],
    }
    CRATE_PATH.write_text(json.dumps(crate, indent=2), encoding="utf-8")
    print(f"RO-Crate -> {CRATE_PATH}")


if __name__ == "__main__":
    main()
