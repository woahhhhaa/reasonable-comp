import os
from types import SimpleNamespace

import sentry_sdk
from fastapi import Depends, FastAPI
import logging
from pydantic import BaseModel, Field, NonNegativeFloat, NonNegativeInt, conint, constr

sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(dsn=sentry_dsn, traces_sample_rate=0.1)

app = FastAPI(title="OwnerPay API", version="0.1.0")


class RoleSplit(BaseModel):
    role: str = Field(pattern="^(sales|operations|administration|finance|marketing|technical)$")
    percent: float = Field(ge=0, le=100)


class Location(BaseModel):
    state: constr(pattern=r"^[A-Z]{2}$")
    msa_code: str = Field(pattern=r"^\d{5}$")


class Business(BaseModel):
    entity_type: constr(pattern=r"^(s_corp)$")
    revenue: NonNegativeFloat
    profit: float
    headcount: NonNegativeInt


class Owner(BaseModel):
    hours_per_week: conint(ge=0, le=80)
    experience_years: conint(ge=0, le=60)


class EstimateRequest(BaseModel):
    tax_year: int = Field(ge=2024, le=2026)
    location: Location
    business: Business
    owner: Owner
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


class MemoResponse(BaseModel):
    id: str
    html_url: str
    pdf_url: str
# Structured logging: configure root to emit JSON lines (middleware formats)
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Middleware for request id and access logs
from src.ownerpay.api.middleware import AccessLogMiddleware, RequestIdMiddleware

app.add_middleware(RequestIdMiddleware)
app.add_middleware(AccessLogMiddleware)

# Conditional rate limiting (enabled when RATE_LIMIT_REDIS_URL is present)
import os as _os
try:
    import redis.asyncio as _redis
    from fastapi_limiter import FastAPILimiter
    from fastapi_limiter.depends import RateLimiter
except Exception:  # pragma: no cover - optional in local/dev
    _redis = None
    FastAPILimiter = None
    RateLimiter = None


@app.on_event("startup")
async def _init_rate_limiter():
    if _redis is None or FastAPILimiter is None:
        # Expose state for logs
        app.state.rate_limit_enabled = False
        return
    url = _os.getenv("RATE_LIMIT_REDIS_URL", "")
    if not url:
        app.state.rate_limit_enabled = False
        return
    # Upstash typically requires SSL (rediss://) - the URL scheme handles SSL
    redis_client = _redis.from_url(url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_client)
    app.state.rate_limit_enabled = True



# Health and readiness endpoints
@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}


@app.get("/readyz", include_in_schema=False)
def readyz():
    # Optionally ping dependencies here; for now return ready
    return {"status": "ready"}


_estimate_dependencies = []
if 'RateLimiter' in globals() and RateLimiter is not None:
    _estimate_dependencies = [Depends(RateLimiter(times=10, seconds=60))]


@app.post("/rc/estimate", response_model=EstimateResponse, dependencies=_estimate_dependencies)
def estimate(payload: EstimateRequest):
    # Import locally to avoid import-time side effects during app startup
    from src.ownerpay.core.kernel import compute_estimate
    from src.ownerpay.api.util import canonicalize_estimate_payload, compute_request_id

    # Convert Pydantic models to the dict-based structure expected by the kernel
    normalized = {
        "tax_year": payload.tax_year,
        "location": payload.location.model_dump(),
        "business": payload.business.model_dump(),
        "owner": payload.owner.model_dump(),
        "role_split": [rs.model_dump() for rs in payload.role_split],
    }
    kernel_payload = SimpleNamespace(
        tax_year=normalized["tax_year"],
        location=normalized["location"],
        business=normalized["business"],
        owner=normalized["owner"],
        role_split=normalized["role_split"],
    )

    kr = compute_estimate(kernel_payload)

    # Deterministic id over canonicalized payload
    rid = compute_request_id(canonicalize_estimate_payload(normalized))

    return EstimateResponse(
        id=rid,
        low=kr.low,
        median=kr.median,
        high=kr.high,
        recommended=kr.recommended,
        soc_sources=kr.soc_sources,
        adjustments=kr.adjustments,
        flags=kr.flags,
        assumptions=kr.assumptions,
        memo_url=f"/rc/memo/{rid}",
    )


_memo_dependencies = []
if 'RateLimiter' in globals() and RateLimiter is not None:
    _memo_dependencies = [Depends(RateLimiter(times=60, seconds=60))]


@app.get("/rc/memo/{id}", response_model=MemoResponse, dependencies=_memo_dependencies)
def memo(id: str):
    from src.ownerpay.api.signing import sign_url

    cdn_base = os.getenv("MEMO_CDN_BASE", "https://cdn.ownerpay.dev")
    ttl = int(os.getenv("MEMO_TTL_SECONDS", "600"))
    secret = os.getenv("MEMO_SIGNING_SECRET", "")

    html_path = f"/memos/{id}.html"
    pdf_path = f"/memos/{id}.pdf"

    if secret:
        html_url = sign_url(cdn_base, html_path, ttl_seconds=ttl, secret=secret)
        pdf_url = sign_url(cdn_base, pdf_path, ttl_seconds=ttl, secret=secret)
    else:
        # Dev fallback: return unsigned URLs when no secret is configured
        html_url = f"{cdn_base}{html_path}"
        pdf_url = f"{cdn_base}{pdf_path}"

    return {"id": id, "html_url": html_url, "pdf_url": pdf_url}
