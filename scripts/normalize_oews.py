#!/usr/bin/env python3
import os, pandas as pd

RAW = "data/raw/oews_2024_05/msa_all.xlsx"
OUT = "data/processed/oews_2024_05/msa.parquet"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

if not os.path.exists(RAW):
    raise SystemExit(f"Missing input: {RAW}")

df = pd.read_excel(RAW, sheet_name=0, dtype=str)

# Some BLS workbooks use AREA_TITLE instead of AREA_NAME – accept either
source_to_target = {
  "OCC_CODE":"SOC",
  "OCC_TITLE":"OCC_TITLE",
  "AREA":"AREA",
  "AREA_NAME":"AREA_NAME",
  "AREA_TITLE":"AREA_NAME",
  "A_PCT10":"A_PCT10",
  "A_PCT25":"A_PCT25",
  "A_MEDIAN":"A_PCT50",
  "A_PCT75":"A_PCT75",
  "A_PCT90":"A_PCT90"
}

# Build the minimal mapping present in the file, preferring AREA_NAME over AREA_TITLE
present_mapping = {}
for src_col, tgt_col in source_to_target.items():
    if src_col in df.columns:
        # If we already mapped an alternative to the same target, prefer AREA_NAME
        if tgt_col in present_mapping.values() and src_col == "AREA_TITLE":
            continue
        present_mapping[src_col] = tgt_col

required_targets = {"SOC","OCC_TITLE","AREA","AREA_NAME","A_PCT10","A_PCT25","A_PCT50","A_PCT75","A_PCT90"}
have_targets = set(present_mapping.values())
if not required_targets.issubset(have_targets):
    missing = sorted(required_targets - have_targets)
    raise SystemExit(f"Missing expected columns: {missing}")

df = df.rename(columns=present_mapping)[list(required_targets)].copy()
for c in ["A_PCT10","A_PCT25","A_PCT50","A_PCT75","A_PCT90"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df.to_parquet(OUT, index=False)
open("data/processed/oews_2024_05/README.md","w").write(
  "# OEWS May 2024 (processed)\ncolumns: SOC, OCC_TITLE, AREA, AREA_NAME, A_PCT10, A_PCT25, A_PCT50, A_PCT75, A_PCT90\n"
)
print("OK normalize_oews")
