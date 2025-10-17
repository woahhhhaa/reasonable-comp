from types import SimpleNamespace

from src.ownerpay.core.kernel import compute_estimate


def _base(location_state="CA", msa_code="41860"):
    return {
        "location": {"state": location_state, "msa_code": msa_code},
        "owner": {"hours_per_week": 40, "experience_years": 8},
    }


def _assert_common(kr):
    assert kr.low > 0 and kr.median > 0 and kr.high > 0
    assert kr.low <= kr.median <= kr.high
    assert kr.recommended >= kr.low
    assert kr.recommended <= int(kr.high * 1.10 + 1)
    assert any(a.startswith("oews_vintage=") for a in kr.assumptions)
    assert any(a.startswith("eci_tag=") for a in kr.assumptions)
    assert any(a == "headcount_policy=headcount_excludes_owner" for a in kr.assumptions)


def test_persona_solo_consultant():
    base = _base()
    payload = SimpleNamespace(
        tax_year=2025,
        location=base["location"],
        business={"entity_type": "s_corp", "revenue": 150_000, "profit": 60_000, "headcount": 0},
        owner=base["owner"],
        role_split=[
            {"role": "sales", "percent": 40},
            {"role": "operations", "percent": 30},
            {"role": "administration", "percent": 30},
        ],
    )
    kr = compute_estimate(payload)
    _assert_common(kr)


def test_persona_high_margin_saas_micro():
    base = _base()
    payload = SimpleNamespace(
        tax_year=2025,
        location=base["location"],
        business={"entity_type": "s_corp", "revenue": 600_000, "profit": 300_000, "headcount": 2},
        owner=base["owner"],
        role_split=[
            {"role": "technical", "percent": 40},
            {"role": "sales", "percent": 30},
            {"role": "operations", "percent": 30},
        ],
    )
    kr = compute_estimate(payload)
    _assert_common(kr)
    assert any(adj.get("type") == "profitability" for adj in kr.adjustments)


def test_persona_low_margin_agency():
    base = _base()
    payload = SimpleNamespace(
        tax_year=2025,
        location=base["location"],
        business={"entity_type": "s_corp", "revenue": 700_000, "profit": 35_000, "headcount": 6},
        owner=base["owner"],
        role_split=[
            {"role": "sales", "percent": 30},
            {"role": "operations", "percent": 40},
            {"role": "administration", "percent": 30},
        ],
    )
    kr = compute_estimate(payload)
    _assert_common(kr)
    assert kr.recommended <= kr.median


def test_persona_growing_ecommerce():
    base = _base()
    payload = SimpleNamespace(
        tax_year=2025,
        location=base["location"],
        business={"entity_type": "s_corp", "revenue": 2_200_000, "profit": 250_000, "headcount": 8},
        owner=base["owner"],
        role_split=[
            {"role": "marketing", "percent": 30},
            {"role": "operations", "percent": 40},
            {"role": "administration", "percent": 30},
        ],
    )
    kr = compute_estimate(payload)
    _assert_common(kr)


def test_persona_exceptional_profitability_over_high_but_capped():
    base = _base()
    payload = SimpleNamespace(
        tax_year=2025,
        location=base["location"],
        business={"entity_type": "s_corp", "revenue": 1_100_000, "profit": 550_000, "headcount": 1},
        owner=base["owner"],
        role_split=[
            {"role": "technical", "percent": 30},
            {"role": "sales", "percent": 40},
            {"role": "operations", "percent": 30},
        ],
    )
    kr = compute_estimate(payload)
    _assert_common(kr)
    # In extreme profitability, recommended can exceed high but must be capped <= high*1.10
    assert kr.recommended >= kr.high
    assert kr.recommended <= int(kr.high * 1.10 + 1)
    assert any(adj.get("type") == "profitability" for adj in kr.adjustments)


