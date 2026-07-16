"""
Shared utilities for the CTA knowledge-graph pipeline.

Canonical pattern: centralise IRI minting, filename parsing, and unit mappings
so preprocess / build_graph / validate all speak the same vocabulary.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from rdflib import URIRef

# --- Namespace IRIs (persistent, opaque instance IDs under these bases) ---
CTA = "https://w3id.org/gulsayyar/cta/"
CTA_DATA = CTA + "data/"
CTA_ONT = CTA + "ontology/"

# Reused community ontology prefixes (imported in TTL, not redefined here)
EXTERNAL = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "dcterms": "http://purl.org/dc/terms/",
    "dcat": "http://www.w3.org/ns/dcat#",
    "prov": "http://www.w3.org/ns/prov#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "qudt": "http://qudt.org/schema/qudt/",
    "unit": "http://qudt.org/vocab/unit/",
    "quantity": "http://qudt.org/vocab/quantitykind/",
    "obi": "http://purl.obolibrary.org/obo/OBI_",
    "cl": "http://purl.obolibrary.org/obo/CL_",
    "uberon": "http://purl.obolibrary.org/obo/UBERON_",
    "mondo": "http://purl.obolibrary.org/obo/MONDO_",
    "pato": "http://purl.obolibrary.org/obo/PATO_",
    "stato": "http://purl.obolibrary.org/obo/STATO_",
    "duo": "http://purl.obolibrary.org/obo/DUO_",
    "schema": "https://schema.org/",
    "bs": "https://bioschemas.org/",
}

# Genes observed in filenames → HGNC symbol (identifiers.org pattern)
GENE_SYMBOLS = {
    "AK8", "CCDC39", "CCDC40", "CCDC103", "DNAH5", "DNAH11", "DNAI1", "DNAI2",
    "DNAAF1", "DNAAF3", "DNAAF11", "DRC1", "HYDIN", "NEK10", "ODAD1", "ODAD2",
    "ODAD3", "ODAD4", "RSPH1", "RSPH9", "SPEF2",
}

# Hallmark ultrastructural defect genes (assumption documented in 00_data_report)
HALLMARK_GENES = {"CCDC39", "CCDC40", "DNAH11", "DNAH5", "DNAI1", "DNAI2"}

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TXT_DIR = PROJECT_ROOT / "txt"
CSV_DIR = PROJECT_ROOT / "csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
ONTOLOGY_DIR = PROJECT_ROOT / "ontology"
RDF_DIR = PROJECT_ROOT / "rdf"
QUERIES_DIR = PROJECT_ROOT / "queries"
DOCS_DIR = PROJECT_ROOT / "docs"


@dataclass
class FileMetadata:
    """Parsed metadata from a CTA filename."""

    basename: str
    group: str  # Healthy or primary gene symbol
    donor_id: str  # W<n>, M<n>, OP-<n>, SP-<n>
    visit_token: Optional[str]  # e.g. II1
    processing_tokens: list[str] = field(default_factory=list)
    culture_condition: str = "Air"
    assay_date: Optional[str] = None  # YYYY_MM_DD
    insert_number: int = 0
    insert_label: str = "Ins1"
    is_healthy: bool = False
    gene_symbols: list[str] = field(default_factory=list)
    diagnostic_subgroup: str = "Unknown"

    @property
    def insert_id(self) -> str:
        return f"{self.donor_id}_{self.insert_label}"

    @property
    def diagnostic_group(self) -> str:
        if self.is_healthy:
            return "HealthyControl"
        return "PCD"


# Filename regex: <GROUP>_[tokens]_Air_[date]_Ins<N>
# GROUP may be compound (DNAH5_DNAH11) or Healthy; donor embedded in tokens.
_FILENAME_RE = re.compile(
    r"^(?P<prefix>.+?)_Air(?:_(?P<date>\d{4}_\d{2}_\d{2}))?_Ins(?P<insert>\d+)$",
    re.IGNORECASE,
)
_DONOR_RE = re.compile(r"(?:^|_)(?P<donor>(?:W|M)\d+|OP-\d+|SP[_-]?\d+)(?:_|$)", re.I)
_VISIT_RE = re.compile(r"(II\d+|I{1,3})", re.I)


def normalise_basename(name: str) -> str:
    """Lowercase alphanumeric only — pairs txt/csv despite separator/case drift."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def parse_filename(stem: str) -> FileMetadata:
    """
    Parse CTA filename stem into structured metadata.

    Assumption (documented): first token before '_' is the gene group or 'Healthy';
    donor id is the first W<n>/M<n>/OP-<n>/SP-<n> token found in the remainder.
    """
    m = _FILENAME_RE.match(stem)
    if not m:
        raise ValueError(f"Filename does not match expected pattern: {stem}")

    prefix = m.group("prefix")
    parts = prefix.split("_")
    group_token = parts[0]

    if group_token.lower() == "healthy":
        group = "Healthy"
        is_healthy = True
        gene_symbols: list[str] = []
    else:
        is_healthy = False
        # Compound gene prefix e.g. DNAH5_DNAH11_OP-4193 or DNAH5_he_OP-3499
        gene_parts = []
        rest_start = 0
        for i, p in enumerate(parts):
            tok = re.sub(r"[^A-Za-z0-9]", "", p).upper()
            if tok in GENE_SYMBOLS or (tok.endswith("HE") and tok[:-2] in GENE_SYMBOLS):
                gene_parts.append(tok.replace("HE", "") if tok.endswith("HE") else tok)
                rest_start = i + 1
            else:
                break
        group = gene_parts[0] if gene_parts else parts[0]
        gene_symbols = gene_parts or [group]

    remainder = "_".join(parts[rest_start:]) if not is_healthy else "_".join(parts[1:])
    donor_m = _DONOR_RE.search(remainder if not is_healthy else stem)
    if not donor_m and is_healthy:
        donor_m = _DONOR_RE.search(stem)
    donor_id = donor_m.group("donor").replace("_", "-") if donor_m else "UNKNOWN"
    if donor_id.startswith("SP"):
        donor_id = donor_id.replace("_", "-")

    visit_m = _VISIT_RE.search(stem)
    visit_token = visit_m.group(1) if visit_m else None

    proc_tokens = []
    for p in parts[1 if is_healthy else rest_start:]:
        if _DONOR_RE.match(f"_{p}_") or _VISIT_RE.fullmatch(p):
            continue
        if p.upper() not in {g.upper() for g in gene_symbols} and p.lower() != "he":
            proc_tokens.append(p)

    insert_num = int(m.group("insert"))
    subgroup = "HealthyControl"
    if not is_healthy:
        subgroup = (
            "HallmarkPathognomonicDefect"
            if any(g in HALLMARK_GENES for g in gene_symbols)
            else "NormalOrNearNormalUltrastructure"
        )

    return FileMetadata(
        basename=stem,
        group=group,
        donor_id=donor_id,
        visit_token=visit_token,
        processing_tokens=proc_tokens,
        assay_date=m.group("date"),
        insert_number=insert_num,
        insert_label=f"Ins{insert_num}",
        is_healthy=is_healthy,
        gene_symbols=gene_symbols,
        diagnostic_subgroup=subgroup,
    )


def parse_time_seconds(value) -> Optional[float]:
    """Convert Imaris time column to seconds (handles decimal or mm:ss.sss)."""
    import pandas as pd

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    s = str(value).strip().replace(",", ".")
    if s in ("", "N/A", "nan", "-"):
        return None
    if ":" in s:
        parts = s.split(":")
        if len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        if len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    try:
        return float(s)
    except ValueError:
        return None


def hgnc_uri(symbol: str) -> str:
    return f"https://identifiers.org/hgnc.symbol:{symbol}"


def read_text_auto(path: Path) -> str:
    """Read file handling UTF-8, UTF-16 LE/BE BOMs (common Imaris export encodings)."""
    raw = path.read_bytes()
    if raw.startswith(b"\xff\xfe"):
        return raw.decode("utf-16-le")
    if raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16-be")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")
    return raw.decode("utf-8", errors="replace")


def detect_sep_from_text(line: str) -> str:
    return ";" if line.count(";") > line.count("\t") else "\t"


def iri(kind: str, local_id: str) -> URIRef:
    """Mint opaque stable instance IRIs under CTA_DATA."""
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", local_id)
    return URIRef(f"{CTA_DATA}{kind}/{safe}")
