from fastapi.testclient import TestClient

from src.ownerpay.api.main import app

client = TestClient(app)


def test_estimate():
    payload = {
        "tax_year": 2025,
        "location": {"state": "CA", "msa_code": "41860"},
        "business": {
            "entity_type": "s_corp",
            "revenue": 350000,
            "profit": 120000,
            "headcount": 3,
        },
        "owner": {"hours_per_week": 40, "experience_years": 8},
        "role_split": [
            {"role": "sales", "percent": 40},
            {"role": "operations", "percent": 30},
            {"role": "administration", "percent": 30},
        ],
    }
    r = client.post("/rc/estimate", json=payload)
    assert r.status_code == 200
    assert "recommended" in r.json()
