# 30-day build & launch plan (America/Los_Angeles)

## Week 1 — Spec, data, kernel (Days 1–7)

**Day 1 — Product spec & rails**

* Lock scope: 1 endpoint `POST /rc/estimate` + 1 memo endpoint `GET /rc/memo/{id}`.
* Decide stack (FastAPI or Fastify), repo, CI, error tracking, and domain.
* Draft disclaimers (“informational, not tax/legal advice”).
  **Acceptance:** 1-page spec + ERD + routes diagram in repo.

**Day 2 — Data sources**

* Pull **BLS OEWS** latest (state + MSA) + documentation; confirm percentile fields (P10, P25, P50, P75, P90). ([Bureau of Labor Statistics][1])
* Pick an **inflation/recency adjuster** using **BLS ECI** (index wages from OEWS vintage → present). ([Bureau of Labor Statistics][2])
  **Acceptance:** raw data cached in storage with version tags (e.g., `oews_2024_05`, `eci_2025_q2`).

**Day 3 — Occupation mapping**

* Choose 15–25 owner “task buckets” (sales, ops, admin, finance, tech, etc.).
* Map each bucket → 1–2 **O*NET/SOC** codes; store weightable list. Add **O*NET attribution** (license requires CC-BY + trademark notice). ([onetcenter.org][3])
  **Acceptance:** `soc_map.json` checked in with notes.

**Day 4–5 — Estimation kernel v1**

* Compute locality wage for each SOC (P25/P50/P75) at user’s MSA; fallback to state if missing. ([Bureau of Labor Statistics][4])
* Weighted blend by role split (e.g., 40% SOC-A, 30% SOC-B…).
* Apply **size/profitability adjustment** (heuristic) referencing classic factor tests (Elliotts 5-factor / “independent investor” signal). ([openjurist.org][5])
  **Acceptance:** given 5 canned personas, kernel returns `{low, median, high, recommended}` and an “assumptions” array.

**Day 6 — Risk flags**

* Add **Watson pattern** flag: high distributions with low wage proxy. ([CaseLaw][6])
  **Acceptance:** unit tests trip the flag under low-wage/high-profit inputs.

**Day 7 — API surface & OpenAPI**

* Implement `POST /rc/estimate` (idempotent hash on normalized payload).
* `GET /rc/memo/{id}` returns signed URL (HTML/PDF).
* Publish **OpenAPI** for your **ChatGPT Action**. ([OpenAI Platform][7])
  **Acceptance:** `openapi.json` passes Swagger validation; local Postman tests green.

---

## Week 2 — Action, memo, website (Days 8–14)

**Day 8 — Staging + telemetry**

* Deploy API to staging; add rate-limits, request/response logging (PII-redacted).
  **Acceptance:** health checks + structured logs in dashboard.

**Day 9 — ChatGPT Action wiring**

* Create a GPT with **Action** → point at `openapi.json`; start with **No Auth** for free QuickCheck.
* Test round-trip prompts (“I’m an S-Corp owner in Austin… what’s a reasonable salary?”). ([OpenAI Platform][7])
  **Acceptance:** GPT calls your endpoint and shows numbers + short explanation.

**Day 10 — Web QuickCheck**

* Next.js page with a 60-second form (location, role split sliders, revenue/profit, hours).
* Show range + “Create memo ($9)” CTA.
  **Acceptance:** Lighthouse ≥ 90 (perf/accessibility).

**Day 11 — Memo generator**

* One-page HTML → PDF with: inputs, SOCs used, OEWS table cites, method, flags, and references to IRS Job Aid + factor tests. ([IRS][8])
  **Acceptance:** PDF renders < 2s; includes mandatory **O*NET** and **BLS** attributions. ([onetonline.org][9])

**Day 12 — Payments + pricing**

* Stripe: $9 per memo; store receipt + memo id; rate-limit free API calls.
  **Acceptance:** test card → successful memo purchase + email receipt.

**Day 13 — OAuth (Pro)**

* Add OAuth for “save scenarios / firm branding / unlimited memos (Pro)”.
  **Acceptance:** sign-in flow gates unlimited memos; quota shown in UI.

**Day 14 — Private beta**

* Invite 5–10 tax pros; capture feedback; embed a “Was this useful?” micro-survey.
  **Acceptance:** ≥ 70 NPS from at least 5 testers or clear issues list.

---

## Week 3 — Quality, coverage, docs (Days 15–21)

**Day 15–16 — Calibration**

* Compare outputs on ~20 hand-picked scenarios; adjust size/profit scaler bands.
* Add “explain adjustments” in JSON (`adjustments: [{type:'size', delta:+8%}, …]`).
  **Acceptance:** internal rubric consistency across cases.

**Day 17 — Edge cases**

* No MSA match → state fallback; multi-role extreme splits; zero-profit firms.
* Hard caps to avoid absurd values.
  **Acceptance:** 100% passing on edge test suite.

