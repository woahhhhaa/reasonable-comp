import os
from functools import lru_cache
from typing import Literal

import pandas as pd


OEWS_VINTAGE_TAG = "oews_2024_05"


def _processed_path(name: Literal["msa", "state"]) -> str:
    base = os.path.join("data", "processed", OEWS_VINTAGE_TAG)
    return os.path.join(base, f"{name}.parquet")


@lru_cache(maxsize=1)
def get_oews_msa() -> pd.DataFrame:
    path = _processed_path("msa")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing OEWS MSA parquet at {path}")
    df = pd.read_parquet(path)
    # Ensure expected columns and types
    expected = [
        "SOC",
        "OCC_TITLE",
        "AREA",
        "AREA_NAME",
        "A_PCT10",
        "A_PCT25",
        "A_PCT50",
        "A_PCT75",
        "A_PCT90",
    ]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"MSA parquet missing columns: {missing}")
    return df


@lru_cache(maxsize=1)
def get_oews_state() -> pd.DataFrame:
    path = _processed_path("state")
    if not os.path.exists(path):
        # Allow Day-4 to proceed by deriving a state-level file if missing
        # The normalize script should have produced this; this is a soft fallback
        df_state = _derive_state_from_msa()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df_state.to_parquet(path, index=False)
        return df_state
    df = pd.read_parquet(path)
    expected = [
        "SOC",
        "OCC_TITLE",
        "AREA",
        "AREA_NAME",
        "A_PCT10",
        "A_PCT25",
        "A_PCT50",
        "A_PCT75",
        "A_PCT90",
    ]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"State parquet missing columns: {missing}")
    return df


def _derive_state_from_msa() -> pd.DataFrame:
    df = get_oews_msa().copy()
    # Extract two-letter state code from AREA_NAME suffix (e.g., "Austin-Round Rock-Georgetown, TX")
    df["STATE"] = df["AREA_NAME"].str.extract(r",\s*([A-Z]{2})$", expand=False)
    # For safety, drop rows without a parsable state code
    df = df[df["STATE"].notna()].copy()
    # Aggregate by state + SOC using median to avoid outliers
    agg_cols = ["A_PCT10", "A_PCT25", "A_PCT50", "A_PCT75", "A_PCT90"]
    grouped = (
        df.groupby(["STATE", "SOC", "OCC_TITLE"], as_index=False)[agg_cols]
        .median()
        .rename(columns={"STATE": "AREA"})
    )
    grouped["AREA_NAME"] = grouped["AREA"]
    # Reorder columns
    cols = [
        "SOC",
        "OCC_TITLE",
        "AREA",
        "AREA_NAME",
        "A_PCT10",
        "A_PCT25",
        "A_PCT50",
        "A_PCT75",
        "A_PCT90",
    ]
    return grouped[cols].copy()


