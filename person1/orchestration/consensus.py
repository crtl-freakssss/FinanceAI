from typing import Dict, List

from models.agent_result import AgentResult


class ConsensusEngine:
    """
    Voting + confidence engine.
    """

    SIGNAL_WEIGHTS = {
        "technical": 0.30,
        "fundamental": 0.30,
        "sentiment": 0.20,
        "risk": 0.20,
    }

    SIGNAL_VALUES = {
        "BUY": 3,
        "HOLD": 2,
        "SELL": 1,
        "AVOID": 0,
    }

    VALUE_TO_SIGNAL = {
        3: "BUY",
        2: "HOLD",
        1: "SELL",
        0: "AVOID",
    }

    @classmethod
    def calculate(
        cls,
        technical: AgentResult,
        fundamental: AgentResult,
        sentiment: AgentResult,
        risk: AgentResult,
    ) -> Dict:

        agents = {
            "technical": technical,
            "fundamental": fundamental,
            "sentiment": sentiment,
            "risk": risk,
        }

        weighted_score = 0.0
        weighted_confidence = 0.0

        vote_counter = {
            "BUY": 0,
            "HOLD": 0,
            "SELL": 0,
            "AVOID": 0,
        }

        reasons: List[str] = []
        risks: List[str] = []
        sources: List[str] = []

        for name, result in agents.items():
            weight = cls.SIGNAL_WEIGHTS[name]

            weighted_score += cls.SIGNAL_VALUES[result.signal] * weight
            weighted_confidence += result.confidence * weight

            vote_counter[result.signal] += 1

            reasons.extend(result.reasons)
            risks.extend(result.risks)
            sources.extend(result.sources)

        rounded_score = round(weighted_score)

        overall_signal = cls.VALUE_TO_SIGNAL.get(rounded_score, "HOLD")

        disagreement = len([v for v in vote_counter.values() if v > 0]) >= 3

        if disagreement:
            weighted_confidence *= 0.85
            risks.append(
                "Agents produced conflicting recommendations. Confidence reduced."
            )

        confidence = round(
            min(max(weighted_confidence, 0.25), 0.99),
            2,
        )

        return {
            "overall_signal": overall_signal,
            "confidence": confidence,
            "vote_breakdown": vote_counter,
            "disagreement": disagreement,
            "reasons": list(dict.fromkeys(reasons)),
            "risks": list(dict.fromkeys(risks)),
            "sources": list(dict.fromkeys(sources)),
        }