# Data policy — nothing shipped

This GitHub package **does not contain assay data**.

## Excluded on purpose

- Laboratory `txt/` / `csv/` exports  
- Any Parquet / summary tables  
- Generated RDF ABox graphs  
- Query result dumps  
- The large `synthetic_data/` corpora from local experiments  

## Optional local demo (not for commit)

After install, `.\run_all.ps1` may create **local-only** synthetic tables via:

```text
src/generate_synthetic_data.py
```

Those files are:

- labelled synthetic / non-clinical  
- written under `data/` and `rdf/` (gitignored)  
- safe to delete anytime  

## Bringing your own private data

Place private exports in local `txt/` and `csv/` (gitignored), then run the pipeline.  
**Do not commit** patient-derived files.
