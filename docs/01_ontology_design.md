# Ontology design (CTA-O v2.0)

## Goals

1. Make CTA assay data **machine-queryable** (SPARQL competency questions).
2. **Reuse** community ontologies (OBI, Mondo, GO, CL, UBERON, QUDT, PROV).
3. Keep a clear **TBox / ABox** split for publication.
4. Support FAIR packaging and SHACL quality control.

## Design principles

| Principle | Implementation |
|-----------|----------------|
| Reuse-first | subclass / equivalentClass / seeAlso |
| Annotated measurement | `hasValue` + `hasUnit` (QUDT) + `hasQuantityKind` |
| Persistent IRIs | `https://w3id.org/gulsayyar/cta/` |
| Modular packaging | DCTERMS/VANN header; versionIRI |
| Competency-driven | `queries/cq*.rq` |
| No data in git | ABox generated locally only |

## Key alignments

| CTA term | External |
|----------|----------|
| `CiliaryTransportAssay` | OBI:0000070 |
| `PrimaryCiliaryDyskinesia` | MONDO:0016575 |
| `Ciliopathy` | MONDO:0005308 |
| `CiliumStructure` | GO:0005929 |
| `CiliumBeatFrequencyRegulation` | GO:0003356 |
| Nasal ciliated epithelium | CL:0002148 |
| Respiratory epithelium | UBERON:0002048 |

## Files in this repo

- `ontology/cta.ttl` — OWL TBox
- `ontology/schemes.ttl` — SKOS
- `ontology/shapes.ttl` — SHACL
- `queries/cq*.rq` — competency questions

## Competency questions

1. DNAH11 donors and Mean CBF  
2. Fast tracks on demo insert  
3. Active Area provenance  
4. Healthy vs hallmark Active Area  
5. Hz / QUDT measurements  
6. Classification stub features (synthetic only)
