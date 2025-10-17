import os

import sentry_sdk
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(dsn=sentry_dsn, traces_sample_rate=0.1)

app = FastAPI(title="OwnerPay API", version="0.1.0")


class RoleSplit(BaseModel):
    role: str = Field(pattern="^(sales|operations|administration|finance|marketing|technical)$")
    percent: float = Field(ge=0, le=100)


class EstimateRequest(BaseModel):
    tax_year: int = Field(ge=2024, le=2026)
    location: dict  # {state:'CA', msa_code:'41860'}; refine on Day 2
    business: dict  # {entity_type:'s_corp', revenue:..., profit:..., headcount:...}
    owner: dict  # {hours_per_week:..., experience_years:...}
    role_split: list[RoleSplit]


class EstimateResponse(BaseModel):
    id: str
    low: float
    median: float
    high: float
    recommended: float
    soc_sources: list[dict] = []
    adjustments: list[dict] = []
    flags: list[dict] = []
    assumptions: list[str] = []
    memo_url: str | None = None


@app.post("/rc/estimate", response_model=EstimateResponse)
def estimate(payload: EstimateRequest):
    # Day-1 stub: return deterministic sample; replace with kernel Day-4/5
    return EstimateResponse(
        id="demo-uuid",
        low=85000,
        median=100000,
        high=115000,
        recommended=98000,
        assumptions=[f"tax_year={payload.tax_year}", "roles weighted by percent"],
        memo_url="https://api-staging.ownerpay.dev/rc/memo/demo-uuid",
    )


@app.get("/rc/memo/{id}")
def memo(id: str):
    if id != "demo-uuid":
        raise HTTPException(status_code=404, detail="Not found")
    return {"id": id, "html_url": f"https://cdn.ownerpay.dev/memos/{id}.html"}
