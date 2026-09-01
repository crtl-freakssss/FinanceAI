"""
StIC AI Insights Adapter
Transforms raw Person 4 Behavioral & Risk Intelligence data into the SI Terminal AI Insights layout.
"""

from typing import Any, Dict, List
from stic.client.stic_person4_client import StICPerson4Client
from stic.schemas.stic_models import (
    SITerminalAIInsightItem,
    SITerminalAIInsightsView,
)


class StICAIInsightsAdapter:
    """Adapts Person 4 Behavioral and Risk data into SI Terminal AI Insights models."""

    def __init__(self, client: StICPerson4Client):
        self.client = client

    def get_terminal_ai_insights_view(self, user_id: str) -> SITerminalAIInsightsView:
        """
        Fetches investor profile, behavior, and advanced risk from Person 4 API,
        then transforms it into the SI Terminal AI Insights UI layout.
        """
        profile_raw = self.client.get_investor_profile(user_id)
        behavior_raw = self.client.get_behavior(user_id)
        risk_raw = self.client.get_advanced_risk(user_id)

        investor_type = profile_raw.get("investor_type", "BALANCED_INVESTOR")
        declared = profile_raw.get("declared_risk_profile", "MODERATE")
        observed = profile_raw.get("observed_risk_profile", "MODERATE")
        alignment = profile_raw.get("alignment", "ALIGNED")
        score = float(profile_raw.get("behaviour_score", 50.0))

        # Sentiment score map (0-100 where higher is Greed/Bullish, lower is Fear/Defensive)
        if observed == "AGGRESSIVE":
            sentiment_score = 78
            sentiment_label = "Greed"
            consensus_action = "BUY"
        elif observed == "CONSERVATIVE":
            sentiment_score = 35
            sentiment_label = "Caution / Fear"
            consensus_action = "HOLD"
        else:
            sentiment_score = 55
            sentiment_label = "Neutral"
            consensus_action = "REBALANCE"

        # Construct AI insight signals
        signals: List[SITerminalAIInsightItem] = []

        # 1. Profile Alignment Signal
        signals.append(
            SITerminalAIInsightItem(
                title=f"Investor Profile: {investor_type.replace('_', ' ').title()}",
                detail=f"Declared profile ({declared}) is {alignment.lower()} with observed trading activity ({observed}).",
                type="info" if alignment == "ALIGNED" else "warning",
            )
        )

        # 2. Risk & Volatility Signal
        vol_data = risk_raw.get("volatility") or {}
        ann_vol = float(vol_data.get("annualized_volatility") or 0.0)
        drawdown_data = risk_raw.get("drawdown") or {}
        max_dd = float(drawdown_data.get("maximum_drawdown_percent") or 0.0)

        signals.append(
            SITerminalAIInsightItem(
                title=f"Portfolio Risk Level: {risk_raw.get('risk_level', 'MEDIUM')}",
                detail=f"Annualized volatility estimated at {ann_vol:.1f}% with historical max drawdown of {max_dd:.1f}%.",
                type="bullish" if ann_vol < 15.0 else ("warning" if ann_vol > 25.0 else "info"),
            )
        )

        # 3. Behavioral Flags Signal
        flags = behavior_raw.get("behavioral_flags", [])
        for flag in flags:
            signals.append(
                SITerminalAIInsightItem(
                    title=f"Behavior Notice: {flag.replace('_', ' ').title()}",
                    detail=f"Detected pattern: {flag}.",
                    type="warning",
                )
            )

        summary_text = (
            f"Observed trading pattern indicates a {observed.lower()} risk posture with {alignment.lower()} profile consistency. "
            f"System recommends {consensus_action.lower()} posture aligned with portfolio diversification targets."
        )

        return SITerminalAIInsightsView(
            user_id=user_id,
            investor_type=investor_type,
            declared_risk_profile=declared,
            observed_risk_profile=observed,
            profile_alignment=alignment,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            synthesis_summary=summary_text,
            consensus_action=consensus_action,
            signals=signals,
            behavior_flags=flags,
        )
