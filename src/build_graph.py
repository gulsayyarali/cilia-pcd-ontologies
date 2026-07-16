#!/usr/bin/env python3
"""
Phase 4: Build ABox instances from processed tables → rdf/cta_data.ttl + .jsonld.

Canonical pattern:
  - TBox lives in ontology/; ABox is ALWAYS generated from data (never hand-typed).
  - Mint opaque IRIs under https://w3id.org/gulsayyar/cta/data/
  - Every Measurement gets prov:wasGeneratedBy + qudt:unit + PROV agents.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, PROV, RDF, RDFS, XSD

from utils import (
    CTA,
    CTA_DATA,
    ONTOLOGY_DIR,
    PROCESSED_DIR,
    RDF_DIR,
    hgnc_uri,
    iri,
    parse_filename,
)

CTA_ONT = Namespace(CTA + "ontology/")
UNIT = Namespace("http://qudt.org/vocab/unit/")
QK = Namespace("http://qudt.org/vocab/quantitykind/")
# Safe quantity kind IRIs (not all are in rdflib's built-in namespaces)
QK_AREA_FRACTION = URIRef("http://qudt.org/vocab/quantitykind/AreaFraction")
QK_FREQUENCY = URIRef("http://qudt.org/vocab/quantitykind/Frequency")
QK_TEMPERATURE = URIRef("http://qudt.org/vocab/quantitykind/Temperature")
QK_VELOCITY = URIRef("http://qudt.org/vocab/quantitykind/Velocity")
QK_LENGTH = URIRef("http://qudt.org/vocab/quantitykind/Length")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core/")
SCHEMA = Namespace("https://schema.org/")
NCBITAXON = URIRef("http://purl.obolibrary.org/obo/NCBITaxon_9606")
DUO_USER = URIRef("http://purl.obolibrary.org/obo/DUO_0000042")  # general research use

DIAG_CONCEPT = {
    "HealthyControl": CTA_ONT.HealthyControl,
    "PCD": CTA_ONT.PCD,
    "HallmarkPathognomonicDefect": CTA_ONT.HallmarkPathognomonicDefect,
    "NormalOrNearNormalUltrastructure": CTA_ONT.NormalOrNearNormalUltrastructure,
}

UNIT_MAP = {
    "pct": UNIT.PERCENT,
    "hz": UNIT.HZ,
    "um": UNIT.MicroM,
    "s": UNIT.SEC,
    "ums": UNIT["MicroM-PER-SEC"],
}


def load_processed():
    summary = pd.read_parquet(PROCESSED_DIR / "insert_summary.parquet")
    tracks = pd.read_parquet(PROCESSED_DIR / "track_summary.parquet")
    points = pd.read_parquet(PROCESSED_DIR / "track_points_rdf_sample.parquet")
    classification = pd.read_parquet(PROCESSED_DIR / "classification_stub.parquet")
    return summary, tracks, points, classification


def build_graph() -> Graph:
    g = Graph()
    g.bind("cta", CTA_ONT)
    g.bind("ctad", Namespace(CTA_DATA))
    g.bind("prov", PROV)
    g.bind("unit", UNIT)
    g.bind("dcterms", DCTERMS)
    g.bind("skos", SKOS)

    # Load TBox
    for ttl in ["cta.ttl", "schemes.ttl"]:
        g.parse(ONTOLOGY_DIR / ttl, format="turtle")

    summary, tracks, points, classification = load_processed()
    points_by_track = {uid: grp for uid, grp in points.groupby("track_uid")}
    class_map = classification.set_index("insert_id").to_dict("index")

    investigation = URIRef(CTA_DATA + "investigation/pcd_cta_demo")
    g.add((investigation, RDF.type, CTA_ONT.Investigation))
    g.add((investigation, DCTERMS.title, Literal("PCD Ciliary Transport Assay Investigation (FAIR demo)")))
    g.add((investigation, CTA_ONT.isSynthetic, Literal(True, datatype=XSD.boolean)))
    g.add((investigation, RDFS.comment, Literal(
        "Public GitHub package uses synthetic assay instances. Ontology TBox is real."
    )))

    assay_activity = URIRef(CTA_DATA + "activity/cta_analysis")
    g.add((assay_activity, RDF.type, PROV.Activity))
    g.add((assay_activity, PROV.wasAssociatedWith, CTA_ONT.imaris))
    g.add((assay_activity, PROV.wasAssociatedWith, CTA_ONT.ctaPipeline))
    g.add((assay_activity, PROV.wasAssociatedWith, CTA_ONT.microscope))
    g.add((assay_activity, PROV.wasAttributedTo, CTA_ONT.researcher))
    g.add((assay_activity, PROV.generatedAtTime, Literal(datetime.utcnow().isoformat(), datatype=XSD.dateTime)))

    donors_seen = {}

    for _, row in summary.iterrows():
        insert_id = row["insert_id"]
        donor_id = row["donor_id"]

        # Donor
        if donor_id not in donors_seen:
            donor_uri = iri("donor", donor_id)
            g.add((donor_uri, RDF.type, CTA_ONT.Donor))
            g.add((donor_uri, RDFS.label, Literal(donor_id)))
            g.add((donor_uri, SCHEMA.identifier, Literal(donor_id)))
            g.add((donor_uri, CTA_ONT.hasDiagnosticGroup, DIAG_CONCEPT.get(row["diagnostic_group"], CTA_ONT.PCD)))
            if "is_synthetic" in row.index and bool(row.get("is_synthetic", False)):
                g.add((donor_uri, CTA_ONT.isSynthetic, Literal(True, datatype=XSD.boolean)))
            g.add((donor_uri, CTA_ONT.hasDataUseRestriction, DUO_USER))
            # Species
            g.add((donor_uri, SCHEMA.taxonomicRange, NCBITAXON))

            if row["gene_symbols"] and str(row["gene_symbols"]) != "nan":
                for gene in str(row["gene_symbols"]).split("|"):
                    gene = gene.strip()
                    if not gene:
                        continue
                    var_uri = iri("variant", f"{donor_id}_{gene}")
                    gene_uri = URIRef(hgnc_uri(gene))
                    g.add((var_uri, RDF.type, CTA_ONT.GeneticVariant))
                    g.add((var_uri, RDFS.label, Literal(f"{donor_id} {gene} variant")))
                    g.add((var_uri, CTA_ONT.variantInGene, gene_uri))
                    g.add((gene_uri, RDF.type, CTA_ONT.Gene))
                    g.add((gene_uri, RDFS.label, Literal(gene)))
                    g.add((gene_uri, SCHEMA.sameAs, gene_uri))
                    g.add((donor_uri, CTA_ONT.carriesVariant, var_uri))
            donors_seen[donor_id] = donor_uri
        donor_uri = donors_seen[donor_id]

        # Insert
        ins_uri = iri("insert", insert_id)
        g.add((ins_uri, RDF.type, CTA_ONT.Insert))
        g.add((ins_uri, RDFS.label, Literal(insert_id)))
        g.add((ins_uri, CTA_ONT.hasDonor, donor_uri))
        g.add((ins_uri, PROV.wasGeneratedBy, assay_activity))
        if row["is_healthy"]:
            g.add((ins_uri, RDF.type, CTA_ONT.HealthyInsert))
            g.add((ins_uri, CTA_ONT.hasDiagnosticSubgroup, CTA_ONT.HealthyControl))
        else:
            g.add((ins_uri, RDF.type, CTA_ONT.PCDInsert))
            subgroup = DIAG_CONCEPT.get(row["diagnostic_subgroup"])
            if subgroup:
                g.add((ins_uri, CTA_ONT.hasDiagnosticSubgroup, subgroup))

        # Assay
        assay_uri = iri("assay", insert_id)
        g.add((assay_uri, RDF.type, CTA_ONT.CiliaryTransportAssay))
        g.add((assay_uri, RDFS.label, Literal(f"CTA {insert_id}")))
        g.add((ins_uri, CTA_ONT.hasAssay, assay_uri))
        g.add((assay_uri, CTA_ONT.hasInstrument, CTA_ONT.microscope))
        g.add((assay_uri, CTA_ONT.hasCondition, CTA_ONT.ConditionAir))
        if pd.notna(row.get("assay_date")) and row["assay_date"]:
            d = str(row["assay_date"]).replace("_", "-")
            g.add((assay_uri, CTA_ONT.hasDate, Literal(d, datatype=XSD.date)))

        # Measurements (priority + all summary numerics)
        meas_specs = [
            ("active_area_pct", CTA_ONT.ActiveAreaMeasurement, UNIT.PERCENT, QK_AREA_FRACTION, "Active Area (%)"),
            ("mean_cbf_g_wfa_hz", CTA_ONT.CBFMeasurement, UNIT.HZ, QK_FREQUENCY, "Mean CBF (G WFA)"),
            ("mean_cbf_wfa_hz", CTA_ONT.CBFMeasurement, UNIT.HZ, QK_FREQUENCY, "Mean CBF (WFA)"),
            ("frame_rate_hz", CTA_ONT.Measurement, UNIT.HZ, QK_FREQUENCY, "Frame Rate"),
            ("temperature_c", CTA_ONT.Measurement, URIRef("http://qudt.org/vocab/unit/DEG_C"), QK_TEMPERATURE, "Temperature"),
            ("mean_speed_ums", CTA_ONT.DerivedFeature, UNIT["MicroM-PER-SEC"], QK_VELOCITY, "Mean track speed"),
            ("net_displacement_um", CTA_ONT.DerivedFeature, UNIT.MicroM, QK_LENGTH, "Net displacement"),
        ]
        for field, rdf_class, unit, qk, label in meas_specs:
            val = row.get(field)
            if pd.isna(val):
                continue
            m_uri = iri("measurement", f"{insert_id}_{field}")
            g.add((m_uri, RDF.type, rdf_class))
            g.add((m_uri, RDFS.label, Literal(f"{label} for {insert_id}")))
            g.add((m_uri, CTA_ONT.hasValue, Literal(float(val), datatype=XSD.decimal)))
            g.add((m_uri, CTA_ONT.hasUnit, unit))
            g.add((m_uri, CTA_ONT.hasQuantityKind, qk))
            g.add((ins_uri, CTA_ONT.hasMeasurement, m_uri))
            g.add((m_uri, PROV.wasGeneratedBy, assay_activity))
            g.add((m_uri, PROV.wasAttributedTo, CTA_ONT.researcher))
            g.add((m_uri, PROV.wasAssociatedWith, CTA_ONT.imaris))

        # Classification
        if insert_id in class_map:
            c = class_map[insert_id]
            cl_uri = iri("classification", insert_id)
            pred = DIAG_CONCEPT.get(c["predicted_group"], CTA_ONT.PCD)
            g.add((cl_uri, RDF.type, CTA_ONT.ClassificationResult))
            g.add((cl_uri, CTA_ONT.predictedGroup, pred))
            g.add((cl_uri, CTA_ONT.probability, Literal(float(c["probability"]), datatype=XSD.decimal)))
            g.add((cl_uri, CTA_ONT.modelId, Literal(c["model_id"])))
            for i in range(1, 4):
                feat = c.get(f"top_xai_feature_{i}")
                if feat:
                    g.add((cl_uri, CTA_ONT.topXAIFeature, Literal(feat)))
            g.add((ins_uri, CTA_ONT.hasClassification, cl_uri))
            g.add((cl_uri, PROV.wasGeneratedBy, assay_activity))

    # Snapshot core ABox (inserts, donors, measurements) before bulk track triples
    core_graph = Graph()
    core_graph.parse(data=g.serialize(format="turtle"), format="turtle")

    # Tracks + representative points (full resolution in track_points.parquet)
    video_map: dict[tuple[str, str], URIRef] = {}
    for i, tr in tracks.iterrows():
        if i and i % 10000 == 0:
            print(f"  tracks: {i}/{len(tracks)}")
        insert_id = tr["insert_id"]
        assay_uri = iri("assay", insert_id)
        video_name = tr["video_name"]
        vkey = (insert_id, video_name)
        if vkey not in video_map:
            v_uri = iri("video", f"{insert_id}_{video_name}".replace(".", "_"))
            g.add((v_uri, RDF.type, CTA_ONT.Video))
            g.add((v_uri, RDFS.label, Literal(video_name)))
            g.add((assay_uri, CTA_ONT.producedVideo, v_uri))
            video_map[vkey] = v_uri
        v_uri = video_map[vkey]

        t_uri = iri("track", tr["track_uid"])
        g.add((t_uri, RDF.type, CTA_ONT.Track))
        g.add((t_uri, RDFS.label, Literal(tr["track_uid"])))
        g.add((v_uri, CTA_ONT.hasTrack, t_uri))
        g.add((t_uri, CTA_ONT.meanSpeed, Literal(float(tr["mean_speed_ums"]), datatype=XSD.decimal)))

        tp = points_by_track.get(tr["track_uid"])
        if tp is None:
            continue
        for _, pt in tp.iterrows():
            p_uri = iri("trackpoint", f"{tr['track_uid']}_{int(pt['t_index'])}")
            g.add((p_uri, RDF.type, CTA_ONT.TrackPoint))
            g.add((t_uri, CTA_ONT.hasTrackPoint, p_uri))
            g.add((p_uri, CTA_ONT.isTrackPointOf, t_uri))
            if pd.notna(pt.get("time_s")):
                g.add((p_uri, CTA_ONT.timeS, Literal(float(pt["time_s"]), datatype=XSD.decimal)))
            if pd.notna(pt.get("x_um")):
                g.add((p_uri, CTA_ONT.positionX, Literal(float(pt["x_um"]), datatype=XSD.decimal)))
            if pd.notna(pt.get("speed_ums")):
                g.add((p_uri, CTA_ONT.speed, Literal(float(pt["speed_ums"]), datatype=XSD.decimal)))

    return g, core_graph


def write_metadata(g: Graph) -> Graph:
    """Phase 7 partial: DCAT dataset metadata in rdf/metadata.ttl."""
    meta = Graph()
    meta.bind("dcat", DCAT)
    meta.bind("dcterms", DCTERMS)

    dataset = URIRef(CTA_DATA + "dataset/cta_kg")
    meta.add((dataset, RDF.type, DCAT.Dataset))
    meta.add((dataset, DCTERMS.title, Literal("PCD Ciliary Transport Assay Knowledge Graph")))
    meta.add((dataset, DCTERMS.creator, CTA_ONT.researcher))
    meta.add((dataset, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by/4.0/")))
    meta.add((dataset, DCTERMS.identifier, Literal("https://w3id.org/gulsayyar/cta/")))

    artifacts = [
        ("distribution/processed_summary", "data/processed/insert_summary.parquet", "application/parquet"),
        ("distribution/rdf_ttl", "rdf/cta_data.ttl", "text/turtle"),
        ("distribution/rdf_jsonld", "rdf/cta_data.jsonld", "application/ld+json"),
        ("distribution/ontology", "ontology/cta.ttl", "text/turtle"),
        ("distribution/code", "src/build_graph.py", "text/x-python"),
    ]
    for dist_id, path, fmt in artifacts:
        d = URIRef(CTA_DATA + dist_id)
        meta.add((d, RDF.type, DCAT.Distribution))
        meta.add((d, DCAT.downloadURL, Literal(path)))
        meta.add((d, DCAT.mediaType, Literal(fmt)))
        meta.add((dataset, DCAT.distribution, d))

    return meta


def main() -> None:
    RDF_DIR.mkdir(parents=True, exist_ok=True)
    g, g_core = build_graph()
    ttl_path = RDF_DIR / "cta_data.ttl"
    jsonld_path = RDF_DIR / "cta_data.jsonld"
    core_path = RDF_DIR / "cta_data_core.ttl"
    g.serialize(destination=str(ttl_path), format="turtle")
    g.serialize(destination=str(jsonld_path), format="json-ld")
    g_core.serialize(destination=str(core_path), format="turtle")
    print(f"ABox: {len(g)} triples -> {ttl_path}")
    print(f"Core ABox: {len(g_core)} triples -> {core_path}")

    meta = write_metadata(g)
    meta.serialize(destination=str(RDF_DIR / "metadata.ttl"), format="turtle")
    print(f"DCAT metadata -> {RDF_DIR / 'metadata.ttl'}")


if __name__ == "__main__":
    main()
