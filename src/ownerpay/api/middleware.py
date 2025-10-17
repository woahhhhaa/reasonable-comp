import json
import logging
import time
import uuid

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
        payload = {
            "ts": int(start * 1000),
            "level": "info",
            "request_id": getattr(request.state, "request_id", None),
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "ua": request.headers.get("user-agent"),
            "ip": request.headers.get("x-forwarded-for"),
        }
        logger.info(json.dumps(payload))
        return response


