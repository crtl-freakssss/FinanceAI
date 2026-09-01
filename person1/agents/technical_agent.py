from typing import Dict, Any

from agents.base_agent import BaseAgent
from models.agent_result import AgentResult


class TechnicalAgent(BaseAgent):
    """
    Technical Analysis Agent

    Uses:
    - RSI
    - EMA20 / EMA50
    - MACD
    - Volume Change
    - Momentum
    - Volatility
    """

    def __init__(self):
        super().__init__("technical")

    async def analyze(self, data: Dict[str, Any]) -> AgentResult:
        market = data.get("market_data", {})

        rsi = market.get("rsi", 50)
        ema20 = market.get("ema20", 0)
        ema50 = market.get("ema50", 0)
        price = market.get("price", 0)
        macd = market.get("macd", 0)
        volume_change = market.get("volume_change", 0)
        momentum = market.get("momentum", 0)
        volatility = market.get("volatility", 0)

        score = 0
        reasons = []
        risks = []

        # ---------------- RSI ----------------
        if 55 <= rsi <= 70:
            score += 20
            reasons.append(f"RSI ({rsi}) indicates healthy bullish momentum.")
        elif rsi > 75:
            score -= 10
            risks.append(f"RSI ({rsi}) suggests the stock may be overbought.")
        elif rsi < 35:
            score -= 15
            risks.append(f"RSI ({rsi}) indicates bearish weakness.")
        else:
            reasons.append(f"RSI ({rsi}) is neutral.")

        # ---------------- EMA ----------------
        if price > ema20 > ema50:
            score += 20
            reasons.append("Price is above EMA20 and EMA50.")
        elif price > ema20:
            score += 10
            reasons.append("Price is above EMA20.")
        else:
            score -= 10
            risks.append("Price is below EMA20.")

        # ---------------- MACD ----------------
        if macd > 0:
            score += 15
            reasons.append("MACD is positive, indicating upward trend.")
        else:
            score -= 10
            risks.append("MACD is negative.")

        # ---------------- Volume ----------------
        if volume_change > 15:
            score += 15
            reasons.append("Trading volume is significantly above average.")
        elif volume_change > 5:
            score += 8
            reasons.append("Trading volume is slightly above average.")
        else:
            risks.append("Volume confirmation is weak.")

        # ---------------- Momentum ----------------
        if momentum >= 0.7:
            score += 15
            reasons.append("Momentum indicator is strongly positive.")
        elif momentum >= 0.4:
            score += 8
            reasons.append("Momentum is moderately positive.")
        else:
            score -= 5
            risks.append("Momentum is weak.")

        # ---------------- Volatility ----------------
        if volatility > 0.45:
            score -= 10
            risks.append("High short-term volatility increases risk.")
        elif volatility > 0.3:
            score -= 5
            risks.append("Moderate volatility detected.")
        else:
            reasons.append("Volatility is within acceptable range.")

        # ---------------- Final Decision ----------------
        if score >= 55:
            signal = "BUY"
        elif score >= 35:
            signal = "HOLD"
        elif score >= 15:
            signal = "SELL"
        else:
            signal = "AVOID"

        confidence = min(max(score / 70, 0), 1)

        return AgentResult(
            agent="technical",
            signal=signal,
            confidence=round(confidence, 2),
            reasons=reasons,
            risks=risks,
            sources=["Technical Market Indicators"],
            metadata={
                "price": price,
                "rsi": rsi,
                "ema20": ema20,
                "ema50": ema50,
                "macd": macd,
                "volume_change": volume_change,
                "momentum": momentum,
                "volatility": volatility,
                "technical_score": score
            }
        )