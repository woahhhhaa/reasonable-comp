# OwnerPay Day-1 Product Spec (Reasonable Comp)

- Time zone: America/Los_Angeles (PT)

## Problem
Small-business owners need a defendable, market-based reasonable compensation estimate for IRS and planning.

## Users
- Primary: S-corp owners and advisors (CPAs, fractional CFOs).
- Secondary: Internal agents and memo rendering service.

## Assumptions
- Day-1 returns a deterministic stub for two endpoints only.
- No persistence or kernel integration today; memo is a URL placeholder.

## Non-goals (Day-1)
- Real comp kernel, data ingestion, SOC mapping, auth, billing, persistence.

## Success Criteria
- Two endpoints ship with green CI and a smoke test.
- Sentry wired via env var; safe to run with no DSN.

## Endpoints
- POST `/rc/estimate` → { id, low, median, high, recommended, memo_url, meta }
- GET `/rc/memo/{id}` → { id, html_url }

## Validation (Day-1)
- Basic schema validation via Pydantic.
- Additional strict validators deferred to Day-2 (role percent sum, numeric ranges).

## Latency/SLO (Day-1)
- P50 < 150ms local, P95 < 500ms; errors mapped to 4xx/5xx.

## Disclaimer
This is not tax or legal advice. Values are illustrative Day-1 stubs.

