#!/usr/bin/env python3
"""
Phase 8: Run SPARQL competency questions from queries/*.rq

Canonical pattern: each CQ in plain English maps 1:1 to a .rq file.
"""
from __future__ import annotations

import sys
from pathlib import Path

from rdflib import Graph

from utils import QUERIES_DIR, RDF_DIR, ONTOLOGY_DIR, DOCS_DIR

RESULTS_DIR = DOCS_DIR / "query_results"


def load_graph() -> Graph:
    g = Graph()
    for f in ["cta.ttl", "schemes.ttl"]:
        g.parse(ONTOLOGY_DIR / f, format="turtle")
    # ABox is generated locally (not in git): run build_graph.py / run_all.ps1 first
    full = RDF_DIR / "cta_data.ttl"
    if not full.exists():
        raise FileNotFoundError(
            "rdf/cta_data.ttl not found. This repo ships no data — run .\\run_all.ps1 first."
        )
    g.parse(full, format="turtle")
    return g


def run_query(g: Graph, rq_path: Path) -> str:
    q = rq_path.read_text(encoding="utf-8")
    results = g.query(q)
    rows = list(results)
    if not rows:
        return "(no results)"
    vars_ = [str(v) for v in results.vars]
    lines = ["\t".join(vars_)]
    for row in rows[:50]:
        lines.append("\t".join(str(row[v]) if row[v] is not None else "" for v in results.vars))
    if len(rows) > 50:
        lines.append(f"... ({len(rows)} total rows)")
    return "\n".join(lines)


def main() -> int:
    g = load_graph()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rq_files = sorted(QUERIES_DIR.glob("cq*.rq"))
    if not rq_files:
        print("No query files found in queries/")
        return 1

    summary_lines = ["# SPARQL Competency Question Results\n"]
    for rq in rq_files:
        out = run_query(g, rq)
        result_path = RESULTS_DIR / f"{rq.stem}.txt"
        result_path.write_text(out, encoding="utf-8")
        n_rows = max(0, len(out.splitlines()) - 1) if out != "(no results)" else 0
        print(f"{rq.name}: {n_rows} rows")
        summary_lines.append(f"## {rq.stem}\n```\n{out[:1500]}\n```\n")

    (DOCS_DIR / "query_results_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
