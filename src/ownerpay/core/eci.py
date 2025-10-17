import glob
import json
import os
from functools import lru_cache
from typing import Tuple


RAW_BASE = os.path.join("data", "raw")


@lru_cache(maxsize=1)
def _load_latest_eci() -> tuple[dict, str]:
    candidates = sorted(glob.glob(os.path.join(RAW_BASE, "eci_*", "index.json")))
    if not candidates:
        raise FileNotFoundError("No ECI index.json found under data/raw/eci_*/")
    latest = candidates[-1]
    js = json.load(open(latest))
    tag = os.path.basename(os.path.dirname(latest))
    return js, tag


def _observations_map(eci_js: dict) -> dict:
    obs = {}
    for d in eci_js["observations"]:
        year = d["year"]
        pname = d["periodName"]
        val = float(d["value"])
        obs[(year, pname)] = val
        qmap = {
            "1st Quarter": "March",
            "2nd Quarter": "June",
            "3rd Quarter": "September",
            "4th Quarter": "December",
        }
        if pname in qmap:
            obs[(year, qmap[pname])] = val
    return obs


def compute_eci_factor(src: Tuple[int, str]) -> tuple[float, str]:
    eci_js, tag = _load_latest_eci()
    obs = _observations_map(eci_js)
    # Destination is the latest observation in the file
    # Find max by (year, month order) using a month order map
    month_order = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12,
        "1st Quarter": 3, "2nd Quarter": 6, "3rd Quarter": 9, "4th Quarter": 12,
    }
    latest_key = max(obs.keys(), key=lambda k: (int(k[0]), month_order.get(k[1], 0)))
    src_val = obs.get(src)
    dst_val = obs.get(latest_key)
    if src_val is None or dst_val is None:
        raise ValueError(f"Missing ECI observation for src={src} or dst={latest_key}")
    return round(dst_val / src_val, 6), tag


