#!/usr/bin/env python3
"""Generate docs/ontology.html (minimal pyLODE-style documentation)."""
from __future__ import annotations

from pathlib import Path

from rdflib import Graph, RDF
from rdflib.namespace import RDFS, OWL

from utils import DOCS_DIR, ONTOLOGY_DIR

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<title>CTA Ontology</title>
<style>body{{font-family:system-ui;max-width:900px;margin:2rem auto;padding:0 1rem}}
table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:.4rem}}</style>
</head><body>
<h1>Ciliary Transport Assay Ontology</h1>
<p>Namespace: <code>https://w3id.org/gulsayyar/cta/ontology/</code></p>
<h2>Classes ({n_classes})</h2>
<table><tr><th>Class</th><th>Label</th><th>Parent</th></tr>
{classes}</table>
<h2>Object Properties ({n_oprops})</h2>
<table><tr><th>Property</th><th>Label</th></tr>
{oprops}</table>
<p><em>Generated from ontology/cta.ttl — full browser via <a href="https://www.ebi.ac.uk/ols4/ontologies">OLS</a> after BioPortal deposition.</em></p>
</body></html>"""


def main() -> None:
    g = Graph()
    g.parse(ONTOLOGY_DIR / "cta.ttl", format="turtle")

    classes = []
    for s in set(g.subjects(RDF.type, OWL.Class)):
        label = g.value(s, RDFS.label)
        parent = next(g.objects(s, RDFS.subClassOf), "")
        classes.append((str(s), str(label or ""), str(parent)))
    classes.sort()

    oprops = []
    for s in set(g.subjects(RDF.type, OWL.ObjectProperty)):
        label = g.value(s, RDFS.label)
        oprops.append((str(s), str(label or "")))
    oprops.sort()

    rows_c = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in classes)
    rows_p = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in oprops)

    html = HTML_TEMPLATE.format(
        n_classes=len(classes),
        n_oprops=len(oprops),
        classes=rows_c,
        oprops=rows_p,
    )
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    out = DOCS_DIR / "ontology.html"
    out.write_text(html, encoding="utf-8")
    print(f"Ontology HTML -> {out}")


if __name__ == "__main__":
    main()
