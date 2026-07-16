#!/usr/bin/env python3
"""
Generate a FAIR-demo synthetic CTA cohort when raw txt/csv are unavailable.

IMPORTANT
---------
Original laboratory files were removed from this public package.
This script creates *realistic-shaped* synthetic Parquet tables that exercise
the ontology, SHACL shapes, and SPARQL competency questions.

Synthetic data are explicitly labelled (is_synthetic=True / model_id stub).
They must NOT be used for clinical conclusions.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from utils import PROCESSED_DIR

RNG = np.random.default_rng(42)

# Compact but query-complete demo cohort
COHORT = [
    # healthy controls
    ("W12", True, [], "HealthyControl"),
    ("W85", True, [], "HealthyControl"),
    ("M13", True, [], "HealthyControl"),
    ("M21", True, [], "HealthyControl"),
    ("M22", True, [], "HealthyControl"),
    # hallmark PCD
    ("OP-4772", False, ["DNAH11"], "HallmarkPathognomonicDefect"),
    ("OP-4193", False, ["DNAH11"], "HallmarkPathognomonicDefect"),
    ("OP-5540", False, ["DNAH11"], "HallmarkPathognomonicDefect"),
    ("OP-5671", False, ["DNAH11"], "HallmarkPathognomonicDefect"),
    ("OP-122", False, ["CCDC39"], "HallmarkPathognomonicDefect"),
    ("OP-335", False, ["DNAH5"], "HallmarkPathognomonicDefect"),
    ("OP-3499", False, ["DNAI1"], "HallmarkPathognomonicDefect"),
    # near-normal ultrastructure PCD
    ("OP-4891", False, ["AK8"], "NormalOrNearNormalUltrastructure"),
    ("OP-4", False, ["CCDC103"], "NormalOrNearNormalUltrastructure"),
    ("SP-32", False, ["SPEF2"], "NormalOrNearNormalUltrastructure"),
]


def _cbf_for(healthy: bool, subgroup: str) -> float:
    if healthy:
        return float(RNG.normal(12.5, 1.5))
    if subgroup == "HallmarkPathognomonicDefect":
        return float(max(0.0, RNG.normal(6.0, 2.5)))
    return float(RNG.normal(9.5, 2.0))


def _active_area_for(healthy: bool, subgroup: str) -> float:
    if healthy:
        return float(np.clip(RNG.normal(55.0, 8.0), 5, 95))
    if subgroup == "HallmarkPathognomonicDefect":
        return float(np.clip(RNG.normal(5.0, 3.0), 0.01, 25))
    return float(np.clip(RNG.normal(20.0, 8.0), 0.5, 60))


def generate() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    summaries = []
    tracks = []
    points = []
    classifications = []

    insert_n = 0
    for donor_id, is_healthy, genes, subgroup in COHORT:
        # Force Ins2 for OP-4772 so published SPARQL CQ2 keeps working
        insert_nums = [2] if donor_id == "OP-4772" else ([1, 2] if is_healthy else [1])
        for ins in insert_nums:
            insert_n += 1
            insert_id = f"{donor_id}_Ins{ins}"
            active = _active_area_for(is_healthy, subgroup)
            cbf = _cbf_for(is_healthy, subgroup)
            mean_speed = float(RNG.normal(8.0 if is_healthy else 3.5, 1.2))
            if insert_id == "OP-4772_Ins2":
                # Ensure CQ2 has fast tracks
                mean_speed = 6.5
                active = 0.01
                cbf = 0.0
            disp = float(max(0.1, RNG.normal(25.0 if is_healthy else 8.0, 4.0)))
            duration = float(RNG.uniform(0.8, 2.5))

            summaries.append({
                "donor_id": donor_id,
                "insert_id": insert_id,
                "insert_label": f"Ins{ins}",
                "group": genes[0] if genes else "Healthy",
                "gene_symbols": "|".join(genes),
                "is_healthy": is_healthy,
                "diagnostic_group": "HealthyControl" if is_healthy else "PCD",
                "diagnostic_subgroup": subgroup,
                "assay_date": "2024_06_15",
                "source_file": f"SYNTH_{insert_id}.csv",
                "n_csv_rows": 5,
                "n_valid_rows": 4,
                "active_area_pct": active,
                "mean_cbf_g_wfa_hz": cbf,
                "mean_cbf_wfa_hz": cbf * 0.98,
                "frame_rate_hz": 200.0,
                "temperature_c": 37.0,
                "mean_speed_ums": mean_speed,
                "net_displacement_um": disp,
                "duration_s": duration,
                "is_synthetic": True,
            })

            # classification stub (explicitly synthetic)
            if is_healthy:
                pred, prob = "HealthyControl", 0.12
                feats = ["mean_speed_ums", "active_area_pct", "mean_cbf_g_wfa_hz"]
            elif subgroup == "HallmarkPathognomonicDefect":
                pred, prob = "HallmarkPathognomonicDefect", 0.91
                feats = ["net_displacement_um", "mean_speed_ums", "active_area_pct"]
            else:
                pred, prob = "NormalOrNearNormalUltrastructure", 0.68
                feats = ["mean_cbf_g_wfa_hz", "active_area_pct", "duration_s"]
            classifications.append({
                "insert_id": insert_id,
                "predicted_group": pred,
                "probability": prob,
                "model_id": "cta_rf_v1_stub",
                "top_xai_feature_1": feats[0],
                "top_xai_feature_2": feats[1],
                "top_xai_feature_3": feats[2],
            })

            n_tracks = 12 if insert_id == "OP-4772_Ins2" else 6
            for t in range(n_tracks):
                track_uid = f"{insert_id}_t{t}_{t}"
                # Bias OP-4772_Ins2 toward many fast tracks (>5 µm/s) for CQ2
                if insert_id == "OP-4772_Ins2":
                    t_speed = float(RNG.uniform(5.2, 10.8))
                else:
                    t_speed = float(max(0.2, RNG.normal(mean_speed, 1.5)))
                tracks.append({
                    "track_uid": track_uid,
                    "donor_id": donor_id,
                    "insert_id": insert_id,
                    "video_name": f"{insert_id}_vid1.avi",
                    "tree_id": t,
                    "track_id": t,
                    "n_points": 5,
                    "duration_s": duration,
                    "mean_speed_ums": t_speed,
                    "max_speed_ums": t_speed * 1.3,
                    "net_displacement_um": disp * RNG.uniform(0.5, 1.2),
                    "path_length_um": disp * RNG.uniform(1.2, 2.5),
                    "is_synthetic": True,
                })
                for k in range(5):
                    ang = 2 * math.pi * k / 5
                    points.append({
                        "donor_id": donor_id,
                        "insert_id": insert_id,
                        "video_name": f"{insert_id}_vid1.avi",
                        "track_uid": track_uid,
                        "tree_id": t,
                        "track_id": t,
                        "t_index": k,
                        "time_s": k * 0.05,
                        "x_um": 10.0 + t_speed * k * 0.05 * math.cos(ang),
                        "y_um": 20.0 + t_speed * k * 0.05 * math.sin(ang),
                        "z_um": 0.0,
                        "speed_ums": t_speed,
                        "seg_length_um": t_speed * 0.05,
                        "spot_type": "Spot",
                        "source_file": f"SYNTH_{insert_id}.txt",
                        "is_synthetic": True,
                    })

    summary_df = pd.DataFrame(summaries)
    track_df = pd.DataFrame(tracks)
    points_df = pd.DataFrame(points)
    class_df = pd.DataFrame(classifications)

    points_df.to_parquet(PROCESSED_DIR / "track_points.parquet", index=False)
    points_df.to_parquet(PROCESSED_DIR / "track_points_rdf_sample.parquet", index=False)
    track_df.to_parquet(PROCESSED_DIR / "track_summary.parquet", index=False)
    summary_df.to_parquet(PROCESSED_DIR / "insert_summary.parquet", index=False)
    summary_df.to_csv(PROCESSED_DIR / "insert_summary.csv", index=False)
    class_df.to_parquet(PROCESSED_DIR / "classification_stub.parquet", index=False)

    meta = PROCESSED_DIR / "SYNTHETIC_DATA_NOTICE.md"
    meta.write_text(
        "# Synthetic data notice\n\n"
        "These Parquet/CSV files were generated by `src/generate_synthetic_data.py` "
        "because original laboratory `txt/` and `csv/` inputs are not redistributed "
        "in the public GitHub package.\n\n"
        "- Seed: 42\n"
        f"- Inserts: {len(summary_df)}\n"
        f"- Tracks: {len(track_df)}\n"
        f"- Track points: {len(points_df)}\n"
        "- Classification / XAI rows are stubs (`cta_rf_v1_stub`).\n"
        "- Not for clinical use.\n",
        encoding="utf-8",
    )

    print(f"Synthetic cohort written to {PROCESSED_DIR}")
    print(f"  inserts={len(summary_df)} tracks={len(track_df)} points={len(points_df)}")


if __name__ == "__main__":
    generate()
