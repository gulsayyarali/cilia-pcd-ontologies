# FAIR Principles Mapping

Each FAIR sub-principle mapped to the **exact artefact** that satisfies it in this package.

## Findable

| Principle | Artefact | How |
|-----------|----------|-----|
| **F1** (meta)data assigned globally unique ID | `https://w3id.org/gulsayyar/cta/` | Persistent w3id.org namespace for ontology + data IRIs |
| **F2** data described with rich metadata | `rdf/metadata.ttl`, `ro-crate-metadata.json` | DCAT Dataset + RO-Crate schema.org JSON-LD |
| **F3** metadata specifies identifier | `CITATION.cff`, `dcterms:identifier` in metadata.ttl | DOI placeholder at Zenodo deposition |
| **F4** metadata registered in searchable resource | `docs/03_publication_deposition_plan.md` | Zenodo, BioPortal, FAIRsharing registration plan |

## Accessible

| Principle | Artefact | How |
|-----------|----------|-----|
| **A1** retrievable by standard protocol | `rdf/cta_data.ttl`, `.jsonld` | HTTP-resolvable w3id.org; open formats |
| **A1.1** open, free, universal protocol | GitHub + Zenodo mirror | HTTPS GET |
| **A1.2** metadata accessible even if data restricted | `ro-crate-metadata.json` | Crate metadata public; raw txt/csv flagged controlled |
| **A2** metadata accessible long-term | w3id.org redirect + Zenodo DOI | Community persistence services |

## Interoperable

| Principle | Artefact | How |
|-----------|----------|-----|
| **I1** formal, accessible, broadly applicable language | `ontology/cta.ttl`, `rdf/cta_data.ttl` | RDF/OWL/Turtle + JSON-LD |
| **I2** FAIR vocabularies | OBI, CL, UBERON, MONDO, QUDT, PROV-O, SKOS, DCAT | Reused IRIs, not local redefinitions |
| **I3** qualified references to metadata | `cta:hasUnit unit:HZ`, `skos:exactMatch mondo:...` | QUDT units, SKOS mappings |

## Reusable

| Principle | Artefact | How |
|-----------|----------|-----|
| **R1** richly described with accurate attributes | `docs/data_dictionary.md`, PROV chain | Units, dtypes, provenance per measurement |
| **R1.1** clear, accessible usage licence | `LICENSE`, `LICENSE-DATA`, `dcterms:license` | MIT (code), CC-BY-4.0 (data/ontology) |
| **R1.2** associated with detailed provenance | PROV-O in ABox | `wasGeneratedBy`, `wasAttributedTo`, `wasAssociatedWith` |
| **R1.3** community conventions | OBI assay pattern, Bioschemas/RO-Crate profile, DUO | Standard biomedical KG patterns |

## Sensitive human data

| Concern | Artefact | Approach |
|---------|----------|----------|
| Identifiability | Pseudonyms only in open graph | `OP-<n>`, `W<n>` — no names/dates of birth |
| Genetic data | DUO `DUO:0000007` on raw folders | Controlled access tier in deposition plan |
| Data use | `cta:hasDataUseRestriction` | DUO general research use on open aggregate |

## Validation & trust

| Mechanism | Artefact |
|-----------|----------|
| Structural validation | `ontology/shapes.ttl` + `docs/validation_report.txt` |
| Logical inference | `rdf/cta_data_inferred.ttl` + `docs/inference_report.txt` |
| Query verification | `queries/cq*.rq` + `docs/query_results/` |