**Day 18 — Caching & costs**

* Cache OEWS lookups by `(MSA,SOC)` for 24h; memo HTML snapshot for 7d.

**Day 19 — Docs site**

* “How we estimate” explainer, API docs, sample payloads, and references to OEWS/O*NET/IRS. ([Bureau of Labor Statistics][10])

**Day 20 — Compliance pass**

* **Attribution**: O*NET CC-BY + trademark; link to license. ([onetcenter.org][3])
* **Privacy**: PII minimization; no SSNs; store only aggregates & scenarios.
* **Legal**: show IRS Job Aid as non-binding reference. ([IRS][8])

**Day 21 — Observability**

* Alerts on p95 latency, 5xx rate, and Action call failures; add synthetic checks.

---

## Week 4 — Launch & GTM (Days 22–30)

**Day 22 — Copy & visuals**

* Landing headline: “Reasonable compensation in 2 minutes—backed by BLS & O*NET.”
* Add examples and “what auditors look for” crib (Job Aid, Elliotts). ([IRS][8])

**Day 23 — Security & backups**

* Rotate all keys, WAF rules, bot protection; daily DB snapshot.

**Day 24 — Pricing page & limits**

* Free in-chat range; $9 PDF; **Pro** $29/mo unlimited + branding.

**Day 25 — GPT polishing**

* Shorter prompts, robust tool descriptions, clear caveats, and one-click **Open memo** button. ([OpenAI Platform][7])

**Day 26 — Final QA**

* 30 scenario regression; memos render reliably across devices; Stripe live mode.

**Day 27 — Soft launch**

* Email beta testers + a few communities; monitor errors/abandon.

**Day 28 — Public launch**

* Announce the GPT with Action + website; create a walkthrough video.

**Day 29–30 — Post-launch**

* Fix top issues; add 2 small features (firm branding + CSV export); start 2 partner talks.

---

## What the algorithm does (v1, transparent)

1. **Role mix → SOC codes** using your map. (You’ll show the codes in the memo.) ([onetonline.org][11])
2. Pull **OEWS percentile wages** for each SOC at the user’s **MSA** (fallback: state), blend by time share to get a **baseline** P25/P50/P75. ([Bureau of Labor Statistics][4])
3. **Index to present** with **ECI** (wages & salaries). ([Bureau of Labor Statistics][12])
4. Apply a small **size/profit scaler** (documented) inspired by **Elliotts** factors and, when profits are very high, mention the **independent-investor** perspective. ([openjurist.org][5])
5. Emit `{low, median, high, recommended}` + `notes`, and **flags** (e.g., “Watson risk: distributions >> wages”). ([CaseLaw][6])

---

## Deliverables checklist (you’ll have these by Day 30)

* `openapi.json` for the **ChatGPT Action** (staging + prod). ([OpenAI Platform][13])
* Deployed API with `/rc/estimate`, `/rc/memo/{id}`.
* Working GPT (Action) that returns a range in-chat and deep-links to your memo. ([OpenAI Platform][7])
* Website QuickCheck + Stripe paywall ($9 PDF).
* Audit-aware memo (HTML/PDF) citing **OEWS**, **O*NET**, **IRS Job Aid**, and case-law touchpoints. ([Bureau of Labor Statistics][1])
* Metrics dashboard + alerts.

---

## Nice-to-haves if time permits

* MSA auto-detect from ZIP; multi-locale currency; simple org accounts for tax firms.
* “Why not the 90th percentile?” explainer to curb aggressive settings.

[1]: https://www.bls.gov/oes/current/oes_tec.htm?utm_source=chatgpt.com
[2]: https://www.bls.gov/eci/?utm_source=chatgpt.com
[3]: https://www.onetcenter.org/license_db.html?utm_source=chatgpt.com
[4]: https://www.bls.gov/oes/2024/may/oessrcma.htm?utm_source=chatgpt.com
[5]: https://openjurist.org/716/f2d/1241/elliotts-inc-v-commissioner-of-internal-revenue?utm_source=chatgpt.com
[6]: https://caselaw.findlaw.com/court/us-8th-circuit/1595046.html?utm_source=chatgpt.com
[7]: https://platform.openai.com/docs/actions/actions-library/getting-started?utm_source=chatgpt.com
[8]: https://www.irs.gov/pub/irs-lbi/Reasonable%20Compensation%20Job%20Aid%20for%20IRS%20Valuation%20Professionals.pdf?utm_source=chatgpt.com
[9]: https://www.onetonline.org/help/license?utm_source=chatgpt.com
[10]: https://www.bls.gov/oes/?utm_source=chatgpt.com
[11]: https://www.onetonline.org/?utm_source=chatgpt.com
[12]: https://www.bls.gov/news.release/eci.nr0.htm?utm_source=chatgpt.com
[13]: https://platform.openai.com/docs/actions/getting-started/openapi-example?utm_source=chatgpt.com
