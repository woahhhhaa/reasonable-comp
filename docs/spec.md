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

## Day-5 Notes (Kernel Heuristic v1)
- Headcount policy: `headcount` excludes the owner.
- Recommended compensation = median × (1 + size/profit delta), then clamped to [P25, P75×1.10].
- Size bands (revenue): <250k:-3%, 250k–1M:0%, 1–3M:+3%, >3M:+5%.
- Profitability bands (margin): <5%:-5%, 5–15%:0%, 15–30%:+5%, >30%:+10%.
- Hours dampener for positive profitability deltas: <20h:×0.7, 20–34h:×0.85, ≥35h:×1.0.

## Day-6 Notes (Risk Flags v1)
- Watson pattern: trigger a warning when distributions are high relative to wage proxy.
- Proxies: distributions ≈ `business.profit`; wage proxy = kernel `recommended`.
- Thresholds: `profit_margin >= 0.30` AND `profit/recommended >= 2.0`.
- Emitted flag example:
  ```json
  {
    "code": "watson_pattern",
    "level": "warning",
    "message": "High distributions relative to wage proxy",
    "details": {"profit_margin": 0.40, "profit_to_wage": 2.3, "wage_proxy": "recommended"},
    "references": [{"title": "Eighth Circuit — Watson", "url": "https://caselaw.findlaw.com/court/us-8th-circuit/1595046.html"}]
  }
  ```

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

