#!/usr/bin/env python3
"""Phase 6: OWL-RL reasoning on core ABox (fast path for large datasets)."""
from __future__ import annotations

import sys

from rdflib import Graph
from owlrl import DeductiveClosure, OWLRL_Semantics

from utils import ONTOLOGY_DIR, RDF_DIR, DOCS_DIR

REPORT = DOCS_DIR / "inference_report.txt"


def main() -> int:
    g = Graph()
    for f in ["cta.ttl", "schemes.ttl"]:
        g.parse(ONTOLOGY_DIR / f, format="turtle")

    core = RDF_DIR / "cta_data_core.ttl"
    data = core if core.exists() else RDF_DIR / "cta_data.ttl"
    g.parse(data, format="turtle")

    before = len(g)
    DeductiveClosure(OWLRL_Semantics).expand(g)
    after = len(g)

    examples = []
    for row in g.query("""
        PREFIX cta: <https://w3id.org/gulsayyar/cta/ontology/>
        SELECT ?insert WHERE { ?insert a cta:PCDInsert . } LIMIT 3
    """):
        examples.append(f"PCDInsert instance: {row.insert}")

    for row in g.query("""
        PREFIX cta: <https://w3id.org/gulsayyar/cta/ontology/>
        SELECT ?donor WHERE {
            ?donor cta:carriesVariant ?v .
            ?v cta:variantInGene <https://identifiers.org/hgnc.symbol:DNAH11> .
        } LIMIT 2
    """):
        examples.append(f"DNAH11 variant carrier: {row.donor}")

    for row in g.query("""
        PREFIX cta: <https://w3id.org/gulsayyar/cta/ontology/>
        SELECT ?tp ?track WHERE { ?tp cta:isTrackPointOf ?track . } LIMIT 2
    """):
        examples.append(f"Inverse property materialised: {row.tp} -> {row.track}")

    out_lines = [
        "OWL-RL Inference Report",
        f"Source: {data.name}",
        f"Triples before: {before}",
        f"Triples after:  {after}",
        f"New triples:    {after - before}",
        "",
        "Concrete examples:",
    ] + [f"  - {e}" for e in examples[:5]]

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out_lines), encoding="utf-8")
    g.serialize(destination=str(RDF_DIR / "cta_data_inferred.ttl"), format="turtle")
    print("\n".join(out_lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
