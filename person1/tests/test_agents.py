import os
import sys
import pytest

_person1_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _person1_dir not in sys.path:
    sys.path.insert(0, _person1_dir)

from agents.technical_agent import TechnicalAgent
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent
from agents.risk_agent import RiskAgent
from orchestration.graph import FinancialAIGraph



sample_input = {
    "symbol": "TCS",
    "market_data": {
        "price": 3421,
        "rsi": 63,
        "ema20": 3315,
        "ema50": 3242,
        "macd": 1.2,
        "volume_change": 18,
        "momentum": 0.74,
        "volatility": 0.28,
    },
    "news_data": {
        "sentiment_score": 0.71,
        "positive_news": 8,
        "negative_news": 2,
        "headlines": [
            "TCS reports strong quarterly growth",
            "Analysts upgrade TCS outlook",
            "Record profit announced"
        ]
    },
    "fundamental_data": {
        "revenue_growth": 11.2,
        "profit_growth": 8.5,
        "pe_ratio": 28,
        "rag_summary": "Strong revenue growth and profit increase in quarterly results.",
        "sources": [
            "Quarterly Results",
            "SEBI Filing"
        ]
    },
    "user_profile": {
        "risk_tolerance": "moderate",
        "portfolio_exposure": 25,
        "investment_horizon": "long_term"
    }
}


@pytest.mark.anyio
async def test_individual_agents():
    technical = await TechnicalAgent().execute(sample_input)
    fundamental = await FundamentalAgent().execute(sample_input)
    sentiment = await SentimentAgent().execute(sample_input)
    risk = await RiskAgent().execute(sample_input)

    assert technical.agent == "technical"
    assert fundamental.agent == "fundamental"
    assert sentiment.agent == "sentiment"
    assert risk.agent == "risk"

    assert technical.signal in ["BUY", "HOLD", "SELL", "AVOID"]
    assert fundamental.signal in ["BUY", "HOLD", "SELL", "AVOID"]
    assert sentiment.signal in ["BUY", "HOLD", "SELL", "AVOID"]
    assert risk.signal in ["BUY", "HOLD", "SELL", "AVOID"]


@pytest.mark.anyio
async def test_full_orchestrator():

    graph = FinancialAIGraph()

    result = await graph.run(sample_input)

    assert result["symbol"] == "TCS"
    assert result["overall_signal"] in ["BUY", "HOLD", "SELL", "AVOID"]
    assert "confidence" in result
    assert "summary" in result
    assert result["metrics"]["parallel_execution"] is True
    assert result["metrics"]["agents_executed"] == 4