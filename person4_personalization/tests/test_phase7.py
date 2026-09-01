import json
import logging
from fastapi.testclient import TestClient
from app import app
from app_logging.structured_logger import (
    get_logger,
    mask_sensitive_data,
    set_request_context,
    clear_request_context,
    LOG_FILE,
)
from app_logging.service import log_event, get_logs, trace_agent_execution
from app_logging.metrics import metrics_collector

client = TestClient(app)


# ============================================================
# LOGGING INITIALIZATION & LOG LEVELS
# ============================================================

def test_logger_initialization_and_levels():
    logger = get_logger("unit_test")
    assert logger is not None
    # Verify standard methods do not raise exceptions
    logger.debug("Test debug message", extra={"key": "val"})
    logger.info("Test info message", extra={"user_id": "test_user"})
    logger.warning("Test warning message")
    logger.error("Test error message")
    logger.critical("Test critical message")


def test_sensitive_data_masking():
    sensitive_payload = {
        "user_id": "u123",
        "password": "SuperSecretPassword!",
        "token": "secret_jwt_token_here",
        "api_key": "sk-1234567890",
        "nested": {
            "authorization": "Bearer my_secret_token",
            "safe_field": "public_data",
        },
    }
    masked = mask_sensitive_data(sensitive_payload)
    assert masked["password"] == "******"
    assert masked["token"] == "******"
    assert masked["api_key"] == "******"
    assert masked["nested"]["authorization"] == "******"
    assert masked["nested"]["safe_field"] == "public_data"
    assert masked["user_id"] == "u123"


# ============================================================
# REQUEST ID & LATENCY TRACKING HEADERS
# ============================================================

def test_request_id_generated_and_latency_header():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time" in response.headers
    assert response.headers["X-Request-ID"].startswith("req_")
    assert response.headers["X-Process-Time"].endswith("ms")


def test_request_id_propagation_from_client():
    custom_request_id = "custom-trace-uuid-12345"
    response = client.get(
        "/api/v1/health",
        headers={"X-Request-ID": custom_request_id},
    )
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_request_id


# ============================================================
# OBSERVABILITY & METRICS ENDPOINTS
# ============================================================

def test_root_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "metrics" in body
    metrics = body["metrics"]
    assert "uptime_seconds" in metrics
    assert "total_requests" in metrics
    assert "status_codes" in metrics
    assert "endpoint_latencies" in metrics
    assert metrics["total_requests"] > 0


def test_v1_metrics_endpoint():
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "metrics" in body


# ============================================================
# AGENT EXECUTION TRACING & OBSERVABILITY
# ============================================================

def test_agent_execution_tracing():
    tracer = trace_agent_execution(
        agent_name="risk_evaluator_agent",
        user_id="moderate_001",
        action="evaluate_portfolio_risk",
        details={"symbol": "RELIANCE.NS"},
    )
    # Simulate agent completion
    tracer.finish(success=True)

    metrics = metrics_collector.get_metrics_snapshot()
    assert "risk_evaluator_agent" in metrics["agent_runs"]
    assert metrics["agent_runs"]["risk_evaluator_agent"] >= 1

    logs = get_logs(user_id="moderate_001")
    agent_logs = [l for l in logs if l.get("agent_name") == "risk_evaluator_agent"]
    assert len(agent_logs) >= 1


def test_agent_execution_tracing_failure():
    tracer = trace_agent_execution(
        agent_name="portfolio_agent",
        user_id="aggressive_001",
        action="execute_rebalance",
    )
    tracer.finish(success=False, error_msg="Constraint breach on max position")

    logs = get_logs(user_id="aggressive_001")
    error_logs = [l for l in logs if l.get("level") == "ERROR"]
    assert len(error_logs) >= 1


# ============================================================
# ERROR HANDLING & EXCEPTION LOGGING WITHOUT LEAKAGE
# ============================================================

def test_error_response_does_not_leak_internals():
    response = client.get("/api/v1/users/does_not_exist_9999/profile")
    assert response.status_code == 404
    body = response.json()
    assert "detail" in body
    # Ensure raw tracebacks are not in the response
    assert "Traceback" not in str(body)
    assert "File \"" not in str(body)


# ============================================================
# VERIFY HEALTH & READINESS REMAIN OPERATIONAL
# ============================================================

def test_health_and_readiness_operational():
    h_resp = client.get("/health")
    assert h_resp.status_code == 200
    assert h_resp.json()["status"] == "ok"

    v1_h = client.get("/api/v1/health")
    assert v1_h.status_code == 200
    assert v1_h.json()["status"] == "ok"

    r_resp = client.get("/api/v1/readiness")
    assert r_resp.status_code == 200
    assert r_resp.json()["status"] == "ready"
    assert r_resp.json()["database"] == "connected"
