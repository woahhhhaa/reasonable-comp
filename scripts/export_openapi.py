import json
import os

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


