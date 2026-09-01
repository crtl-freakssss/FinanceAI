import time
from fastapi import Request, status
from fastapi.responses import JSONResponse
from security.config import security_config
from security.rate_limiter import rate_limiter
from app_logging.structured_logger import get_logger

logger = get_logger("security_middleware")


async def security_headers_and_rate_limit_middleware(request: Request, call_next):
    if not security_config.SECURITY_ENABLED:
        return await call_next(request)

    # 1. Request size limit check
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > security_config.MAX_REQUEST_SIZE:
                logger.warning(
                    f"Request payload size {content_length} bytes exceeded max allowed {security_config.MAX_REQUEST_SIZE} bytes",
                    extra={"path": request.url.path},
                )
                return JSONResponse(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE if hasattr(status, "HTTP_413_CONTENT_TOO_LARGE") else 413,
                    content={
                        "detail": "Request payload exceeds maximum allowed size.",
                        "max_size_bytes": security_config.MAX_REQUEST_SIZE,
                    },
                )
        except ValueError:
            pass

    # 2. Rate limiting check (using client IP / X-Forwarded-For)
    client_ip = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or request.client.host
        if request.client
        else "127.0.0.1"
    )

    # Apply rate limiter
    allowed, retry_after = rate_limiter.is_allowed(client_ip)
    if not allowed:
        logger.warning(f"Rate limit exceeded for client IP: {client_ip}", extra={"client_ip": client_ip, "path": request.url.path})
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Too many requests. Please try again later.",
                "retry_after_seconds": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )

    # 3. Process the request
    response = await call_next(request)

    # 4. Inject Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Granular Content Security Policy:
    # Allow required Swagger UI / ReDoc CDN assets strictly on documentation endpoints;
    # Keep strict default-src 'self' across all standard API and system endpoints.
    path = request.url.path
    if path in ("/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json"):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.jsdelivr.net; "
            "connect-src 'self'"
        )
    else:
        response.headers["Content-Security-Policy"] = "default-src 'self'"

    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"

    return response
