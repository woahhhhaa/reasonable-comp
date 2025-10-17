# Risks & Day-2 Hand-off

## Risks
- Scope creep beyond two endpoints
- Compliance/claims wording sensitivity
- Data model churn once kernel lands

## Mitigations
- Freeze Day-1 scope
- Lock disclaimer language
- Keep schema backward-compatible with additive fields

## Day-2 Prep
- Gather OEWS/O*NET samples; build `soc_map.json`
- Add strict validators (role percent sum ≈ 100±0.5, numeric bounds, tax_year ∈ {2024,2025,2026})
- Memo HTML template + storage interface stub (URL resolver)
