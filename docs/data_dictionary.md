# Data Dictionary

Processed tables in `data/processed/`. Units follow QUDT alignment in ontology.

## track_points.parquet

| Field | Meaning | Unit | Dtype |
|-------|---------|------|-------|
| donor_id | Pseudonymous donor (W<n>, OP-<n>) | — | string |
| insert_id | Donor + insert (e.g. OP-4772_Ins2) | — | string |
| video_name | Source microscopy video | — | string |
| track_uid | Stable track identifier | — | string |
| tree_id | Imaris tree id | — | int |
| track_id | Imaris track id | — | int |
| t_index | Time index (ND.T) | — | int |
| time_s | Elapsed time | s | float |
| x_um | X position | µm | float |
| y_um | Y position | µm | float |
| z_um | Z position (0 in 2D) | µm | float |
| speed_ums | Instantaneous speed | µm/s | float |
| seg_length_um | Segment length | µm | float |
| area_um2 | Spot area | µm² | float |

## insert_summary.parquet (priority measurements **bold**)

| Field | Meaning | Unit | Dtype |
|-------|---------|------|-------|
| insert_id | Insert identifier | — | string |
| donor_id | Pseudonymous donor | — | string |
| **active_area_pct** | **Ciliated/active area fraction** | **%** | float |
| **mean_cbf_g_wfa_hz** | **Mean ciliary beat frequency (Gaussian WFA)** | **Hz** | float |
| mean_cbf_wfa_hz | Mean CBF (WFA) | Hz | float |
| frame_rate_hz | Imaging frame rate | Hz | float |
| temperature_c | Acquisition temperature | °C | float |
| diagnostic_group | HealthyControl or PCD | — | string |
| diagnostic_subgroup | Ultrastructure class | — | string |
| gene_symbols | Pipe-separated HGNC symbols | — | string |

## track_summary.parquet

| Field | Meaning | Unit | Dtype |
|-------|---------|------|-------|
| track_uid | Track identifier | — | string |
| mean_speed_ums | Mean speed over track | µm/s | float |
| net_displacement_um | Euclidean start–end distance | µm | float |
| duration_s | Track duration | s | float |
| n_points | Number of track points | — | int |

## classification_stub.parquet

| Field | Meaning | Unit | Dtype |
|-------|---------|------|-------|
| predicted_group | ML-predicted class | — | string |
| probability | Prediction probability | — | float |
| model_id | Model identifier | — | string |
| top_xai_feature_* | Top explainability features (stub) | — | string |