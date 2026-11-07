import json
import logging
import os
import sys
import time
import uuid
from datetime import UTC, datetime

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

SERVICE = os.getenv("SERVICE_NAME", "unknown")
VERSION = os.getenv("APP_VERSION", "v1.0.0")

logger = logging.getLogger("shop")

REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "path", "status"],
)
LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["service", "method", "path"],
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "service": SERVICE,
            "version": VERSION,
            "msg": record.getMessage(),
        }
        payload.update(getattr(record, "fields", {}))
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def log(level: int, msg: str, **fields) -> None:
    logger.log(level, msg, extra={"fields": fields})


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False


def create_app(lifespan=None) -> FastAPI:
    setup_logging()
    app = FastAPI(title=SERVICE, lifespan=lifespan)

    @app.middleware("http")
    async def observe(request: Request, call_next):
        path = request.url.path
        if path in ("/metrics", "/health") or path.startswith("/admin"):
            return await call_next(request)
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        request.state.request_id = request_id
        start = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["x-request-id"] = request_id
            return response
        except Exception:
            logger.error(
                "unhandled exception",
                extra={"fields": {"request_id": request_id, "path": path}},
                exc_info=True,
            )
            raise
        finally:
            elapsed = time.perf_counter() - start
            REQUESTS.labels(SERVICE, request.method, path, str(status)).inc()
            LATENCY.labels(SERVICE, request.method, path).observe(elapsed)
            log(
                logging.INFO,
                "request",
                request_id=request_id,
                method=request.method,
                path=path,
                status=status,
                duration_ms=round(elapsed * 1000, 1),
            )

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "service": SERVICE, "version": VERSION}

    @app.get("/metrics")
    def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    return app
