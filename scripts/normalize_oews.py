#!/usr/bin/env python3
import os, pandas as pd

RAW = "data/raw/oews_2024_05/msa_all.xlsx"
OUT = "data/processed/oews_2024_05/msa.parquet"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

if not os.path.exists(RAW):
    raise SystemExit(f"Missing input: {RAW}")

df = pd.read_excel(RAW, sheet_name=0, dtype=str)
keep = {
  "OCC_CODE":"SOC",
  "OCC_TITLE":"OCC_TITLE",
  "AREA":"AREA",
  "AREA_NAME":"AREA_NAME",
  "A_PCT10":"A_PCT10",
  "A_PCT25":"A_PCT25",
  "A_MEDIAN":"A_PCT50",
  "A_PCT75":"A_PCT75",
  "A_PCT90":"A_PCT90"
}
missing = [k for k in keep if k not in df.columns]
if missing:
    raise SystemExit(f"Missing expected columns: {missing}")

df = df.rename(columns=keep)[list(keep.values())].copy()
for c in ["A_PCT10","A_PCT25","A_PCT50","A_PCT75","A_PCT90"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df.to_parquet(OUT, index=False)
open("data/processed/oews_2024_05/README.md","w").write(
  "# OEWS May 2024 (processed)\ncolumns: SOC, OCC_TITLE, AREA, AREA_NAME, A_PCT10, A_PCT25, A_PCT50, A_PCT75, A_PCT90\n"
)
print("OK normalize_oews")
