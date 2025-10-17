import os
from urllib.parse import urlparse, parse_qs

from fastapi.testclient import TestClient

from src.ownerpay.api.main import app


client = TestClient(app)


def test_memo_returns_urls_with_exp_and_sig_when_secret_set(monkeypatch):
    monkeypatch.setenv("MEMO_SIGNING_SECRET", "test_secret")
    monkeypatch.setenv("MEMO_TTL_SECONDS", "60")
    r = client.get("/rc/memo/test-id")
    assert r.status_code == 200
    js = r.json()
    for key in ("html_url", "pdf_url"):
        u = urlparse(js[key])
        qs = parse_qs(u.query)
        assert "exp" in qs and "sig" in qs


def test_memo_returns_unsigned_when_secret_missing(monkeypatch):
    monkeypatch.delenv("MEMO_SIGNING_SECRET", raising=False)
    r = client.get("/rc/memo/test-id2")
    assert r.status_code == 200
    js = r.json()
    assert "?" not in js["html_url"] and "?" not in js["pdf_url"]


