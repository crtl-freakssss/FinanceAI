import time
from typing import Any, Callable, Dict, List, Optional
from db.database import SessionLocal
from db.crud import create_analysis_log, get_analysis_logs
from app_logging.structured_logger import get_logger, mask_sensitive_data
from app_logging.metrics import metrics_collector

logger = get_logger("service")


def log_event(
    user_id: str,
    message: str,
    level: str = "INFO",
    session_id: Optional[str] = None,
    agent_name: str = "person4_personalization",
    details: Optional[Dict[str, Any]] = None,
    db=None,
) -> dict:
    masked_details = mask_sensitive_data(details or {})
    # Write to structured application log
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(
        message,
        extra={
            "user_id": user_id,
            "session_id": session_id,
            "agent_name": agent_name,
            "details": masked_details,
        },
    )

    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        log_db = create_analysis_log(
            db=db,
            user_id=user_id,
            message=message,
            level=level.upper(),
            session_id=session_id,
            agent_name=agent_name,
            details=masked_details,
        )
        return {
            "id": log_db.id,
            "user_id": log_db.user_id,
            "session_id": log_db.session_id,
            "level": log_db.level,
            "agent_name": log_db.agent_name,
            "message": log_db.message,
            "timestamp": log_db.timestamp.isoformat() if log_db.timestamp else "",
        }
    finally:
        if own_session:
            db.close()


def get_logs(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = 100,
    db=None,
) -> List[dict]:
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        logs = get_analysis_logs(db=db, user_id=user_id, session_id=session_id, limit=limit)
        return [
            {
                "id": log.id,
                "user_id": log.user_id,
                "session_id": log.session_id,
                "level": log.level,
                "agent_name": log.agent_name,
                "message": log.message,
                "timestamp": log.timestamp.isoformat() if log.timestamp else "",
            }
            for log in logs
        ]
    finally:
        if own_session:
            db.close()


def trace_agent_execution(
    agent_name: str,
    user_id: str,
    action: str,
    session_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
):
    """Context manager or helper for logging agent execution start/end and metrics."""
    metrics_collector.record_agent_run(agent_name)
    start_time = time.perf_counter()

    log_event(
        user_id=user_id,
        message=f"Agent '{agent_name}' started action: {action}",
        level="INFO",
        session_id=session_id,
        agent_name=agent_name,
        details=details,
    )

    class _TraceContext:
        def finish(self, success: bool = True, error_msg: Optional[str] = None):
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            level = "INFO" if success else "ERROR"
            msg = (
                f"Agent '{agent_name}' completed action '{action}' in {duration_ms}ms"
                if success
                else f"Agent '{agent_name}' failed action '{action}' in {duration_ms}ms: {error_msg}"
            )
            log_event(
                user_id=user_id,
                message=msg,
                level=level,
                session_id=session_id,
                agent_name=agent_name,
                details={"duration_ms": duration_ms, "success": success, "error": error_msg},
            )

    return _TraceContext()
