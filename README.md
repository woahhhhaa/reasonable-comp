# OwnerPay API (Reasonable Comp)
Day-1 scaffold for /rc/estimate and /rc/memo/{id}.

## Domain & Environments
- Decision: `ownerpay.dev` with `api.ownerpay.dev` and `api-staging.ownerpay.dev`.
- Steps: buy domain (Namecheap/Cloudflare), set nameservers to Cloudflare, add A/AAAA/CNAME, point later to hosting.
- `.env.example` stays committed; real `.env` never committed.

## EOD Checklist
- Repo scaffolded and pushed to GitHub as private `ownerpay`.
- App runs locally via `uvicorn src.ownerpay.api.main:app --reload`.
- `pytest -q` passes (smoke test).
- CI is green on push and PR.
- Sentry init present; DSN from env; safe if unset.
- Docs committed: spec, ERD (Mermaid + ASCII), routes (Mermaid + ASCII).
- Meta files present: README, LICENSE (MIT), CODEOWNERS, CONTRIBUTING, `.editorconfig`, `pyproject.toml`.
- `.env.example` checked in.

