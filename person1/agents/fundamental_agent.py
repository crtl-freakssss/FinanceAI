from typing import Dict, Any

from agents.base_agent import BaseAgent
from models.agent_result import AgentResult


class FundamentalAgent(BaseAgent):
    """
    Fundamental Analysis Agent

    Uses:
    - Revenue Growth
    - Profit Growth
    - PE Ratio
    - RAG Summary
    - Financial Documents / Citations
    """

    def __init__(self):
        super().__init__("fundamental")

    async def analyze(self, data: Dict[str, Any]) -> AgentResult:
        fundamentals = data.get("fundamental_data", {})

        revenue_growth = fundamentals.get("revenue_growth", 0)
        profit_growth = fundamentals.get("profit_growth", 0)
        pe_ratio = fundamentals.get("pe_ratio", 25)
        rag_summary = fundamentals.get("rag_summary", "")
        sources = fundamentals.get("sources", [])

        score = 0
        reasons = []
        risks = []

        # -------- Revenue Growth --------
        if revenue_growth >= 15:
            score += 25
            reasons.append(f"Revenue growth is strong ({revenue_growth}%).")
        elif revenue_growth >= 8:
            score += 18
            reasons.append(f"Revenue growth is healthy ({revenue_growth}%).")
        elif revenue_growth >= 3:
            score += 10
            reasons.append("Revenue growth is moderate.")
        else:
            score -= 12
            risks.append("Weak revenue growth.")

        # -------- Profit Growth --------
        if profit_growth >= 12:
            score += 20
            reasons.append(f"Profit growth is strong ({profit_growth}%).")
        elif profit_growth >= 5:
            score += 12
            reasons.append(f"Profit growth is positive ({profit_growth}%).")
        else:
            score -= 10
            risks.append("Profit growth is weak or declining.")

        # -------- PE Ratio --------
        if pe_ratio <= 20:
            score += 15
            reasons.append(f"PE ratio ({pe_ratio}) indicates attractive valuation.")
        elif pe_ratio <= 30:
            score += 8
            reasons.append(f"PE ratio ({pe_ratio}) is within acceptable valuation range.")
        else:
            score -= 10
            risks.append(f"PE ratio ({pe_ratio}) suggests expensive valuation.")

        # -------- RAG Summary --------
        summary = rag_summary.lower()

        positive_keywords = [
            "growth",
            "record",
            "profit",
            "expansion",
            "strong",
            "increase",
            "approved",
            "beat",
        ]

        negative_keywords = [
            "loss",
            "decline",
            "debt",
            "penalty",
            "fraud",
            "warning",
            "miss",
            "lawsuit",
        ]

        positive_hits = sum(word in summary for word in positive_keywords)
        negative_hits = sum(word in summary for word in negative_keywords)

        if positive_hits > negative_hits:
            score += 15
            reasons.append("RAG analysis found positive earnings and filing signals.")
        elif negative_hits > positive_hits:
            score -= 15
            risks.append("RAG analysis detected financial concerns.")
        else:
            reasons.append("RAG analysis is neutral.")

        # -------- Final Signal --------
        if score >= 55:
            signal = "BUY"
        elif score >= 35:
            signal = "HOLD"
        elif score >= 15:
            signal = "SELL"
        else:
            signal = "AVOID"

        confidence = min(max(score / 75, 0), 1)

        return AgentResult(
            agent="fundamental",
            signal=signal,
            confidence=round(confidence, 2),
            reasons=reasons,
            risks=risks,
            sources=sources if sources else ["Quarterly Results", "Financial Filings"],
            metadata={
                "revenue_growth": revenue_growth,
                "profit_growth": profit_growth,
                "pe_ratio": pe_ratio,
                "rag_summary": rag_summary,
                "positive_hits": positive_hits,
                "negative_hits": negative_hits,
                "fundamental_score": score,
            },
        )