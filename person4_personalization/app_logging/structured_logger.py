from __future__ import annotations

import contextvars
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import re
import time
from typing import Any, Callable, Dict, Optional

# Context variables for correlation and tracing
request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_id", default=None)
user_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("user_id", default=None)
session_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("session_id", default=None)

LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

SENSITIVE_KEYS = {"password", "token", "secret", "api_key", "authorization", "access_token", "bearer"}


def mask_sensitive_data(data: Any) -> Any:
    """Recursively mask sensitive keys in dictionaries or strings."""
    if isinstance(data, dict):
        masked = {}
        for k, v in data.items():
            if any(sens in k.lower() for sens in SENSITIVE_KEYS):
                masked[k] = "******"
            else:
                masked[k] = mask_sensitive_data(v)
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    elif isinstance(data, str):
        # Mask authorization header values
        if "bearer " in data.lower():
            return re.sub(r"(?i)bearer\s+[a-zA-Z0-9\-\._~+/]+=*", "Bearer ******", data)
        return data
    return data


class StructuredLogFormatter(logging.Formatter):
    """Formats log records as structured dictionary / JSON for observability."""

    def format(self, record: logging.LogRecord) -> str:
        log_payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None) or request_id_ctx.get(),
            "user_id": getattr(record, "user_id", None) or user_id_ctx.get(),
            "session_id": getattr(record, "session_id", None) or session_id_ctx.get(),
        }

        # Include custom extra fields if attached
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_payload["data"] = mask_sensitive_data(record.extra_data)

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload)


_handler_initialized = False


def setup_root_logger():
    global _handler_initialized
    if _handler_initialized:
        return

    root_logger = logging.getLogger("person4_personalization")
    root_logger.setLevel(LOG_LEVEL)
    root_logger.propagate = False

    formatter = StructuredLogFormatter(datefmt="%Y-%m-%dT%H:%M:%SZ")

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Rotating File Handler (Max 5MB, keep 3 backup files)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    _handler_initialized = True


# Initialize logger handlers
setup_root_logger()


class AppLogger:
    """Application logger exposing structured logging methods."""

    def __init__(self, name: str = "person4_personalization"):
        self.logger = logging.getLogger(f"person4_personalization.{name}")

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.DEBUG, message, extra)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.INFO, message, extra)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.WARNING, message, extra)

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        self._log(logging.ERROR, message, extra, exc_info=exc_info)

    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = True):
        self._log(logging.CRITICAL, message, extra, exc_info=exc_info)

    def _log(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        if self.logger.isEnabledFor(level):
            record = self.logger.makeRecord(
                name=self.logger.name,
                level=level,
                fn="",
                lno=0,
                msg=message,
                args=(),
                exc_info=None if not exc_info else logging.sys.exc_info(),
            )
            record.request_id = request_id_ctx.get()
            record.user_id = user_id_ctx.get()
            record.session_id = session_id_ctx.get()
            if extra:
                record.extra_data = mask_sensitive_data(extra)
            self.logger.handle(record)


def get_logger(name: str = "core") -> AppLogger:
    return AppLogger(name)


def set_request_context(request_id: Optional[str] = None, user_id: Optional[str] = None, session_id: Optional[str] = None):
    if request_id:
        request_id_ctx.set(request_id)
    if user_id:
        user_id_ctx.set(user_id)
    if session_id:
        session_id_ctx.set(session_id)


def clear_request_context():
    request_id_ctx.set(None)
    user_id_ctx.set(None)
    session_id_ctx.set(None)
