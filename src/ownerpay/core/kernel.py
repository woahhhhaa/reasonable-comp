from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from .data import OEWS_VINTAGE_TAG, get_oews_msa, get_oews_state
from .eci import compute_eci_factor
from .mapping import expand_roles_to_soc_weights


@dataclass
class KernelResult:
    low: float
    median: float
    high: float
    recommended: float
    soc_sources: List[dict]
    adjustments: List[dict]
    flags: List[dict]
    assumptions: List[str]


def _lookup_percentiles(df_msa: pd.DataFrame, df_state: pd.DataFrame, soc: str, msa_code: str, state_code: str) -> tuple[float, float, float, str]:
    row = df_msa[(df_msa.SOC == soc) & (df_msa.AREA == msa_code)].head(1)
    source = "msa"
    if row.empty or row[["A_PCT25", "A_PCT50", "A_PCT75"]].isna().any(axis=None):
        row = df_state[(df_state.SOC == soc) & (df_state.AREA == state_code)].head(1)
        source = "state"
    if row.empty:
        raise ValueError(f"No OEWS data for SOC {soc} in MSA {msa_code} or state {state_code}")
    s25 = float(row["A_PCT25"].iloc[0])
    s50 = float(row["A_PCT50"].iloc[0])
    s75 = float(row["A_PCT75"].iloc[0])
    return s25, s50, s75, source


def _compute_size_profit_adjustment(
    low: float,
    med: float,
    high: float,
    business: dict,
    owner: dict,
) -> tuple[float, list[dict]]:
    """Compute a v1 heuristic delta fraction based on size and profitability.

    Returns (delta_fraction, adjustments_list).
    """
    revenue = max(float(business.get("revenue", 0.0)), 0.0)
    profit = max(float(business.get("profit", 0.0)), 0.0)
    # Headcount excludes owner per Day-5 policy
    headcount = max(int(business.get("headcount", 0)), 0)

    # Profitability band
    profit_margin = profit / max(revenue, 1.0)
    if profit_margin < 0.05:
        prof_delta = -0.05
    elif profit_margin < 0.15:
        prof_delta = 0.00
    elif profit_margin < 0.30:
        prof_delta = 0.05
    else:
        prof_delta = 0.10

    # Size band by revenue
    if revenue < 250_000:
        size_delta = -0.03
    elif revenue < 1_000_000:
        size_delta = 0.00
    elif revenue < 3_000_000:
        size_delta = 0.03
    else:
        size_delta = 0.05

    # Hours modifier dampens only positive profitability deltas for part-time owners
    hours = float(owner.get("hours_per_week", 40.0))
    if hours < 20:
        positive_scale = 0.7
    elif hours < 35:
        positive_scale = 0.85
    else:
        positive_scale = 1.0

    adjusted_prof_delta = prof_delta * positive_scale if prof_delta > 0 else prof_delta
    delta_fraction = size_delta + adjusted_prof_delta

    adjustments = [
        {"type": "profitability", "delta": round(prof_delta, 4), "reason": f"profit_margin={profit_margin:.2f}"},
        {"type": "size", "delta": round(size_delta, 4), "reason": f"revenue={revenue:.0f}; headcount_ex_owner={headcount}"},
        {"type": "hours", "delta": round(positive_scale, 4), "reason": f"hours_per_week={hours:.0f}"},
    ]

    return delta_fraction, adjustments


def _compute_risk_flags(recommended: float, business: dict) -> list[dict]:
    flags: list[dict] = []
    revenue = max(float(business.get("revenue", 0.0)), 0.0)
    profit = max(float(business.get("profit", 0.0)), 0.0)

    # Watson-pattern: high distributions with low wage proxy.
    # We proxy distributions with profit and wage with recommended.
    if recommended <= 0:
        return flags

    profit_margin = profit / max(revenue, 1.0)
    profit_to_wage = profit / max(recommended, 1.0)

    if profit_margin >= 0.30 and profit_to_wage >= 2.0:
        flags.append(
            {
                "code": "watson_pattern",
                "level": "warning",
                "message": "High distributions relative to wage proxy",
                "details": {
                    "profit_margin": round(profit_margin, 3),
                    "profit_to_wage": round(profit_to_wage, 2),
                    "wage_proxy": "recommended",
                },
                "references": [
                    {
                        "title": "Eighth Circuit — Watson",
                        "url": "https://caselaw.findlaw.com/court/us-8th-circuit/1595046.html",
                    }
                ],
            }
        )

    return flags


def compute_estimate(payload) -> KernelResult:
    # Data
    df_msa = get_oews_msa()
    df_state = get_oews_state()

    # Mapping: role mix -> SOC weights
    soc_weights: Dict[str, float] = expand_roles_to_soc_weights(payload.role_split)

    msa_code = payload.location["msa_code"]
    state_code = payload.location["state"]

    p25 = p50 = p75 = 0.0
    sources: List[dict] = []
    for soc, w in soc_weights.items():
        s25, s50, s75, source = _lookup_percentiles(df_msa, df_state, soc, msa_code, state_code)
        p25 += w * s25
        p50 += w * s50
        p75 += w * s75
        sources.append({"soc": soc, "source": source})

    # ECI factor: OEWS May 2024 -> ECI June 2024 as source point
    factor, eci_tag = compute_eci_factor(src=(2024, "June"))
    low = round(p25 * factor)
    med = round(p50 * factor)
    high = round(p75 * factor)

    # Day-5: size/profitability heuristic to adjust recommended
    delta_fraction, adjustments = _compute_size_profit_adjustment(
        low=low, med=med, high=high, business=payload.business, owner=payload.owner
    )
    raw_rec = med * (1.0 + delta_fraction)
    cap = high * 1.10
    capped = max(low, min(raw_rec, cap))
    recommended = round(capped)

    # Day-6: risk flags
    flags = _compute_risk_flags(recommended=recommended, business=payload.business)

    assumptions = [
        f"tax_year={payload.tax_year}",
        f"oews_vintage={OEWS_VINTAGE_TAG}",
        f"eci_tag={eci_tag}",
        "roles weighted by percent",
        "eci indexed to present",
        "headcount_policy=headcount_excludes_owner",
        "size_profit_heuristic=v1",
    ]
    if raw_rec > cap:
        assumptions.append("recommended_cap=high*1.10")

    return KernelResult(
        low=low,
        median=med,
        high=high,
        recommended=recommended,
        soc_sources=sources,
        adjustments=adjustments,
        flags=flags,
        assumptions=assumptions,
    )


