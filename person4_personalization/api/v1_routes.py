import re
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from profile.service import get_profile
from portfolio.service import get_portfolio
from portfolio.personalization_engine import build_personalization_context

from models.portfolio_analysis import (
    AllocationResult,
    ConcentrationResult,
    ExposureResult,
    PortfolioAnalysis,
    PortfolioHealthResult,
    PortfolioRiskResult,
)
from portfolio.analytics import (
    calculate_allocation,
    calculate_concentration,
    calculate_exposure,
    calculate_portfolio_analysis,
    calculate_portfolio_health,
    calculate_portfolio_risk,
)

from models.risk_engine import AdvancedRiskAssessment
from portfolio.risk_engine import calculate_advanced_risk

from behavior.analyzer import analyze_behavior
from profile.investor_profiler import build_investor_profile
from models.behavior import (
    BehaviourAssessment,
    InvestorProfileAssessment,
)

from db.database import get_db
from db import crud
from models.persistence import (
    UserCreate,
    UserResponse,
    ProfileCreateOrUpdate,
    PortfolioCreateOrUpdate,
    AnalysisSessionCreate,
    AnalysisSessionResponse,
    AnalysisLogCreate,
    AnalysisLogResponse,
)

router_v1 = APIRouter(tags=["Production API v1"])


# ============================================================
# SYSTEM HEALTH & READINESS
# ============================================================

@router_v1.get("/health", summary="Service Health Check")
def health_v1():
    """Returns the operational status of the service."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "service": "finance-personalization",
    }


@router_v1.get("/readiness", summary="Database Readiness Check")
def readiness_v1(db: Session = Depends(get_db)):
    """Verifies that the database connection is alive and ready."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
            "service": "finance-personalization",
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failure: {str(exc)}",
        )


@router_v1.get("/metrics", summary="Service Observability Metrics")
def metrics_v1():
    """Returns application runtime metrics and performance data."""
    from app_logging.metrics import metrics_collector
    return {
        "status": "ok",
        "service": "finance-personalization",
        "metrics": metrics_collector.get_metrics_snapshot(),
    }


# ============================================================
# USERS & PROFILES
# ============================================================

@router_v1.get("/users/{user_id}/profile", summary="Get User Profile")
def get_user_profile_v1(
    user_id: str = Path(..., min_length=1, max_length=100, description="User identifier"),
):
    profile = get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    if hasattr(profile, "model_dump"):
        return profile.model_dump()
    return profile


@router_v1.get("/users/{user_id}/portfolio", summary="Get User Portfolio")
def get_user_portfolio_v1(
    user_id: str = Path(..., min_length=1, max_length=100, description="User identifier"),
):
    portfolio = get_portfolio(user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail=f"Portfolio for user '{user_id}' not found")
    if hasattr(portfolio, "model_dump"):
        return portfolio.model_dump()
    return portfolio


# ============================================================
# PERSONALIZATION CONTEXT
# ============================================================

@router_v1.get("/users/{user_id}/context/{symbol}", summary="Evaluate Personalization Context")
def get_user_context_v1(
    user_id: str = Path(..., min_length=1, max_length=100),
    symbol: str = Path(..., min_length=1, max_length=30, pattern=r"^[A-Za-z0-9\.\-\_]+$"),
    sector: str = Query(..., min_length=1, max_length=100, description="Stock sector"),
    market_cap: str = Query("ANY", pattern=r"^(LARGE|MID|SMALL|MICRO|ANY)$", description="Market cap bucket"),
    volatility: str = Query("MEDIUM", pattern=r"^(LOW|MEDIUM|HIGH)$", description="Volatility category"),
):
    try:
        context = build_personalization_context(
            user_id=user_id,
            symbol=symbol,
            sector=sector,
            market_cap=market_cap,
            volatility=volatility,
        )
        if hasattr(context, "model_dump"):
            return context.model_dump()
        return context
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc) or f"User '{user_id}' not found")


# ============================================================
# PORTFOLIO INTELLIGENCE & ANALYTICS
# ============================================================

@router_v1.get("/users/{user_id}/portfolio/analysis", response_model=PortfolioAnalysis, summary="Complete Portfolio Analysis")
def portfolio_analysis_v1(user_id: str = Path(..., min_length=1, max_length=100)):
    portfolio = get_portfolio(user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail=f"Portfolio for user '{user_id}' not found")
    return calculate_portfolio_analysis(portfolio)


