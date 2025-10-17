from types import SimpleNamespace

from src.ownerpay.core.kernel import compute_estimate


def _base_payload(**overrides):
    payload = {
        "tax_year": 2025,
        "location": {"state": "CA", "msa_code": "41860"},
        "business": {"entity_type": "s_corp", "revenue": 1000000, "profit": 400000, "headcount": 3},
        "owner": {"hours_per_week": 40, "experience_years": 8},
        "role_split": [
            {"role": "sales", "percent": 40},
            {"role": "operations", "percent": 30},
            {"role": "administration", "percent": 30},
        ],
    }
    for k, v in overrides.items():
        payload[k] = v
    return SimpleNamespace(**payload)


def _has_flag(flags, code: str) -> bool:
    return any(f.get("code") == code for f in flags or [])


def test_watson_flag_positive_high_profit_ratio():
    payload = _base_payload()
    kr = compute_estimate(payload)
    assert _has_flag(kr.flags, "watson_pattern"), f"expected watson flag; flags={kr.flags}"
    watson = next(f for f in kr.flags if f.get("code") == "watson_pattern")
    assert watson.get("level") == "warning"
    assert watson.get("details", {}).get("wage_proxy") == "recommended"


def test_watson_flag_negative_low_margin():
    payload = _base_payload(business={"entity_type": "s_corp", "revenue": 300000, "profit": 30000, "headcount": 2})
    kr = compute_estimate(payload)
    assert not _has_flag(kr.flags, "watson_pattern"), f"did not expect watson flag; flags={kr.flags}"


