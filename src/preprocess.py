#!/usr/bin/env python3
"""
Phase 1: Clean and preprocess raw CTA data → data/processed/.

Canonical pattern: separate *tidy* (long track points) from *summary* (one row
per insert) tables; snake_case columns; explicit units in data dictionary.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from utils import (
    CSV_DIR,
    DOCS_DIR,
    PROCESSED_DIR,
    TXT_DIR,
    detect_sep_from_text,
    normalise_basename,
    parse_filename,
    parse_time_seconds,
    read_text_auto,
)

# --- TXT column standardisation ---
TXT_RENAME = {
    "Name": "video_name",
    "Type": "spot_type",
    "Tree ID": "tree_id",
    "ID": "track_id",
    "ND.M": "nd_m",
    "ND.T": "t_index",
    "Time [s]": "time_raw",
    "PositionX [µm]": "x_um",
    "PositionX [um]": "x_um",
    "PositionY [µm]": "y_um",
    "PositionY [um]": "y_um",
    "PositionZ [µm]": "z_um",
    "PositionZ [um]": "z_um",
    "Seg.Length [µm]": "seg_length_um",
    "Seg.Length [um]": "seg_length_um",
    "Speed [µm/s]": "speed_ums",
    "Speed [um/s]": "speed_ums",
    "RefLineSpeed [µm/s]": "ref_line_speed_ums",
    "Area [µm²]": "area_um2",
    "Area [um^2]": "area_um2",
    "Volume [µm³]": "volume_um3",
    "EqDiameter [µm]": "eq_diameter_um",
    "Perimeter [µm]": "perimeter_um",
    "Surface [µm²]": "surface_um2",
    "Width [µm]": "width_um",
    "MaxFeret [µm]": "max_feret_um",
    "MinFeret [µm]": "min_feret_um",
    "Circularity": "circularity",
    "Elongation": "elongation",
    "MeanIntensity": "mean_intensity",
    "MinIntensity": "min_intensity",
    "MaxIntensity": "max_intensity",
    "SumIntensity": "sum_intensity",
    "StDev": "stdev",
}

CSV_RENAME = {
    "Sample Name": "sample_name",
    "Plate No.": "plate_no",
    "Date and Time": "datetime",
    "Elapsed Time": "elapsed_time",
    "Frame Rate": "frame_rate_hz",
    "Frequency Range": "frequency_range",
    "Magnification": "magnification",
    "Temperature (°C)": "temperature_c",
    "Comments": "comments",
    "Active Area (%)": "active_area_pct",
    "Mean CBF (WFA)": "mean_cbf_wfa_hz",
    "St. Err (WFA)": "st_err_wfa_hz",
    "# of Pts. (WFA)": "n_pts_wfa",
    "Mean CBF (G WFA)": "mean_cbf_g_wfa_hz",
    "St. Dev (G WFA)": "st_dev_g_wfa_hz",
    "# of Pts. (G WFA)": "n_pts_g_wfa",
    "Mean CBF (ROIs)": "mean_cbf_rois_hz",
    "St. Err (ROIs)": "st_err_rois_hz",
    "# of Pts. (ROIs)": "n_pts_rois",
    "CBF (ROIs)": "cbf_rois",
}


def detect_sep(path: Path) -> str:
    line = read_text_auto(path).splitlines()[0]
    return detect_sep_from_text(line)


def clean_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.replace(["N/A", "-", ""], pd.NA), errors="coerce")


def load_txt(path: Path, meta) -> pd.DataFrame:
    import io
    sep = detect_sep(path)
    df = pd.read_csv(io.StringIO(read_text_auto(path)), sep=sep, low_memory=False)
    df = df.rename(columns={k: v for k, v in TXT_RENAME.items() if k in df.columns})
    df = df.replace("N/A", pd.NA)

    df["time_s"] = df["time_raw"].apply(parse_time_seconds) if "time_raw" in df else df.get("t_index")
    for col in df.columns:
        if col not in ("video_name", "spot_type", "time_raw"):
            if df[col].dtype == object:
                df[col] = clean_numeric(df[col])

    df["donor_id"] = meta.donor_id
    df["insert_label"] = meta.insert_label
    df["insert_id"] = meta.insert_id
    df["source_file"] = path.name
    df["track_uid"] = (
        meta.insert_id + "_t" + df["tree_id"].astype(str) + "_" + df["track_id"].astype(str)
    )
    return df


def aggregate_tracks(points: pd.DataFrame) -> pd.DataFrame:
    """Per-track derived features (canonical ML-ready aggregates)."""
    rows = []
    for uid, g in points.groupby("track_uid"):
        g = g.sort_values("t_index")
        x0, y0 = g["x_um"].iloc[0], g["y_um"].iloc[0]
        x1, y1 = g["x_um"].iloc[-1], g["y_um"].iloc[-1]
        disp = float(np.hypot(x1 - x0, y1 - y0)) if pd.notna(x1) else np.nan
        rows.append({
            "track_uid": uid,
            "donor_id": g["donor_id"].iloc[0],
            "insert_id": g["insert_id"].iloc[0],
            "video_name": g["video_name"].iloc[0],
            "tree_id": int(g["tree_id"].iloc[0]),
            "track_id": int(g["track_id"].iloc[0]),
            "n_points": len(g),
            "duration_s": float(g["time_s"].max() - g["time_s"].min()) if g["time_s"].notna().any() else np.nan,
            "mean_speed_ums": float(g["speed_ums"].mean()),
            "max_speed_ums": float(g["speed_ums"].max()),
            "net_displacement_um": disp,
            "path_length_um": float(g["seg_length_um"].sum()) if "seg_length_um" in g else np.nan,
        })
    return pd.DataFrame(rows)


def aggregate_csv(path: Path, meta) -> dict:
    df = pd.read_csv(path)
    df = df.rename(columns={k: v for k, v in CSV_RENAME.items() if k in df.columns})
    for col in df.columns:
        if col not in ("sample_name", "datetime", "elapsed_time", "frequency_range", "magnification", "comments", "cbf_rois"):
            df[col] = clean_numeric(df[col])

    # Prefer rows with measurable cilia (Active Area > 0)
    valid = df[df["active_area_pct"].fillna(0) > 0] if "active_area_pct" in df else df
    src = valid if len(valid) > 0 else df
    row = src.mean(numeric_only=True).to_dict()
    row.update({
        "donor_id": meta.donor_id,
        "insert_id": meta.insert_id,
        "insert_label": meta.insert_label,
        "group": meta.group,
        "gene_symbols": "|".join(meta.gene_symbols),
        "is_healthy": meta.is_healthy,
        "diagnostic_group": meta.diagnostic_group,
        "diagnostic_subgroup": meta.diagnostic_subgroup,
        "assay_date": meta.assay_date,
        "source_file": path.name,
        "n_csv_rows": len(df),
        "n_valid_rows": len(valid),
    })
    return row


def stub_classification(summary: pd.DataFrame) -> pd.DataFrame:
    """
    Synthetic classification for graph/XAI demo — raw data has no ML output.

    Pattern: PCD hallmark genes → high PCD probability; healthy → low.
    """
    records = []
    for _, r in summary.iterrows():
        if r["is_healthy"]:
            pred, prob = "HealthyControl", 0.12
            top_features = ["mean_speed_ums", "active_area_pct", "mean_cbf_g_wfa_hz"]
        elif r["diagnostic_subgroup"] == "HallmarkPathognomonicDefect":
            pred, prob = "HallmarkPathognomonicDefect", 0.91
            top_features = ["net_displacement_um", "mean_speed_ums", "active_area_pct"]
        else:
            pred, prob = "NormalOrNearNormalUltrastructure", 0.68
            top_features = ["mean_cbf_g_wfa_hz", "active_area_pct", "duration_s"]
        records.append({
            "insert_id": r["insert_id"],
            "predicted_group": pred,
            "probability": prob,
            "model_id": "cta_rf_v1_stub",
            "top_xai_feature_1": top_features[0],
            "top_xai_feature_2": top_features[1],
            "top_xai_feature_3": top_features[2],
        })
    return pd.DataFrame(records)


def write_data_dictionary() -> None:
    """Emit docs/data_dictionary.md — one row per processed field."""
    lines = [
        "# Data Dictionary",
        "",
        "Processed tables in `data/processed/`. Units follow QUDT alignment in ontology.",
        "",
        "## track_points.parquet",
        "",
        "| Field | Meaning | Unit | Dtype |",
        "|-------|---------|------|-------|",
        "| donor_id | Pseudonymous donor (W<n>, OP-<n>) | — | string |",
        "| insert_id | Donor + insert (e.g. OP-4772_Ins2) | — | string |",
        "| video_name | Source microscopy video | — | string |",
        "| track_uid | Stable track identifier | — | string |",
        "| tree_id | Imaris tree id | — | int |",
        "| track_id | Imaris track id | — | int |",
        "| t_index | Time index (ND.T) | — | int |",
        "| time_s | Elapsed time | s | float |",
        "| x_um | X position | µm | float |",
        "| y_um | Y position | µm | float |",
        "| z_um | Z position (0 in 2D) | µm | float |",
        "| speed_ums | Instantaneous speed | µm/s | float |",
        "| seg_length_um | Segment length | µm | float |",
        "| area_um2 | Spot area | µm² | float |",
        "",
        "## insert_summary.parquet (priority measurements **bold**)",
        "",
        "| Field | Meaning | Unit | Dtype |",
        "|-------|---------|------|-------|",
        "| insert_id | Insert identifier | — | string |",
        "| donor_id | Pseudonymous donor | — | string |",
        "| **active_area_pct** | **Ciliated/active area fraction** | **%** | float |",
        "| **mean_cbf_g_wfa_hz** | **Mean ciliary beat frequency (Gaussian WFA)** | **Hz** | float |",
        "| mean_cbf_wfa_hz | Mean CBF (WFA) | Hz | float |",
        "| frame_rate_hz | Imaging frame rate | Hz | float |",
        "| temperature_c | Acquisition temperature | °C | float |",
        "| diagnostic_group | HealthyControl or PCD | — | string |",
        "| diagnostic_subgroup | Ultrastructure class | — | string |",
        "| gene_symbols | Pipe-separated HGNC symbols | — | string |",
        "",
        "## track_summary.parquet",
        "",
        "| Field | Meaning | Unit | Dtype |",
        "|-------|---------|------|-------|",
        "| track_uid | Track identifier | — | string |",
        "| mean_speed_ums | Mean speed over track | µm/s | float |",
        "| net_displacement_um | Euclidean start–end distance | µm | float |",
        "| duration_s | Track duration | s | float |",
        "| n_points | Number of track points | — | int |",
        "",
        "## classification_stub.parquet",
        "",
        "| Field | Meaning | Unit | Dtype |",
        "|-------|---------|------|-------|",
        "| predicted_group | ML-predicted class | — | string |",
        "| probability | Prediction probability | — | float |",
        "| model_id | Model identifier | — | string |",
        "| top_xai_feature_* | Top explainability features (stub) | — | string |",
    ]
    (DOCS_DIR / "data_dictionary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    txt_files = sorted(TXT_DIR.glob("*.txt")) if TXT_DIR.exists() else []
    csv_map = {normalise_basename(p.stem): p for p in CSV_DIR.glob("*.csv")} if CSV_DIR.exists() else {}

    # Public GitHub package ships without raw laboratory txt/csv.
    if not txt_files:
        summary = PROCESSED_DIR / "insert_summary.parquet"
        if not summary.exists():
            print("No raw txt/ found — generating local synthetic demo cohort...")
            from generate_synthetic_data import generate
            generate()
        else:
            print("Using existing local processed tables (not in git).")
        write_data_dictionary()
        return

    all_points = []
    summaries = []

    for txt_path in txt_files:
        meta = parse_filename(txt_path.stem)
        pts = load_txt(txt_path, meta)
        all_points.append(pts)

        norm = normalise_basename(txt_path.stem)
        csv_path = csv_map.get(norm)
        if csv_path:
            summaries.append(aggregate_csv(csv_path, meta))

    points_df = pd.concat(all_points, ignore_index=True)
    track_df = aggregate_tracks(points_df)
    summary_df = pd.DataFrame(summaries)

    # Merge track-level aggregates into summary for XAI features
    track_agg = track_df.groupby("insert_id").agg(
        mean_speed_ums=("mean_speed_ums", "mean"),
        net_displacement_um=("net_displacement_um", "mean"),
        duration_s=("duration_s", "mean"),
    ).reset_index()
    summary_df = summary_df.merge(track_agg, on="insert_id", how="left")

    class_df = stub_classification(summary_df)

    # Drop raw time column (mixed types); time_s is canonical
    if "time_raw" in points_df.columns:
        points_df = points_df.drop(columns=["time_raw"])

    points_df.to_parquet(PROCESSED_DIR / "track_points.parquet", index=False)

    # RDF sample: up to 5 evenly-spaced points per track (canonical full data stays above)
    rdf_pts = []
    for uid, grp in points_df.groupby("track_uid"):
        grp = grp.sort_values("t_index")
        if len(grp) > 5:
            idx = np.linspace(0, len(grp) - 1, 5, dtype=int)
            grp = grp.iloc[idx]
        rdf_pts.append(grp)
    rdf_points_df = pd.concat(rdf_pts, ignore_index=True)
    rdf_points_df.to_parquet(PROCESSED_DIR / "track_points_rdf_sample.parquet", index=False)
    track_df.to_parquet(PROCESSED_DIR / "track_summary.parquet", index=False)
    summary_df.to_parquet(PROCESSED_DIR / "insert_summary.parquet", index=False)
    class_df.to_parquet(PROCESSED_DIR / "classification_stub.parquet", index=False)

    # Also emit CSV for human inspection
    summary_df.to_csv(PROCESSED_DIR / "insert_summary.csv", index=False)

    write_data_dictionary()
    print(f"Processed {len(txt_files)} inserts")
    print(f"  track_points: {len(points_df):,} rows")
    print(f"  track_summary: {len(track_df):,} tracks")
    print(f"  insert_summary: {len(summary_df)} rows")


if __name__ == "__main__":
    main()
