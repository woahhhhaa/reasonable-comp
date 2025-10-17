# Data Sources (Day-2)

## What we pulled
- OEWS May 2024 MSA files (all areas + MSA definitions) from BLS pages:
  - `https://www.bls.gov/oes/2024/may/oessrcma.htm`
  - `https://www.bls.gov/oes/2024/may/msa_def.htm`
- ECI (NSA, wages & salaries, private industry) series: `CIU2020000000000I` via BLS API:
  - `https://api.bls.gov/publicAPI/v2/timeseries/data`

## Versioned folders
- `data/raw/oews_YYYY_MM/` (e.g., `oews_2024_05`)
- `data/raw/eci_YYYY_qN/` (e.g., `eci_2025_q2`) with `index.json` and `VERSION`
- `data/processed/oews_YYYY_MM/` for normalized outputs

## OEWS normalization
- Input columns expected: `OCC_CODE, OCC_TITLE, AREA, AREA_NAME, A_PCT10, A_PCT25, A_MEDIAN, A_PCT75, A_PCT90`
- Kept/renamed: `SOC, OCC_TITLE, AREA, AREA_NAME, A_PCT10, A_PCT25, A_PCT50, A_PCT75, A_PCT90`
- Percentiles: A_PCT10/25/50/75/90 represent annual wage percentiles for an occupation in an MSA.

## ECI usage
- Treat OEWS May 2024 as Q2 2024 ("June").
- Use `scripts/eci_factor.py` to scale wages from 2024 June to latest quarter using `data/raw/eci_*/index.json`.

## Runbook
1. `python scripts/fetch_oews.py`
2. `python scripts/normalize_oews.py`
3. `python scripts/fetch_eci.py`
4. `python scripts/eci_factor.py data/raw/eci_2025_q2/index.json 2024 June 2025 June`
5. `pytest -q`
