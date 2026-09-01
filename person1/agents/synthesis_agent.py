from models.final_result import FinalResult, PerformanceMetrics
from models.agent_result import AgentResult
from orchestration.consensus import ConsensusEngine


class SynthesisAgent:
    """
    Combines outputs from all specialized agents into one explainable recommendation.
    """

    def synthesize(
        self,
        symbol: str,
        technical: AgentResult,
        fundamental: AgentResult,
        sentiment: AgentResult,
        risk: AgentResult,
    ) -> FinalResult:

        consensus = ConsensusEngine.calculate(
            technical,
            fundamental,
            sentiment,
            risk,
        )

        overall_signal = consensus["overall_signal"]
        confidence = consensus["confidence"]

        # -------- Human-readable summary --------
        if overall_signal == "BUY":
            summary = (
                f"{symbol} shows a positive investment outlook based on technical "
                "momentum, financial fundamentals, market sentiment, and portfolio suitability."
            )

        elif overall_signal == "HOLD":
            summary = (
                f"{symbol} presents a balanced investment outlook. Some indicators "
                "are positive while others recommend caution."
            )

        elif overall_signal == "SELL":
            summary = (
                f"{symbol} has multiple warning signals. Investors should carefully "
                "evaluate exposure before investing."
            )

        else:
            summary = (
                f"{symbol} currently carries elevated downside risk and is not "
                "recommended for this investor profile."
            )

        # -------- Correct latency for PARALLEL execution --------
        slowest_agent = max(
            technical.latency_ms,
            fundamental.latency_ms,
            sentiment.latency_ms,
            risk.latency_ms,
        )

        metrics = PerformanceMetrics(
            technical_latency_ms=technical.latency_ms,
            fundamental_latency_ms=fundamental.latency_ms,
            sentiment_latency_ms=sentiment.latency_ms,
            risk_latency_ms=risk.latency_ms,
            total_latency_ms=slowest_agent,
            slowest_agent_ms=slowest_agent,
        )

        return FinalResult(
            symbol=symbol,
            overall_signal=overall_signal,
            confidence=confidence,
            summary=summary,
            key_reasons=consensus["reasons"][:5],
            risks=consensus["risks"][:5],
            sources=consensus["sources"],
            agents={
                "technical": technical,
                "fundamental": fundamental,
                "sentiment": sentiment,
                "risk": risk,
            },
            metrics=metrics,
        )