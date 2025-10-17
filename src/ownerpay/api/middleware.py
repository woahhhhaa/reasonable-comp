import json
import logging
import time
import uuid
import os
import hashlib

from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger("api")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        req_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        request.state.request_id = req_id
        response = await call_next(request)
        response.headers["x-request-id"] = req_id
        return response


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)
        # Hash caller IP (if present) to avoid logging raw PII
        xff = request.headers.get("x-forwarded-for", "")
        client_ip = xff.split(",")[0].strip() if xff else ""
        salt = os.getenv("ACCESS_LOG_IP_SALT", "")
        ip_hash = None
        if salt and client_ip:
            ip_hash = hashlib.sha256((salt + client_ip).encode("utf-8")).hexdigest()[:12]
        # Detect whether rate limiting is enabled (set at app startup)
        rl_enabled = bool(getattr(request.app.state, "rate_limit_enabled", False))
        payload = {
            "ts": int(start * 1000),
            "level": "info",
            "request_id": getattr(request.state, "request_id", None),
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "ua": request.headers.get("user-agent"),
            "ip_hash": ip_hash,
            "rl_enabled": rl_enabled,
        }
        logger.info(json.dumps(payload))
        return response


