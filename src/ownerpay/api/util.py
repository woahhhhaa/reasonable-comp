import hashlib
import json
from typing import Any, Dict, Iterable


def _sorted_role_split(role_split: Iterable[dict]) -> list[dict]:
    items = [
        {
            "role": str(entry.get("role", "")),
            "percent": float(entry.get("percent", 0.0)),
        }
        for entry in role_split or []
    ]
    items.sort(key=lambda e: (e.get("role", ""), e.get("percent", 0.0)))
    return items


def canonicalize_estimate_payload(p: Dict[str, Any]) -> Dict[str, Any]:
    """Return a canonicalized shallow copy of the estimate payload for hashing.

    - Sort role_split deterministically by (role, percent)
    - Leave other structures intact; JSON dump with sort_keys ensures key ordering
    """
    canonical = dict(p)
    canonical["role_split"] = _sorted_role_split(p.get("role_split", []))
    return canonical


def compute_request_id(canonical_payload: Dict[str, Any]) -> str:
    js = json.dumps(canonical_payload, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(js.encode("utf-8")).hexdigest()
    return digest[:12]


