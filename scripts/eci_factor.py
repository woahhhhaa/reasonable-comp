#!/usr/bin/env python3
import json, sys

# usage: python scripts/eci_factor.py data/raw/eci_2025_q2/index.json 2024 June 2025 June
_, eci_json, src_year, src_periodName, dst_year, dst_periodName = sys.argv

js = json.load(open(eci_json))
obs = {}
for d in js["observations"]:
    year = d["year"]
    pname = d["periodName"]
    val = float(d["value"])
    obs[(year, pname)] = val
    # Map quarterly names to canonical month names for convenience
    qmap = {
        "1st Quarter": "March",
        "2nd Quarter": "June",
        "3rd Quarter": "September",
        "4th Quarter": "December",
    }
    if pname in qmap:
        obs[(year, qmap[pname])] = val

try:
    src = obs[(src_year, src_periodName)]
    dst = obs[(dst_year, dst_periodName)]
except KeyError:
    raise SystemExit(f"Missing ECI observation for {(src_year, src_periodName)} or {(dst_year, dst_periodName)}")

print(round(dst/src, 6))
