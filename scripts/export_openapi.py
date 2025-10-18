import json
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so that `src` is importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ownerpay.api.main import app


def main() -> None:
    schema = app.openapi()
    # Inject servers list for ChatGPT Action friendliness
    schema["servers"] = [
        {"url": "https://api-staging.ownerpay.dev"},
        {"url": "https://api.ownerpay.dev"},
        {"url": "http://localhost:8000"},
    ]
    out_dir = os.path.join("ownerpay")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "openapi.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main()


