# Interview FAQ (CTA-KG)

## Did you use online ontologies?

Yes — by IRI reuse in `ontology/cta.ttl` (OBI, Mondo, GO, CL, UBERON, QUDT, PROV), not by vendoring full OBO files.

## What are ontologies for here?

Shared meaning + queryable relations (SPARQL) + quality rules (SHACL). Not “upload to a free folder.”

## Is data in the GitHub repo?

**No.** Ontology + code + queries only. Optional synthetic demo is generated locally and gitignored.

## How do I query?

```powershell
.\run_all.ps1
# then open docs/query_results/ (local only)
```

## Relation to github.com/gulsayyarali/Ontologies?

That repo is building-systems OWL. CTA-KG reuses packaging patterns, not HVAC domain classes.