@router_v1.get("/users/{user_id}/portfolio/allocation", response_model=AllocationResult, summary="Portfolio Allocation Breakdown")
def portfolio_allocation_v1(user_id: str = Path(..., min_length=1, max_length=100)):
    portfolio = get_portfolio(user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail=f"Portfolio for user '{user_id}' not found")
    return calculate_allocation(portfolio)


@router_v1.get("/users/{user_id}/portfolio/concentration", response_model=ConcentrationResult, summary="Portfolio Concentration Analysis")
def portfolio_concentration_v1(user_id: str = Path(..., min_length=1, max_length=100)):
    portfolio = get_portfolio(user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail=f"Portfolio for user '{user_id}' not found")
    return calculate_concentration(portfolio)


@router_v1.get("/users/{user_id}/portfolio/risk", response_model=PortfolioRiskResult, summary="Standard Portfolio Risk")
def portfolio_risk_v1(user_id: str = Path(..., min_length=1, max_length=100)):
    portfolio = get_portfolio(user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail=f"Portfolio for user '{user_id}' not found")
    concentration = calculate_concentration(portfolio)
    return calculate_portfolio_risk(portfolio, concentration)


@router_v1.get("/users/{user_id}/portfolio/risk/advanced", response_model=AdvancedRiskAssessment, summary="Advanced Quantitative Risk Assessment")
def advanced_portfolio_risk_v1(user_id: str = Path(..., min_length=1, max_length=100)):
    user = get_profile(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

    portfolio = get_portfolio(user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail=f"Portfolio for user '{user_id}' not found")

    try:
        allocation = calculate_allocation(portfolio)
        concentration = calculate_concentration(portfolio)
        return calculate_advanced_risk(
            portfolio=portfolio,
            user_profile=user,
            concentration=concentration,
            allocation=allocation,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router_v1.get("/users/{user_id}/portfolio/health", response_model=PortfolioHealthResult, summary="Portfolio Overall Health")
def portfolio_health_v1(user_id: str = Path(..., min_length=1, max_length=100)):
    portfolio = get_portfolio(user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail=f"Portfolio for user '{user_id}' not found")

    concentration = calculate_concentration(portfolio)
    risk = calculate_portfolio_risk(portfolio, concentration)
    return calculate_portfolio_health(portfolio, concentration, risk)


@router_v1.get("/users/{user_id}/portfolio/exposure/{symbol}", response_model=ExposureResult, summary="Stock & Sector Exposure")
def portfolio_exposure_v1(
    user_id: str = Path(..., min_length=1, max_length=100),
    symbol: str = Path(..., min_length=1, max_length=30),
    sector: str = Query(default="Unknown", min_length=1, max_length=100),
):
    user = get_profile(user_id)
    portfolio = get_portfolio(user_id)
    if not user or not portfolio:
        raise HTTPException(status_code=404, detail=f"User or portfolio for '{user_id}' not found")

    return calculate_exposure(portfolio, user, symbol, sector)


# ============================================================
# BEHAVIOR & INVESTOR PROFILING
# ============================================================

@router_v1.get("/users/{user_id}/behavior", response_model=BehaviourAssessment, summary="Behavioral Pattern Assessment")
def user_behavior_v1(user_id: str = Path(..., min_length=1, max_length=100)):
    profile = get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    return analyze_behavior(user_id)


@router_v1.get("/users/{user_id}/investor-profile", response_model=InvestorProfileAssessment, summary="Investor Profile & Alignment Assessment")
def investor_profile_v1(user_id: str = Path(..., min_length=1, max_length=100)):
    profile = get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    return build_investor_profile(user_id, profile)


# ============================================================
# PERSISTENCE & PAGINATION
# ============================================================

@router_v1.post("/db/users", response_model=UserResponse, summary="Create User Record")
def create_user_v1(payload: UserCreate, db: Session = Depends(get_db)):
    if not payload.user_id.strip():
        raise HTTPException(status_code=400, detail="user_id cannot be empty")
    user = crud.create_user(db, user_id=payload.user_id.strip(), name=payload.name.strip())
    return UserResponse(
        user_id=user.user_id,
        name=user.name,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )


@router_v1.get("/db/users", response_model=List[UserResponse], summary="Paginated User List")
def list_users_v1(
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(20, ge=1, le=100, description="Maximum items to return"),
    db: Session = Depends(get_db),
):
    users = crud.list_users(db, skip=skip, limit=limit)
    return [
        UserResponse(
            user_id=u.user_id,
            name=u.name,
            created_at=u.created_at.isoformat() if u.created_at else "",
        )
        for u in users
    ]


@router_v1.post("/db/users/{user_id}/profile", summary="Persist or Update Profile in DB")
def save_db_profile_v1(
    user_id: str = Path(..., min_length=1, max_length=100),
    payload: ProfileCreateOrUpdate = ...,
    db: Session = Depends(get_db),
):
    profile = crud.create_or_update_profile(
        db=db,
        user_id=user_id,
        name=payload.name or "",
        risk_tolerance=payload.risk_tolerance,
        risk_capacity=payload.risk_capacity,
        investment_horizon=payload.investment_horizon,
        investor_style=payload.investor_style,
        capital=payload.capital,
        preferences=payload.preferences,
        constraints=payload.constraints,
    )
    return {
        "status": "saved",
        "user_id": profile.user_id,
        "risk_tolerance": profile.risk_tolerance,
        "capital": profile.capital,
    }


@router_v1.post("/db/users/{user_id}/portfolio", summary="Persist or Update Portfolio in DB")
def save_db_portfolio_v1(
    user_id: str = Path(..., min_length=1, max_length=100),
    payload: PortfolioCreateOrUpdate = ...,
    db: Session = Depends(get_db),
):
    portfolio = crud.create_or_update_portfolio(
        db=db,
        user_id=user_id,
        total_value=payload.total_value,
        cash=payload.cash,
        holdings=payload.holdings,
    )
    return {
        "status": "saved",
        "user_id": portfolio.user_id,
        "total_value": portfolio.total_value,
        "cash": portfolio.cash,
        "holdings_count": len(portfolio.holdings),
    }


@router_v1.post("/db/sessions", response_model=AnalysisSessionResponse, summary="Persist Analysis Session")
def create_session_v1(payload: AnalysisSessionCreate, db: Session = Depends(get_db)):
    if not payload.user_id.strip():
        raise HTTPException(status_code=400, detail="user_id cannot be empty")
    session = crud.create_analysis_session(
        db=db,
        user_id=payload.user_id.strip(),
        symbol=payload.symbol,
        analysis_type=payload.analysis_type,
        result_data=payload.result_data,
    )
    return AnalysisSessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        symbol=session.symbol,
        analysis_type=session.analysis_type,
        result_json=session.result_json,
        created_at=session.created_at.isoformat() if session.created_at else "",
    )


@router_v1.get("/db/users/{user_id}/sessions", response_model=List[AnalysisSessionResponse], summary="List User Sessions")
def list_user_sessions_v1(
    user_id: str = Path(..., min_length=1, max_length=100),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    sessions = crud.list_analysis_sessions(db, user_id=user_id, limit=limit)
    return [
        AnalysisSessionResponse(
            session_id=s.session_id,
            user_id=s.user_id,
            symbol=s.symbol,
            analysis_type=s.analysis_type,
            result_json=s.result_json,
            created_at=s.created_at.isoformat() if s.created_at else "",
        )
        for s in sessions
    ]


@router_v1.post("/db/logs", response_model=AnalysisLogResponse, summary="Append Analysis Log")
def create_log_v1(payload: AnalysisLogCreate, db: Session = Depends(get_db)):
    if not payload.user_id.strip() or not payload.message.strip():
        raise HTTPException(status_code=400, detail="user_id and message are required")
    log = crud.create_analysis_log(
        db=db,
        user_id=payload.user_id.strip(),
        message=payload.message.strip(),
        level=payload.level,
        session_id=payload.session_id,
        agent_name=payload.agent_name,
        details=payload.details,
    )
    return AnalysisLogResponse(
        id=log.id,
        user_id=log.user_id,
        session_id=log.session_id,
        level=log.level,
        agent_name=log.agent_name,
        message=log.message,
        timestamp=log.timestamp.isoformat() if log.timestamp else "",
    )


@router_v1.get("/db/users/{user_id}/logs", response_model=List[AnalysisLogResponse], summary="Retrieve User Analysis Logs")
def list_user_logs_v1(
    user_id: str = Path(..., min_length=1, max_length=100),
    session_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    logs = crud.get_analysis_logs(db, user_id=user_id, session_id=session_id, limit=limit)
    return [
        AnalysisLogResponse(
            id=l.id,
            user_id=l.user_id,
            session_id=l.session_id,
            level=l.level,
            agent_name=l.agent_name,
            message=l.message,
            timestamp=l.timestamp.isoformat() if l.timestamp else "",
        )
        for l in logs
    ]
