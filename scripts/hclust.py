#!/usr/bin/env python3
"""
Hierarchical clustering and dendrogram generation for tab-separated input.
Usage:
    python scripts/hclust.py --input 給.csv --sample 500 --png outputs/dendrogram.png --html outputs/dendrogram.html
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.cluster import hierarchy
from sklearn.preprocessing import StandardScaler
import plotly.figure_factory as ff


TEXT_COLS = ["NP2", "VP"]
CATEGORY_COLS = ["RELATION"]
NUMERIC_COLS = [
    "Freq",
    "FREQOFSLOT1",
    "FREQOFSLOT2",
    "LLR",
    "LOGODDSRATIO",
    "PMI",
    "DELTAP1TO2",
    "DELTAP2TO1",
    "KLD1TO2",
    "KLD2TO1",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hierarchical clustering with dendrogram outputs.")
    parser.add_argument("--input", default="給.csv", help="Input TSV/CSV file path (default: 給.csv)")
    parser.add_argument("--sample", type=int, default=500, help="Number of rows to keep after sorting (default: 500)")
    parser.add_argument("--png", default="outputs/dendrogram.png", help="Path to save static dendrogram PNG")
    parser.add_argument("--html", default="outputs/dendrogram.html", help="Path to save interactive dendrogram HTML")
    parser.add_argument("--max-leaves", type=int, default=100, help="Max leaves shown in static dendrogram (0 to show all)")
    parser.add_argument("--method", default="ward", choices=["ward", "single", "complete", "average"], help="Linkage method (default: ward)")
    parser.add_argument("--metric", default="euclidean", help="Distance metric (default: euclidean; ward requires euclidean)")
    return parser.parse_args()


def load_data(path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, sep="\t", encoding="utf-8")
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Failed to read {path}: {exc}", file=sys.stderr)
        sys.exit(1)
    return df


def prepare_dataframe(df: pd.DataFrame, sample_size: int) -> tuple[pd.DataFrame, List[str]]:
    missing_cols = [c for c in TEXT_COLS + NUMERIC_COLS if c not in df.columns]
    if missing_cols:
        print(f"Missing required columns: {missing_cols}", file=sys.stderr)
        sys.exit(1)

    # Build labels before filtering to keep text context aligned.
    labels = (df["NP2"].fillna("") + "-" + df["VP"].fillna("")).astype(str)
    df = df.assign(_label=labels)

    # Sort by priority and sample.
    df = df.sort_values(by=["Freq", "LLR"], ascending=False)
    if sample_size > 0:
        df = df.head(sample_size)

    # Keep numeric features and coerce to float, replacing inf/-inf.
    numeric = df[NUMERIC_COLS].apply(pd.to_numeric, errors="coerce")
    numeric = numeric.replace([np.inf, -np.inf], np.nan)
    before_drop = len(numeric)
    mask_valid = numeric.notna().all(axis=1)
    numeric = numeric[mask_valid]
    df = df.loc[mask_valid].copy()
    after_drop = len(numeric)

    if after_drop == 0:
        print("No rows left after dropping rows with non-numeric values", file=sys.stderr)
        sys.exit(1)

    if before_drop != after_drop:
        print(f"Dropped {before_drop - after_drop} rows due to NaNs in numeric columns", file=sys.stderr)

    return df, df["_label"].tolist()


def scale_features(numeric_df: pd.DataFrame) -> np.ndarray:
    scaler = StandardScaler()
    return scaler.fit_transform(numeric_df.values)


def plot_static(linkage_matrix: np.ndarray, labels: List[str], output_path: Path, max_leaves: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(18, 9))

    kwargs = {
        "labels": labels,
        "leaf_rotation": 90,
        "leaf_font_size": 6,
        "color_threshold": None,
    }
    if max_leaves > 0:
        kwargs.update({"truncate_mode": "lastp", "p": max_leaves})

    hierarchy.dendrogram(linkage_matrix, **kwargs)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_interactive(data_matrix: np.ndarray, labels: List[str], output_path: Path, method: str, metric: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig = ff.create_dendrogram(data_matrix, labels=labels, linkagefun=lambda x: hierarchy.linkage(x, method=method, metric=metric))
    fig.update_layout(width=1400, height=900)
    fig.write_html(output_path)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    df_raw = load_data(input_path)
    df_filtered, labels = prepare_dataframe(df_raw, args.sample)

    numeric_df = df_filtered[NUMERIC_COLS]
    features = scale_features(numeric_df)

    linkage_matrix = hierarchy.linkage(features, method=args.method, metric=args.metric)

    plot_static(linkage_matrix, labels, Path(args.png), args.max_leaves)
    plot_interactive(features, labels, Path(args.html), args.method, args.metric)

    print(f"Rows used: {len(df_filtered)}")
    print(f"PNG saved to: {Path(args.png).resolve()}")
    print(f"HTML saved to: {Path(args.html).resolve()}")


if __name__ == "__main__":
    main()
