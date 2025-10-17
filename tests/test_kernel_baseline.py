from fastapi.testclient import TestClient

from src.ownerpay.api.main import app


client = TestClient(app)


def test_estimate_uses_kernel_and_returns_indexed_values():
    payload = {
        "tax_year": 2025,
        "location": {"state": "TX", "msa_code": "12420"},  # Austin-Round Rock-Georgetown, TX
        "business": {
            "entity_type": "s_corp",
            "revenue": 400000,
            "profit": 140000,
            "headcount": 2,
        },
        "owner": {"hours_per_week": 40, "experience_years": 10},
        "role_split": [
            {"role": "sales", "percent": 40},
            {"role": "operations", "percent": 30},
            {"role": "administration", "percent": 20},
            {"role": "technical", "percent": 10},
        ],
    }
    r = client.post("/rc/estimate", json=payload)
    assert r.status_code == 200
    js = r.json()
    # Kernel should populate these fields (non-stub)
    assert js["low"] > 0 and js["median"] > 0 and js["high"] > 0
    assert js["low"] <= js["median"] <= js["high"]
    assert any("eci_tag=" in a for a in js.get("assumptions", []))

