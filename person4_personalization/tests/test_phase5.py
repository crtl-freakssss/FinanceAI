import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import app
from db.database import Base, get_db, SessionLocal
from db import crud, models
from app_logging.service import log_event, get_logs

client = TestClient(app)


# ============================================================
# DB CRUD TESTS
# ============================================================

def test_db_user_crud():
    db = SessionLocal()
    try:
        user = crud.create_user(db, user_id="test_db_user_001", name="Test Database User")
        assert user.user_id == "test_db_user_001"
        assert user.name == "Test Database User"

        fetched = crud.get_user(db, "test_db_user_001")
        assert fetched is not None
        assert fetched.user_id == "test_db_user_001"
    finally:
        db.close()


def test_db_profile_crud():
    db = SessionLocal()
    try:
        profile = crud.create_or_update_profile(
            db,
            user_id="test_db_user_002",
            name="Profile Test User",
            risk_tolerance="AGGRESSIVE",
            capital=750000.0,
            preferences={"preferred_sectors": ["Technology", "Energy"]},
            constraints={"max_single_position_pct": 25.0},
        )
        assert profile.user_id == "test_db_user_002"
        assert profile.risk_tolerance == "AGGRESSIVE"
        assert profile.capital == 750000.0
        assert profile.preferences.get("preferred_sectors") == ["Technology", "Energy"]

        fetched = crud.get_profile(db, "test_db_user_002")
        assert fetched is not None
        assert fetched.risk_tolerance == "AGGRESSIVE"
    finally:
        db.close()


def test_db_portfolio_crud():
    db = SessionLocal()
    try:
        holdings = [
            {"symbol": "RELIANCE.NS", "shares": 100, "price": 2500.0, "value": 250000.0},
            {"symbol": "TCS.NS", "shares": 50, "price": 3600.0, "value": 180000.0},
        ]
        portfolio = crud.create_or_update_portfolio(
            db,
            user_id="test_db_user_003",
            total_value=500000.0,
            cash=70000.0,
            holdings=holdings,
        )
        assert portfolio.user_id == "test_db_user_003"
        assert portfolio.total_value == 500000.0
        assert len(portfolio.holdings) == 2

        fetched = crud.get_portfolio(db, "test_db_user_003")
        assert fetched is not None
        assert len(fetched.holdings) == 2
    finally:
        db.close()


def test_db_analysis_session_crud():
    db = SessionLocal()
    try:
        session = crud.create_analysis_session(
            db,
            user_id="test_db_user_004",
            symbol="INFY.NS",
            analysis_type="PERSONALIZATION",
            result_data={"risk_score": 62.5, "suitability": "SUITABLE"},
        )
        assert session.session_id.startswith("session_")
        assert session.user_id == "test_db_user_004"
        assert session.symbol == "INFY.NS"

        fetched = crud.get_analysis_session(db, session.session_id)
        assert fetched is not None
        assert fetched.session_id == session.session_id

        user_sessions = crud.list_analysis_sessions(db, user_id="test_db_user_004")
        assert len(user_sessions) >= 1
    finally:
        db.close()


def test_db_analysis_log_crud():
    db = SessionLocal()
    try:
        log = crud.create_analysis_log(
            db,
            user_id="test_db_user_005",
            message="Calculated risk score for portfolio",
            level="INFO",
            session_id="session_test_log_001",
        )
        assert log.id is not None
        assert log.message == "Calculated risk score for portfolio"

        logs = crud.get_analysis_logs(db, user_id="test_db_user_005")
        assert len(logs) >= 1
        assert logs[0].user_id == "test_db_user_005"
    finally:
        db.close()


def test_app_logging_service():
    log_entry = log_event(
        user_id="test_db_user_006",
        message="Evaluating behavioral patterns",
        level="DEBUG",
        details={"trades_analyzed": 15},
    )
    assert log_entry["user_id"] == "test_db_user_006"
    assert log_entry["message"] == "Evaluating behavioral patterns"

    logs = get_logs(user_id="test_db_user_006")
    assert len(logs) >= 1
    assert logs[0]["user_id"] == "test_db_user_006"


# ============================================================
# API PERSISTENCE TESTS
# ============================================================

def test_api_user_persistence():
    response = client.post(
        "/api/db/users",
        json={"user_id": "api_user_001", "name": "API Persisted User"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "api_user_001"
    assert body["name"] == "API Persisted User"

    get_resp = client.get("/api/db/users")
    assert get_resp.status_code == 200
    users = get_resp.json()
    assert any(u["user_id"] == "api_user_001" for u in users)


def test_api_profile_persistence():
    response = client.post(
        "/api/db/users/api_user_002/profile",
        json={
            "name": "API User 2",
            "risk_tolerance": "CONSERVATIVE",
            "risk_capacity": "LOW",
            "capital": 1000000.0,
            "preferences": {"preferred_sectors": ["FMCG"]},
            "constraints": {"max_single_position_pct": 10.0},
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "saved"

    get_resp = client.get("/api/db/users/api_user_002/profile")
    assert get_resp.status_code == 200
    profile = get_resp.json()
    assert profile["user_id"] == "api_user_002"
    assert profile["risk_tolerance"] == "CONSERVATIVE"


def test_api_portfolio_persistence():
    response = client.post(
        "/api/db/users/api_user_003/portfolio",
        json={
            "total_value": 300000.0,
            "cash": 50000.0,
            "holdings": [{"symbol": "HDFCBANK.NS", "shares": 100, "price": 1500.0, "value": 150000.0}],
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "saved"

    get_resp = client.get("/api/db/users/api_user_003/portfolio")
    assert get_resp.status_code == 200
    portfolio = get_resp.json()
    assert portfolio["user_id"] == "api_user_003"
    assert portfolio["total_value"] == 300000.0
    assert len(portfolio["holdings"]) == 1


def test_api_session_persistence():
    response = client.post(
        "/api/db/sessions",
        json={
            "user_id": "api_user_004",
            "symbol": "TCS.NS",
            "analysis_type": "PERSONALIZATION",
            "result_data": {"suitability_score": 85.0},
        },
    )
    assert response.status_code == 200
    body = response.json()
    session_id = body["session_id"]
    assert session_id

    get_resp = client.get(f"/api/db/sessions/{session_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["session_id"] == session_id

    list_resp = client.get("/api/db/users/api_user_004/sessions")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1


def test_api_log_persistence():
    response = client.post(
        "/api/db/logs",
        json={
            "user_id": "api_user_005",
            "message": "Phase 5 persistence test log message",
            "level": "INFO",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "api_user_005"
    assert body["message"] == "Phase 5 persistence test log message"

    get_resp = client.get("/api/db/users/api_user_005/logs")
    assert get_resp.status_code == 200
    logs = get_resp.json()
    assert len(logs) >= 1
    assert logs[0]["user_id"] == "api_user_005"
