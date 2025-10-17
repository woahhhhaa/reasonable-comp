import json
import os
from functools import lru_cache
from typing import Dict, Iterable


SOC_MAP_PATH = os.path.join("occ-map", "soc_map.json")


@lru_cache(maxsize=1)
def _load_soc_map() -> dict:
    with open(SOC_MAP_PATH) as f:
        return json.load(f)


ROLE_ALIASES = {
    "administration": "admin",
}


TECH_BUCKETS = ["sw_app", "sw_infra", "qa", "devops", "ithelp"]


def expand_roles_to_soc_weights(role_split: Iterable[dict]) -> Dict[str, float]:
    buckets = _load_soc_map()["buckets"]
    bucket_by_id = {b["id"]: b for b in buckets}

    soc_to_weight: Dict[str, float] = {}

    for entry in role_split:
        role_id = entry["role"]
        percent = float(entry.get("percent", 0.0)) / 100.0
        role_id = ROLE_ALIASES.get(role_id, role_id)

        if role_id == "technical":
            # Evenly distribute the role percent among technical buckets
            per_bucket_weight = percent / len(TECH_BUCKETS)
            target_bucket_ids = TECH_BUCKETS
        else:
            per_bucket_weight = percent
            target_bucket_ids = [role_id]

        for bucket_id in target_bucket_ids:
            bucket = bucket_by_id.get(bucket_id)
            if not bucket:
                continue
            for soc_entry in bucket.get("soc_codes", []):
                soc = soc_entry["soc"]
                soc_w = float(soc_entry.get("weight", 1.0))
                soc_to_weight[soc] = soc_to_weight.get(soc, 0.0) + per_bucket_weight * soc_w

    # Normalize to sum to 1.0 if non-empty
    total = sum(soc_to_weight.values())
    if total > 0:
        soc_to_weight = {k: v / total for k, v in soc_to_weight.items()}
    return soc_to_weight


