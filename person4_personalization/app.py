import sys
from pathlib import Path

# Ensure root workspace, person1, person2, and person4 are on sys.path
_p4_dir = Path(__file__).resolve().parent
_repo_root = _p4_dir.parent
for _p in [str(_repo_root), str(_p4_dir), str(_repo_root / "person1"), str(_repo_root / "person2")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

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



@app.get("/ready", tags=["System"])
def root_ready():
    return {
        "status": "ready",
        "service": "financeapp-unified",
        "version": "1.0.0",
    }


@app.get("/metrics", tags=["System"])
def root_metrics():
    return {
        "status": "ok",
        "service": "financeapp-unified",
        "metrics": metrics_collector.get_metrics_snapshot(),
    }


# Include legacy API routes for Phase 1-5 backward compatibility
app.include_router(legacy_router, prefix="/api")

# Include Production Person 4 API v1 routes
app.include_router(router_v1, prefix="/api/v1")

# Include Person 2 Market & Data API routes
from api.market_routes import market_router
app.include_router(market_router, prefix="/api/v1")

# Include Person 2 RAG & Citations API routes
from api.rag_routes import rag_router
app.include_router(rag_router, prefix="/api/v1")

# Include Person 1 Multi-Agent AI API routes
import importlib
import api.ai_routes
importlib.reload(api.ai_routes)
from api.ai_routes import ai_router
app.include_router(ai_router, prefix="/api/v1")

# Mount StIC UI Static Files and Dashboard Route
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

_ui_dir = Path(__file__).resolve().parent / "stic" / "ui"
if _ui_dir.exists():
    app.mount("/ui", StaticFiles(directory=str(_ui_dir)), name="ui")

    @app.get("/", tags=["StIC UI"])
    @app.get("/dashboard", tags=["StIC UI"])
    @app.get("/terminal", tags=["StIC UI"])
    def get_terminal_dashboard():
        html_path = _ui_dir / "terminal_dashboard.html"
        return FileResponse(str(html_path), media_type="text/html")

    @app.get("/api.js", include_in_schema=False)
    @app.get("/ui/api.js", include_in_schema=False)
    def get_ui_api_js():
        return FileResponse(str(_ui_dir / "api.js"), media_type="application/javascript")

    @app.get("/terminal.css", include_in_schema=False)
    @app.get("/ui/terminal.css", include_in_schema=False)
    def get_ui_terminal_css():
        return FileResponse(str(_ui_dir / "terminal.css"), media_type="text/css")


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=False)


