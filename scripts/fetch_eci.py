#!/usr/bin/env python3
import os, json, requests
BASE = "data/raw"
os.makedirs(BASE, exist_ok=True)

API = "https://api.bls.gov/publicAPI/v2/timeseries/data"
SERIES = "CIU2020000000000I"
key = os.getenv("BLS_API_KEY")

payload = {"seriesid":[SERIES],"registrationKey": key} if key else {"seriesid":[SERIES]}
r = requests.post(API, json=payload, timeout=60)
r.raise_for_status()
js = r.json()
if js.get("status") != "REQUEST_SUCCEEDED":
    raise SystemExit(f"BLS API error: {js}")

data = js["Results"]["series"][0]["data"]

latest = max(data, key=lambda d: (int(d["year"]), int(d["period"][1:])))
y, p = int(latest["year"]), int(latest["period"][1:])
tag = f"eci_{y}_q{p}"

path = f"{BASE}/{tag}"
os.makedirs(path, exist_ok=True)
open(f"{path}/index.json","w").write(json.dumps({"series":SERIES,"observations":data}, indent=2))
open(f"{path}/VERSION","w").write(tag)
print(f"OK {tag}")
