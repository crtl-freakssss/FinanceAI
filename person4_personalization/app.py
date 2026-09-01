import time
import uuid
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.routes import router as legacy_router
from api.v1_routes import router_v1
from db.database import init_db
from app_logging.structured_logger import (
    get_logger,
    set_request_context,
    clear_request_context,
)
from app_logging.metrics import metrics_collector
from security.config import security_config
from security.middleware import security_headers_and_rate_limit_middleware

logger = get_logger("http")

# Initialize database tables
init_db()

app = FastAPI(
    title="Finance Personalization & Portfolio Intelligence API",
    version="1.0.0",
    description="Production-grade API for Person 4 Personalization, Risk Engine, Behavioral Analytics, and Data Persistence.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware for secure cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register Security Headers and Rate Limiting Middleware
app.middleware("http")(security_headers_and_rate_limit_middleware)


# ============================================================
# OBSERVABILITY MIDDLEWARE (CORRELATION ID, TIMING, LOGGING)
# ============================================================

@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
    set_request_context(request_id=request_id)

    start_time = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Inject correlation ID and latency headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

        # Record metrics
        metrics_collector.record_request(
            endpoint=request.url.path,
            status_code=status_code,
            duration_ms=duration_ms,
        )

        # Structured request logging
        logger.info(
            f"{request.method} {request.url.path} -> {status_code} ({duration_ms}ms)",
            extra={
                "http_method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

    except Exception as exc:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        metrics_collector.record_request(
            endpoint=request.url.path,
            status_code=500,
            duration_ms=duration_ms,
        )
        logger.error(
            f"Unhandled exception during {request.method} {request.url.path}: {str(exc)}",
            extra={
                "http_method": request.method,
                "path": request.url.path,
                "duration_ms": duration_ms,
            },
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An internal server error occurred.",
                "request_id": request_id,
            },
            headers={
                "X-Request-ID": request_id,
                "X-Process-Time": f"{duration_ms:.2f}ms",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
            },
        )
    finally:
        clear_request_context()


# ============================================================
# SYSTEM HEALTH & METRICS ENDPOINTS
# ============================================================

@app.get("/health", tags=["System"])
def root_health():
    return {
        "status": "ok",
        "service": "finance-personalization",
        "version": "1.0.0",
    }


@app.get("/metrics", tags=["System"])
def root_metrics():
    return {
        "status": "ok",
        "service": "finance-personalization",
        "metrics": metrics_collector.get_metrics_snapshot(),
    }


# Include legacy API routes for complete Phase 1-5 backward compatibility
app.include_router(legacy_router, prefix="/api")

# Include Production API v1 routes
app.include_router(router_v1, prefix="/api/v1")
