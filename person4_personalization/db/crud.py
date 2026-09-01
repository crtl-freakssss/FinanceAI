import json
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from db.models import UserDB, ProfileDB, PortfolioDB, AnalysisSessionDB, AnalysisLogDB


# ============================================================
# USERS
# ============================================================

def create_user(db: Session, user_id: str, name: str = "") -> UserDB:
    existing = get_user(db, user_id)
    if existing:
        return existing
    user = UserDB(user_id=user_id, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: str) -> Optional[UserDB]:
    return db.query(UserDB).filter(UserDB.user_id == user_id).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserDB]:
    return db.query(UserDB).offset(skip).limit(limit).all()


# ============================================================
# PROFILES
# ============================================================

def create_or_update_profile(
    db: Session,
    user_id: str,
    name: str = "",
    risk_tolerance: str = "MODERATE",
    risk_capacity: str = "MEDIUM",
    investment_horizon: str = "MEDIUM_TERM",
    investor_style: str = "BALANCED",
    capital: float = 0.0,
    preferences: Optional[Dict[str, Any]] = None,
    constraints: Optional[Dict[str, Any]] = None,
) -> ProfileDB:
    user = get_user(db, user_id)
    if not user:
        user = create_user(db, user_id=user_id, name=name)

    profile = db.query(ProfileDB).filter(ProfileDB.user_id == user_id).first()
    if not profile:
        profile = ProfileDB(user_id=user_id)
        db.add(profile)

    profile.name = name or profile.name or user.name
    profile.risk_tolerance = risk_tolerance
    profile.risk_capacity = risk_capacity
    profile.investment_horizon = investment_horizon
    profile.investor_style = investor_style
    profile.capital = capital
    if preferences is not None:
        profile.preferences_json = json.dumps(preferences)
    if constraints is not None:
        profile.constraints_json = json.dumps(constraints)

    db.commit()
    db.refresh(profile)
    return profile


def get_profile(db: Session, user_id: str) -> Optional[ProfileDB]:
    return db.query(ProfileDB).filter(ProfileDB.user_id == user_id).first()


# ============================================================
# PORTFOLIOS
# ============================================================

def create_or_update_portfolio(
    db: Session,
    user_id: str,
    total_value: float = 0.0,
    cash: float = 0.0,
    holdings: Optional[List[Dict[str, Any]]] = None,
) -> PortfolioDB:
    user = get_user(db, user_id)
    if not user:
        create_user(db, user_id=user_id)

    portfolio = db.query(PortfolioDB).filter(PortfolioDB.user_id == user_id).first()
    if not portfolio:
        portfolio = PortfolioDB(user_id=user_id)
        db.add(portfolio)

    portfolio.total_value = total_value
    portfolio.cash = cash
    if holdings is not None:
        portfolio.holdings_json = json.dumps(holdings)

    db.commit()
    db.refresh(portfolio)
    return portfolio


def get_portfolio(db: Session, user_id: str) -> Optional[PortfolioDB]:
    return db.query(PortfolioDB).filter(PortfolioDB.user_id == user_id).first()


# ============================================================
# ANALYSIS SESSIONS
# ============================================================

def create_analysis_session(
    db: Session,
    user_id: str,
    symbol: Optional[str] = None,
    analysis_type: str = "PERSONALIZATION",
    result_data: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
) -> AnalysisSessionDB:
    user = get_user(db, user_id)
    if not user:
        create_user(db, user_id=user_id)

    sid = session_id or f"session_{uuid.uuid4().hex[:12]}"
    session = AnalysisSessionDB(
        session_id=sid,
        user_id=user_id,
        symbol=symbol,
        analysis_type=analysis_type,
        result_json=json.dumps(result_data or {}),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_analysis_session(db: Session, session_id: str) -> Optional[AnalysisSessionDB]:
    return db.query(AnalysisSessionDB).filter(AnalysisSessionDB.session_id == session_id).first()


def list_analysis_sessions(db: Session, user_id: Optional[str] = None, limit: int = 50) -> List[AnalysisSessionDB]:
    query = db.query(AnalysisSessionDB)
    if user_id:
        query = query.filter(AnalysisSessionDB.user_id == user_id)
    return query.order_by(AnalysisSessionDB.created_at.desc()).limit(limit).all()


# ============================================================
# ANALYSIS LOGS
# ============================================================

def create_analysis_log(
    db: Session,
    user_id: str,
    message: str,
    level: str = "INFO",
    session_id: Optional[str] = None,
    agent_name: str = "person4_personalization",
    details: Optional[Dict[str, Any]] = None,
) -> AnalysisLogDB:
    user = get_user(db, user_id)
    if not user:
        create_user(db, user_id=user_id)

    log = AnalysisLogDB(
        user_id=user_id,
        session_id=session_id,
        level=level,
        agent_name=agent_name,
        message=message,
        details_json=json.dumps(details or {}),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_analysis_logs(
    db: Session,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = 100,
) -> List[AnalysisLogDB]:
    query = db.query(AnalysisLogDB)
    if user_id:
        query = query.filter(AnalysisLogDB.user_id == user_id)
    if session_id:
        query = query.filter(AnalysisLogDB.session_id == session_id)
    return query.order_by(AnalysisLogDB.timestamp.desc()).limit(limit).all()
