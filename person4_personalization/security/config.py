import os
from typing import List


class SecurityConfig:
    SECURITY_ENABLED: bool = os.getenv("SECURITY_ENABLED", "true").lower() in ("true", "1", "yes")
    
    # CORS Allowed Origins
    _origins_str: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000",
    )
    ALLOWED_ORIGINS: List[str] = [o.strip() for o in _origins_str.split(",") if o.strip()]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() in ("true", "1", "yes")
    RATE_LIMIT: int = int(os.getenv("RATE_LIMIT", "120"))  # Max requests per window
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # Window in seconds

    # Maximum payload size in bytes (1MB default)
    MAX_REQUEST_SIZE: int = int(os.getenv("MAX_REQUEST_SIZE", str(1024 * 1024)))

    # Log level
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()


security_config = SecurityConfig()
