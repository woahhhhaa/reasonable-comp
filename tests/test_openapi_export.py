import json
import os


def test_openapi_file_exists_and_has_servers():
    path = os.path.join("ownerpay", "openapi.json")
    assert os.path.exists(path), "openapi.json missing; run scripts/export_openapi.py"
    js = json.load(open(path))
    servers = js.get("servers", [])
    assert isinstance(servers, list) and len(servers) >= 3
    urls = {s.get("url") for s in servers}
    assert "https://api-staging.ownerpay.dev" in urls
    assert "https://api.ownerpay.dev" in urls
    assert "http://localhost:8000" in urls


