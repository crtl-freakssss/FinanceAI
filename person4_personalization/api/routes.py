from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from profile.service import get_profile
from portfolio.service import get_portfolio
from portfolio.personalization_engine import (
    build_personalization_context,
)

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

from db.database import get_db, init_db
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

# Ensure database tables exist
init_db()

router = APIRouter()


# ============================================================
# Health
# ============================================================

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "phase": 1,
    }


# ============================================================
# USER PROFILE
# ============================================================

@router.get("/users/{user_id}/profile")
def get_user_profile(user_id: str):
    profile = get_profile(user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if hasattr(profile, "model_dump"):
        return profile.model_dump()

    return profile


# ============================================================
# PORTFOLIO
# ============================================================

@router.get("/users/{user_id}/portfolio")
def get_user_portfolio(user_id: str):
    portfolio = get_portfolio(user_id)

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found",
        )

    if hasattr(portfolio, "model_dump"):
        return portfolio.model_dump()

    return portfolio


# ============================================================
# PERSONALIZATION CONTEXT
# ============================================================

@router.get("/users/{user_id}/context/{symbol}")
def get_user_context(
    user_id: str,
    symbol: str,
    sector: str = Query(
        ...,
        description="Stock sector",
    ),
    market_cap: str = Query(
        "ANY",
        description="Market cap category",
    ),
    volatility: str = Query(
        "MEDIUM",
        description="Volatility category",
    ),
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
        raise HTTPException(
            status_code=404,
            detail=str(exc) or "User not found",
        )


# ============================================================
# PORTFOLIO ANALYSIS
# ============================================================

@router.get(
    "/users/{user_id}/portfolio/analysis",
    response_model=PortfolioAnalysis,
)
def portfolio_analysis(user_id: str):
    portfolio = get_portfolio(user_id)

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found",
        )

    return calculate_portfolio_analysis(portfolio)


# ============================================================
# PORTFOLIO ALLOCATION
# ============================================================

@router.get(
    "/users/{user_id}/portfolio/allocation",
    response_model=AllocationResult,
)
def portfolio_allocation(user_id: str):
    portfolio = get_portfolio(user_id)

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found",
        )

    return calculate_allocation(portfolio)


# ============================================================
# PORTFOLIO CONCENTRATION
# ============================================================

@router.get(
    "/users/{user_id}/portfolio/concentration",
    response_model=ConcentrationResult,
)
def portfolio_concentration(user_id: str):
    portfolio = get_portfolio(user_id)

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found",
        )

    return calculate_concentration(portfolio)


# ============================================================
# ADVANCED PORTFOLIO RISK
# ============================================================

@router.get(
    "/users/{user_id}/portfolio/risk/advanced",
    response_model=AdvancedRiskAssessment,
)
def advanced_portfolio_risk(user_id: str):
    user = get_profile(user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    portfolio = get_portfolio(user_id)

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found",
        )

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
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ============================================================
# PORTFOLIO RISK
# ============================================================

@router.get(
    "/users/{user_id}/portfolio/risk",
    response_model=PortfolioRiskResult,
)
def portfolio_risk(user_id: str):
    portfolio = get_portfolio(user_id)

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found",
        )

    concentration = calculate_concentration(
        portfolio
    )

    return calculate_portfolio_risk(
        portfolio,
        concentration,
    )


# ============================================================
# PORTFOLIO HEALTH
# ============================================================

@router.get(
    "/users/{user_id}/portfolio/health",
    response_model=PortfolioHealthResult,
)
def portfolio_health(user_id: str):
    portfolio = get_portfolio(user_id)

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found",
        )

    concentration = calculate_concentration(
        portfolio
    )

    risk = calculate_portfolio_risk(
        portfolio,
        concentration,
    )

    return calculate_portfolio_health(
        portfolio,
        concentration,
        risk,
    )


# ============================================================
# STOCK / SECTOR EXPOSURE
# ============================================================

@router.get(
    "/users/{user_id}/portfolio/exposure/{symbol}",
    response_model=ExposureResult,
)
def portfolio_exposure(
    user_id: str,
    symbol: str,
    sector: str = Query(default="Unknown"),
):
    user = get_profile(user_id)
    portfolio = get_portfolio(user_id)

    if not user or not portfolio:
        raise HTTPException(
            status_code=404,
            detail="User or portfolio not found",
        )

    return calculate_exposure(
        portfolio,
        user,
        symbol,
        sector,
    )


