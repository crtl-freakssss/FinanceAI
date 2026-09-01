from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from db.database import Base


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("ProfileDB", back_populates="user", uselist=False, cascade="all, delete-orphan")
    portfolio = relationship("PortfolioDB", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("AnalysisSessionDB", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("AnalysisLogDB", back_populates="user", cascade="all, delete-orphan")


class ProfileDB(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("users.user_id"), unique=True, nullable=False, index=True)
    name = Column(String(200), default="")
    risk_tolerance = Column(String(50), default="MODERATE")
    risk_capacity = Column(String(50), default="MEDIUM")
    investment_horizon = Column(String(50), default="MEDIUM_TERM")
    investor_style = Column(String(50), default="BALANCED")
    capital = Column(Float, default=0.0)
    preferences_json = Column(Text, default="{}")
    constraints_json = Column(Text, default="{}")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserDB", back_populates="profile")

    @property
    def preferences(self):
        return json.loads(self.preferences_json or "{}")

    @preferences.setter
    def preferences(self, val):
        self.preferences_json = json.dumps(val if isinstance(val, dict) else (val.dict() if hasattr(val, "dict") else {}))

    @property
    def constraints(self):
        return json.loads(self.constraints_json or "{}")

    @constraints.setter
    def constraints(self, val):
        self.constraints_json = json.dumps(val if isinstance(val, dict) else (val.dict() if hasattr(val, "dict") else {}))


class PortfolioDB(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("users.user_id"), unique=True, nullable=False, index=True)
    total_value = Column(Float, default=0.0)
    cash = Column(Float, default=0.0)
    holdings_json = Column(Text, default="[]")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserDB", back_populates="portfolio")

    @property
    def holdings(self):
        return json.loads(self.holdings_json or "[]")

    @holdings.setter
    def holdings(self, val):
        self.holdings_json = json.dumps(val if isinstance(val, list) else [])


class AnalysisSessionDB(Base):
    __tablename__ = "analysis_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(100), ForeignKey("users.user_id"), nullable=False, index=True)
    symbol = Column(String(50), nullable=True)
    analysis_type = Column(String(50), default="PERSONALIZATION")
    result_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserDB", back_populates="sessions")
    logs = relationship("AnalysisLogDB", back_populates="session", cascade="all, delete-orphan")


class AnalysisLogDB(Base):
    __tablename__ = "analysis_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("analysis_sessions.session_id"), nullable=True, index=True)
    user_id = Column(String(100), ForeignKey("users.user_id"), nullable=False, index=True)
    level = Column(String(20), default="INFO")
    agent_name = Column(String(100), default="person4_personalization")
    message = Column(Text, nullable=False)
    details_json = Column(Text, default="{}")
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserDB", back_populates="logs")
    session = relationship("AnalysisSessionDB", back_populates="logs")
