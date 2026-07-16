# Publication & Deposition Plan

Tiered deposition strategy: **as open as possible, as closed as necessary**.

## Tier 1 — Open (immediate upon release)

| Artefact | Target repository | Rationale |
|----------|-------------------|-----------|
| Processed tables (`data/processed/`) | **Zenodo** (DOI) | Standard open research data archive; GitHub-integrated |
| RDF knowledge graph + ontology | **Zenodo** + **BioPortal** / **OLS** | Citable DOI; ontology discoverable via OBO Foundry ecosystem |
| Code pipeline (`src/`) | **GitHub** + Zenodo mirror | Version control + archived release |
| RO-Crate package | Zenodo | Single-download research object |
| FAIRsharing registration | **FAIRsharing.org** | Standards/database registration for discoverability |

**Persistent ID stack**: ORCID (creator) + ROR (institution) + Zenodo DOI (dataset) + w3id.org (ontology/data IRIs).

**Licence**: CC-BY-4.0 (data/ontology), MIT (code).

## Tier 2 — Embargoed / controlled (until manuscript acceptance)

| Artefact | Target repository | Rationale |
|----------|-------------------|-----------|
| Raw microscopy videos (.avi) | **BioImage Archive** (EMBL-EBI) | Community standard for imaging; REMBI metadata |
| Curated cloud access | **IDR** (Image Data Resource) | Reference publication-quality image browsing |
| Format | OME-TIFF / OME-NGFF | Open microscopy formats |

**Metadata standard**: REMBI (Recommended Metadata for Biological Images).

## Tier 3 — Controlled access (human genetic / identifiable)

| Artefact | Target repository | Rationale |
|----------|-------------------|-----------|
| Linked genomic identifiers | **EGA** (European Genome-phenome Archive) | GDPR-compliant controlled access for human genetic data |
| Variant records | **ClinVar** / **LOVD** | Community variant databases with HGNC gene links |

**DUO codes**: `DUO:0000007` (disease-specific research) for controlled tier; general research use for open aggregates.

## Tier 4 — Ontology publication

| Artefact | Target | Rationale |
|----------|--------|-----------|
| `ontology/cta.ttl` | BioPortal + OLS | Term search, mapping, community reuse |
| Persistent IRI | `https://w3id.org/gulsayyar/cta/ontology/` | w3id.org redirect to GitHub/PURL |

## Pre-deposition checklist

- [ ] Remove any direct identifiers from open release (verify pseudonyms only)
- [ ] Obtain DUO/Data Access Committee approval for EGA submission
- [ ] Mint Zenodo DOI and update `CITATION.cff` + `rdf/metadata.ttl`
- [ ] Register on FAIRsharing (database + standards)
- [ ] Submit ontology to BioPortal
- [ ] Link ORCID + ROR in all metadata

## Alternatives considered

| Repository | Role | Why not primary |
|------------|------|-----------------|
| Dryad | Open data | Zenodo preferred for EU GitHub integration |
| OSF | Project workspace | Less DOI citation traction in life sciences |
| Harvard Dataverse | Institutional | Good backup; Zenodo more common for EU |

## Timeline

1. **Now**: Open package (processed + KG + ontology) → Zenodo draft
2. **Manuscript submission**: Embargo raw imaging → BioImage Archive
3. **Acceptance**: Release embargo; publish EGA if genomic links included
4. **Post-publication**: ClinVar/LOVD variant deposition; FAIRsharing registration