# ============================================================
# BEHAVIOUR ASSESSMENT
# ============================================================

@router.get(
    "/users/{user_id}/behavior",
    response_model=BehaviourAssessment,
)
def user_behavior(user_id: str):
    profile = get_profile(user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return analyze_behavior(user_id)


# ============================================================
# INVESTOR PROFILE
# ============================================================

@router.get(
    "/users/{user_id}/investor-profile",
    response_model=InvestorProfileAssessment,
)
def investor_profile(user_id: str):
    profile = get_profile(user_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return build_investor_profile(
        user_id,
        profile,
    )


# ============================================================
# PHASE 5: PERSISTENCE ENDPOINTS (USERS, PROFILES, PORTFOLIOS, SESSIONS, LOGS)
# ============================================================

@router.post("/db/users", response_model=UserResponse)
def create_db_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = crud.create_user(db, user_id=payload.user_id, name=payload.name)
    return UserResponse(
        user_id=user.user_id,
        name=user.name,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )


@router.get("/db/users", response_model=List[UserResponse])
def list_db_users(db: Session = Depends(get_db)):
    users = crud.list_users(db)
    return [
        UserResponse(
            user_id=u.user_id,
            name=u.name,
            created_at=u.created_at.isoformat() if u.created_at else "",
        )
        for u in users
    ]


@router.post("/db/users/{user_id}/profile")
def save_db_profile(user_id: str, payload: ProfileCreateOrUpdate, db: Session = Depends(get_db)):
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


@router.get("/db/users/{user_id}/profile")
def get_db_profile(user_id: str, db: Session = Depends(get_db)):
    profile = crud.get_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found in database")
    return {
        "user_id": profile.user_id,
        "name": profile.name,
        "risk_tolerance": profile.risk_tolerance,
        "risk_capacity": profile.risk_capacity,
        "investment_horizon": profile.investment_horizon,
        "investor_style": profile.investor_style,
        "capital": profile.capital,
        "preferences": profile.preferences,
        "constraints": profile.constraints,
    }


@router.post("/db/users/{user_id}/portfolio")
def save_db_portfolio(user_id: str, payload: PortfolioCreateOrUpdate, db: Session = Depends(get_db)):
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


@router.get("/db/users/{user_id}/portfolio")
def get_db_portfolio(user_id: str, db: Session = Depends(get_db)):
    portfolio = crud.get_portfolio(db, user_id=user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found in database")
    return {
        "user_id": portfolio.user_id,
        "total_value": portfolio.total_value,
        "cash": portfolio.cash,
        "holdings": portfolio.holdings,
    }


@router.post("/db/sessions", response_model=AnalysisSessionResponse)
def create_db_session(payload: AnalysisSessionCreate, db: Session = Depends(get_db)):
    session = crud.create_analysis_session(
        db=db,
        user_id=payload.user_id,
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


@router.get("/db/sessions/{session_id}", response_model=AnalysisSessionResponse)
def get_db_session(session_id: str, db: Session = Depends(get_db)):
    session = crud.get_analysis_session(db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Analysis session not found")
    return AnalysisSessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        symbol=session.symbol,
        analysis_type=session.analysis_type,
        result_json=session.result_json,
        created_at=session.created_at.isoformat() if session.created_at else "",
    )


@router.get("/db/users/{user_id}/sessions", response_model=List[AnalysisSessionResponse])
def list_user_db_sessions(user_id: str, db: Session = Depends(get_db)):
    sessions = crud.list_analysis_sessions(db, user_id=user_id)
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


@router.post("/db/logs", response_model=AnalysisLogResponse)
def create_db_log(payload: AnalysisLogCreate, db: Session = Depends(get_db)):
    log = crud.create_analysis_log(
        db=db,
        user_id=payload.user_id,
        message=payload.message,
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


@router.get("/db/users/{user_id}/logs", response_model=List[AnalysisLogResponse])
def list_user_db_logs(user_id: str, session_id: Optional[str] = None, db: Session = Depends(get_db)):
    logs = crud.get_analysis_logs(db, user_id=user_id, session_id=session_id)
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
