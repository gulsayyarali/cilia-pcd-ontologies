# CTA-KG — FAIR ontology & pipeline for PCD Ciliary Transport Assays

[![License: MIT](https://img.shields.io/badge/code-MIT-yellow.svg)](LICENSE)
[![Ontology](https://img.shields.io/badge/ontology-CC--BY--4.0-blue.svg)](LICENSE-DATA)
[![Data](https://img.shields.io/badge/data-not%20included-lightgrey.svg)](DATA.md)

**CTA-KG** publishes a reusable **OWL ontology**, **SHACL shapes**, **SPARQL competency questions**, and a **Python pipeline** for modelling Primary Ciliary Dyskinesia (PCD) *Ciliary Transport Assay* (CTA) data as a FAIR knowledge graph.

> **This repository does not include assay data** (no `txt/`, `csv/`, Parquet, or RDF ABox dumps).  
> Demo instances can be **generated locally** after clone (synthetic, labelled, non-clinical).  
> See [DATA.md](DATA.md).

**Ontology IRI:** `https://w3id.org/gulsayyar/cta/ontology/`  
**Draft paper:** [CTA_KG_short_paper.md](CTA_KG_short_paper.md)

---

## Contents (what is in this repo)

```
.
├── ontology/          # TBox + SKOS + SHACL (publishable)
├── queries/           # SPARQL competency questions
├── src/               # Pipeline (generate → RDF → validate → query)
├── docs/              # Design & FAIR notes
├── CTA_KG_short_paper.md
├── requirements.txt
└── run_all.ps1
```

**Not included:** laboratory files, synthetic cohorts on disk, generated graphs, query result dumps.

---

## Quick start

```powershell
git clone https://github.com/<you>/CTA-KG.git
cd CTA-KG
py -m pip install -r requirements.txt
.\run_all.ps1
```

`run_all.ps1` will:

1. Generate a **local synthetic demo cohort** (not committed)
2. Build RDF, validate with SHACL, run SPARQL CQs, write RO-Crate locally

Generated artefacts stay on your machine (`data/`, `rdf/`, `docs/query_results/`) and are gitignored.

---

## Ontology (v2.0)

Reuse-first alignments:

| CTA concept | External standard |
|-------------|-------------------|
| Assay | OBI |
| PCD | Mondo `MONDO:0016575` |
| Cilium / CBF processes | GO (`GO:0005929`, `GO:0003356`, …) |
| Cell / tissue | CL, UBERON |
| Units | QUDT |
| Provenance | PROV-O |

Packaging patterns (persistent IRIs, DCTERMS/VANN metadata, TBox/ABox split) follow modular OWL practice also used in [gulsayyarali/Ontologies](https://github.com/gulsayyarali/Ontologies) (building-systems domain — patterns only).

---

## Competency questions

| ID | Question |
|----|----------|
| CQ1 | DNAH11 donors × Mean CBF |
| CQ2 | Fast tracks on a demo insert |
| CQ3 | Active Area provenance |
| CQ4 | Healthy vs hallmark Active Area |
| CQ5 | Hz / QUDT measurements |
| CQ6 | Classification stub features (synthetic only) |

---

## Citation

See [CITATION.cff](CITATION.cff).

---

## Licence

- Code (`src/`): [MIT](LICENSE)
- Ontology & documentation: [CC-BY-4.0](LICENSE-DATA)
