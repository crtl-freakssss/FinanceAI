from typing import Dict, Any

from agents.base_agent import BaseAgent
from models.agent_result import AgentResult


class RiskAgent(BaseAgent):
    """
    Portfolio Risk & Personalization Agent

    Uses:
    - Risk tolerance
    - Portfolio exposure
    - Investment horizon
    """

    def __init__(self):
        super().__init__("risk")

    async def analyze(self, data: Dict[str, Any]) -> AgentResult:
        profile = data.get("user_profile", {})

        risk_tolerance = profile.get("risk_tolerance", "moderate").lower()
        portfolio_exposure = profile.get("portfolio_exposure", 0)
        investment_horizon = profile.get("investment_horizon", "long_term").lower()

        score = 50
        reasons = []
        risks = []

        # ---------- Risk Tolerance ----------
        if risk_tolerance == "aggressive":
            score += 15
            reasons.append("Aggressive investor profile can tolerate higher volatility.")
        elif risk_tolerance == "moderate":
            reasons.append("Moderate investor profile prefers balanced opportunities.")
        elif risk_tolerance == "conservative":
            score -= 15
            risks.append("Conservative investor profile favors lower-risk investments.")

        # ---------- Portfolio Exposure ----------
        if portfolio_exposure >= 45:
            score -= 20
            risks.append(f"Portfolio exposure is high ({portfolio_exposure}%).")
        elif portfolio_exposure >= 30:
            score -= 10
            risks.append(f"Portfolio exposure is moderate ({portfolio_exposure}%).")
        else:
            score += 10
            reasons.append("Portfolio has healthy diversification.")

        # ---------- Investment Horizon ----------
        if investment_horizon == "long_term":
            score += 10
            reasons.append("Long-term horizon supports growth investments.")
        elif investment_horizon == "short_term":
            score -= 10
            risks.append("Short-term investing increases market timing risk.")
        else:
            reasons.append("Medium-term investment horizon detected.")

        # ---------- Final Signal ----------
        if score >= 65:
            signal = "BUY"
        elif score >= 45:
            signal = "HOLD"
        elif score >= 30:
            signal = "SELL"
        else:
            signal = "AVOID"

        confidence = min(max(score / 80, 0), 1)

        return AgentResult(
            agent="risk",
            signal=signal,
            confidence=round(confidence, 2),
            reasons=reasons,
            risks=risks,
            sources=["User Profile", "Portfolio Analysis"],
            metadata={
                "risk_tolerance": risk_tolerance,
                "portfolio_exposure": portfolio_exposure,
                "investment_horizon": investment_horizon,
                "risk_score": score,
            },
        )