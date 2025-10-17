import pandas as pd, os, json

def test_oews_monotonic():
    pq = "data/processed/oews_2024_05/msa.parquet"
    assert os.path.exists(pq), "Processed OEWS parquet missing"
    df = pd.read_parquet(pq)
    cols = ["A_PCT10","A_PCT25","A_PCT50","A_PCT75","A_PCT90"]
    m = (df[cols].notna().all(axis=1)) & (df["SOC"].notna()) & (df["AREA"].notna())
    sub = df.loc[m, cols]
    ok = ((sub["A_PCT10"] <= sub["A_PCT25"]) &
          (sub["A_PCT25"] <= sub["A_PCT50"]) &
          (sub["A_PCT50"] <= sub["A_PCT75"]) &
          (sub["A_PCT75"] <= sub["A_PCT90"]))
    frac = ok.mean()
    assert frac >= 0.995, f"Monotonic percentile rows below threshold: {frac:.4f}"

def test_eci_version_tag_present():
    base = "data/raw"
    tags = [d for d in os.listdir(base) if d.startswith("eci_")]
    assert tags, "No ECI version folder found"
    ver = os.path.join(base, tags[0], "VERSION")
    assert os.path.exists(ver), "ECI VERSION file missing"
    assert open(ver).read().strip().startswith("eci_")
