from fastapi.testclient import TestClient

from src.ownerpay.api.main import app


client = TestClient(app)


def _payload(role_split=None):
    return {
        "tax_year": 2025,
        "location": {"state": "CA", "msa_code": "41860"},
        "business": {"entity_type": "s_corp", "revenue": 300000, "profit": 100000, "headcount": 2},
        "owner": {"hours_per_week": 40, "experience_years": 7},
        "role_split": role_split
        or [
            {"role": "sales", "percent": 40},
            {"role": "operations", "percent": 30},
            {"role": "administration", "percent": 30},
        ],
    }


def test_same_payload_same_id():
    r1 = client.post("/rc/estimate", json=_payload())
    r2 = client.post("/rc/estimate", json=_payload())
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]


def test_reordered_role_split_same_id():
    a = _payload()
    b = _payload(role_split=list(reversed(a["role_split"])))
    r1 = client.post("/rc/estimate", json=a)
    r2 = client.post("/rc/estimate", json=b)
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]


def test_changed_percent_different_id():
    a = _payload()
    b = _payload(role_split=[
        {"role": "sales", "percent": 39},
        {"role": "operations", "percent": 31},
        {"role": "administration", "percent": 30},
    ])
    r1 = client.post("/rc/estimate", json=a)
    r2 = client.post("/rc/estimate", json=b)
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["id"] != r2.json()["id"]


