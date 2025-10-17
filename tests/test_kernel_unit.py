from types import SimpleNamespace

from src.ownerpay.core.kernel import compute_estimate


def test_compute_estimate_basic_monotonic_and_tags():
    payload = SimpleNamespace(
        tax_year=2025,
        location={"state": "CA", "msa_code": "41860"},
        business={"entity_type": "s_corp", "revenue": 300000, "profit": 100000, "headcount": 1},
        owner={"hours_per_week": 40, "experience_years": 7},
        role_split=[
            {"role": "sales", "percent": 30},
            {"role": "operations", "percent": 30},
            {"role": "administration", "percent": 20},
            {"role": "technical", "percent": 20},
        ],
    )
    kr = compute_estimate(payload)
    assert kr.low > 0 and kr.median > 0 and kr.high > 0
    assert kr.low <= kr.median <= kr.high
    assert any(a.startswith("oews_vintage=") for a in kr.assumptions)
    assert any(a.startswith("eci_tag=") for a in kr.assumptions)
    assert len(kr.soc_sources) > 0
    assert all(s["source"] in ("msa", "state") for s in kr.soc_sources)


