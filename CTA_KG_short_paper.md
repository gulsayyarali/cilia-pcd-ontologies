# CTA-KG: A FAIR Semantic Knowledge Graph for Primary Ciliary Dyskinesia Ciliary Transport Assay Data

**Gul Sayyar**  
*Correspondence / namespace:* `https://w3id.org/gulsayyar/cta/`  
*Companion engineering portfolio:* [github.com/gulsayyarali/Ontologies](https://github.com/gulsayyarali/Ontologies)

---

## Abstract

Primary ciliary dyskinesia (PCD) research links genetic variants to quantitative ciliary motility phenotypes. Ciliary Transport Assay (CTA) outputs—trajectories, ciliary beat frequency (CBF) and active-area measurements—are usually stored as laboratory files with weak shared vocabulary. We present **CTA-KG v2**, a FAIR OWL ontology and RDF knowledge graph that reuses OBI, Mondo, Gene Ontology (GO), CL, UBERON, QUDT and PROV-O; validates instances with SHACL; answers SPARQL competency questions; and packages outputs as an RO-Crate. The public GitHub package **ships no assay data**. A labelled synthetic demo cohort can be generated locally after clone to exercise schema and queries; it is gitignored and non-clinical. CTA-KG complements gene–disease cilia resources (GO cilia branch, CiliaMiner, CiliaHub, SYSCILIA) at the **assay-data layer**, and adopts modular ontology packaging patterns also used in the author’s building-systems OWL portfolio.

**Keywords:** FAIR; ontology; knowledge graph; PCD; ciliary transport assay; SPARQL; SHACL; RO-Crate; synthetic demo data

---

## 1. Introduction

PCD is a genetically heterogeneous ciliopathy with impaired motile ciliary function [1,2]. Functional phenotyping includes high-speed video and particle-transport assays that quantify CBF and transport behaviour [3]. Community resources improved ciliary gene and disease representation [4–8], yet CTA laboratory artefacts remain poorly integrated for machine querying.

**CTA-KG** contributes:

1. Ontology **v2.0** with publication metadata (DCTERMS/VANN), GO/HPO bridges, corrected Mondo PCD IRI (`MONDO:0016575`), and an annotated measurement pattern.
2. A reproducible Python pipeline (preprocess → RDF → SHACL → OWL-RL → SPARQL → RO-Crate).
3. Six competency questions covering genotype–phenotype, tracks, provenance and group contrast.
4. A GitHub-ready package that uses **synthetic demo data** when raw `txt/`/`csv/` are absent, with clear labelling via `cta:isSynthetic`.

Interview-style design questions—why reuse online ontologies, how to query relations, how much data are real—are addressed explicitly in the package documentation (`README.md`, `DATA.md`).

---

## 2. Related work

**Cilia vocabulary & catalogues.** GO–SYSCILIA expanded ciliary component/process terms and annotations [4]. Mondo harmonises PCD/ciliopathy disease identifiers [5]. CL/Uberon situate ciliated epithelium [6,7]. HPO encodes clinical phenotypes [8]. CiliaMiner, CilioGenics and CiliaHub publish gene–disease and prediction resources [9–11]. SYSCILIA Gold Standards curate ciliary genes [12,13].

**FAIR / assay semantics.** OBI models assays [14]; QUDT units [15]; PROV-O provenance [16]; RO-Crate packaging [17]. Precision-medicine KGs integrate disease scales but not CTA trajectories [18].

**Ontology engineering practice.** Modular OWL packaging with persistent `w3id.org` IRIs, rich ontology headers and separated TBox/ABox evaluation graphs is well established in engineering domains (e.g. Fraunhofer IBP control ontologies maintained at [19]). CTA-KG reuses that **engineering discipline**, not the building-automation domain content.

**Gap.** No published resource focuses on FAIR CTA assay graphs linking PCD genotype, motility metrics, tracks and provenance.

---

## 3. Materials and methods

### 3.1 No data in the repository

The published repository contains ontology, shapes, queries and code only. Optional local demo instances are produced by `src/generate_synthetic_data.py` (seed 42) after clone; outputs are gitignored. Classification/XAI rows remain **stubs**. See `DATA.md`.

### 3.2 Ontology design (v2.0)

`ontology/cta.ttl` follows reuse-first modelling:

| Construct | Alignment |
|-----------|-----------|
| `CiliaryTransportAssay` | subclass of OBI assay |
| `PrimaryCiliaryDyskinesia` | `owl:equivalentClass` Mondo `MONDO:0016575` |
| `CiliumStructure` / beat-frequency classes | GO `GO:0005929`, `GO:0003356`, `GO:0003341` |
| Epithelium | CL + UBERON |
| Measurements | value + QUDT unit + quantity kind |
| Provenance | PROV-O activity/agent chain |

SKOS schemes (`schemes.ttl`) provide diagnostic taxonomies with `skos:exactMatch` to Mondo. SHACL (`shapes.ttl`) enforces units and cardinalities. Ontology header includes `owl:versionIRI`, VANN prefix declarations and `rdfs:seeAlso` links to GO/Mondo papers and the author’s Ontologies portfolio [19].

### 3.3 Graph construction & validation

`build_graph.py` mints IRIs under `https://w3id.org/gulsayyar/cta/data/`, emits Turtle/JSON-LD, marks synthetic investigations with `cta:isSynthetic true`, validates with pySHACL, expands OWL-RL inverses/subclasses, and packages an RO-Crate.

### 3.4 Competency questions

CQ1 DNAH11–CBF; CQ2 fast tracks; CQ3 Active Area provenance; CQ4 healthy vs hallmark Active Area; CQ5 Hz/QUDT; CQ6 stub classification features.

---

## 4. Results

### 4.1 Ontology artefact

CTA-O v2.0 provides a stable TBox with term status tags (`vs:term_status`), inverse properties (`hasDonor`/`donorOf`, `hasTrackPoint`/`isTrackPointOf`), and bridge classes to GO/Mondo for interoperability without cloning external hierarchies.

### 4.2 Pipeline on synthetic cohort

Running `run_all.ps1` without raw files generates Parquet tables, a queryable RDF graph, SHACL report, SPARQL result files and RO-Crate metadata. A minimal committed demo ABox (`rdf/cta_demo.ttl`) illustrates key links without executing the pipeline.

### 4.3 Queryability

Competency queries recover: DNAH11-linked CBF rows; tracks with `meanSpeed > 5` on `OP-4772_Ins2`; PROV chains for Active Area; and lower mean Active Area in hallmark vs healthy groups—demonstrating the genotype–motility–provenance path that file folders obscure.

### 4.4 FAIR evidence

Persistent IRIs, open serialisations, community vocabularies, dual licensing (MIT code / CC-BY-4.0 ontology & demo data), PROV and RO-Crate address Findable–Accessible–Interoperable–Reusable requirements [20].

---

## 5. Discussion

CTA-KG shows that a CTA assay layer can be published as a standards-based ontology even when patient-level files must remain controlled. Synthetic demo data make the repository reproducible for GitHub reviewers while avoiding privacy leakage. Alignments to GO beat-frequency terms and Mondo PCD connect the assay graph to the broader cilia knowledge ecosystem [4,5,9].

**Limitations.** Synthetic values are not clinical; classification/XAI is a stub; `w3id.org` resolution and Zenodo DOI remain deployment steps; cohort scale is demo-sized.

**Future work.** OBI term request for *ciliary transport assay*; optional controlled-access real-data crate; GraphDB/Fuseki endpoint; Widoco HTML documentation generation similar to [19].

---

## 6. Conclusion

CTA-KG v2 provides a FAIR, queryable semantic model for PCD ciliary transport assays, complementary to gene–disease cilia databases. The public GitHub package pairs a publication-ready ontology with a transparent synthetic demo graph and a one-command validation/query pipeline.

**Availability.** Ontology: `ontology/cta.ttl` (v2.0.0). Pipeline: `src/`, `run_all.ps1`. Paper source: this file. Portfolio of modular OWL packaging patterns: [19].

---

## References

[1] Lucas, J.S. et al. (2020). ERS guidelines for the diagnosis of primary ciliary dyskinesia. *Eur Respir J*. https://doi.org/10.1183/13993003.01090-2019

[2] Shapiro, A.J. et al. (2018). Diagnosis of primary ciliary dyskinesia. ATS guideline. *Am J Respir Crit Care Med*. https://doi.org/10.1164/rccm.201805-0819ST

[3] Kempeneers, C. & Chilvers, M.A. (2018). Assessment of ciliary beat frequency and pattern. *Front Pediatr*.

[4] Roncaglia, P. et al. (2017). The Gene Ontology of eukaryotic cilia and flagella. *Cilia* 6:10. https://doi.org/10.1186/s13630-017-0054-8

[5] Vasilevsky, N.A. et al. (2025). Mondo: integrating disease terminology across communities. *Genetics*. https://doi.org/10.1093/genetics/iyaf215

[6] Diehl, A.D. et al. (2016). The Cell Ontology 2016. *J Biomed Semantics*. https://doi.org/10.1186/s13326-016-0088-7

[7] Mungall, C.J. et al. (2012). Uberon, an integrative multi-species anatomy ontology. *Genome Biol* 13:R5. https://doi.org/10.1186/gb-2012-13-1-r5

[8] Köhler, S. et al. (2021). The Human Phenotype Ontology in 2021. *Nucleic Acids Res*. https://doi.org/10.1093/nar/gkaa1043

[9] Turan, M.G. et al. (2023). CiliaMiner. *Database* baad047. https://doi.org/10.1093/database/baad047

[10] Pir, M.S. et al. (2024). CilioGenics. *Nucleic Acids Res*. https://doi.org/10.1093/nar/gkae554

[11] Yenisert, F. & Kaplan, O.I. (2025). Expanded ciliary gene catalogue (CiliaHub). *bioRxiv*. https://doi.org/10.1101/2025.08.22.671678

[12] van Dam, T.J.P. et al. (2013). SYSCILIA gold standard (SCGSv1). *Cilia* 2:7. https://doi.org/10.1186/2046-2530-2-7

[13] Vasquez, S.S.V. et al. (2021). SYSCILIA gold standard (SCGSv2). *Mol Biol Cell*. https://doi.org/10.1091/mbc.E21-05-0226

[14] Bandrowski, A. et al. (2016). The Ontology for Biomedical Investigations. *PLOS ONE*. https://doi.org/10.1371/journal.pone.0154556

[15] QUDT Organization. https://www.qudt.org/

[16] Lebo, T. et al. (2013). PROV-O. W3C Recommendation. https://www.w3.org/TR/prov-o/

[17] Soiland-Reyes, S. et al. (2022). Packaging research artefacts with RO-Crate. *Data Science*. https://doi.org/10.3233/DS-210053

[18] Chandak, P. et al. (2023). Building a knowledge graph to enable precision medicine. *Sci Data*. https://doi.org/10.1038/s41597-023-01960-3

[19] Sayyar, G. / Fraunhofer IBP TBS community. *Ontologies* (modular OWL packaging portfolio). https://github.com/gulsayyarali/Ontologies

[20] Wilkinson, M.D. et al. (2016). The FAIR Guiding Principles. *Sci Data*. https://doi.org/10.1038/sdata.2016.18

[21] Sayyar, G. (2026). CTA-KG software & ontology v2.0.0 (this repository).
