from __future__ import annotations

from typing import Any

from behavior.analyzer import analyze_behavior

from models.behavior import (
    BehaviourFlag,
    InvestorProfileAssessment,
)


def _get(
    obj: Any,
    key: str,
    default=None,
):
    if isinstance(obj, dict):
        return obj.get(
            key,
            default,
        )

    return getattr(
        obj,
        key,
        default,
    )


def _normalize_profile(
    profile: Any,
) -> str:

    value = _get(
        profile,
        "risk_tolerance",
    )

    if value is None:
        value = _get(
            profile,
            "risk_profile",
            "MODERATE",
        )

    return str(
        value
    ).upper()


def _observed_profile(
    behaviour: Any,
) -> str:

    score = float(
        behaviour.behaviour_score
    )

    if score < 30:
        return "CONSERVATIVE"

    if score < 60:
        return "MODERATE"

    return "AGGRESSIVE"


def _alignment(
    declared: str,
    observed: str,
) -> str:

    if declared == observed:
        return "ALIGNED"

    pairs = {
        (
            "CONSERVATIVE",
            "MODERATE",
        ),
        (
            "MODERATE",
            "CONSERVATIVE",
        ),
        (
            "MODERATE",
            "AGGRESSIVE",
        ),
        (
            "AGGRESSIVE",
            "MODERATE",
        ),
    }

    if (
        declared,
        observed,
    ) in pairs:
        return "PARTIALLY_ALIGNED"

    return "MISALIGNED"


def build_investor_profile(
    user_id: str,
    profile: Any,
) -> InvestorProfileAssessment:

    behaviour = analyze_behavior(
        user_id
    )

    declared = _normalize_profile(
        profile
    )

    observed = _observed_profile(
        behaviour
    )

    alignment = _alignment(
        declared,
        observed,
    )

    # Confidence depends on available behavioural evidence.
    if (
        behaviour.data_quality.overall
        == "complete"
    ):
        confidence = 90.0

    elif (
        behaviour.data_quality.overall
        == "partial"
    ):
        confidence = 60.0

    else:
        confidence = 25.0

    recommendations: list[str] = []

    if alignment == "MISALIGNED":
        recommendations.append(
            "Review the difference between declared risk tolerance "
            "and observed trading behaviour."
        )

    if behaviour.behaviour_score >= 60:
        recommendations.append(
            "Review trading frequency and portfolio turnover "
            "before taking additional risk."
        )

    if behaviour.investor_archetype == "ACTIVE_TRADER":
        recommendations.append(
            "Monitor transaction costs and short-term trading exposure."
        )

    if (
        behaviour.loss_tolerance == "HIGH"
    ):
        recommendations.append(
            "Review downside protection and maximum acceptable loss."
        )

    if not recommendations:
        recommendations.append(
            "Observed behaviour is broadly consistent with the "
            "available investor profile data."
        )

    return InvestorProfileAssessment(
        user_id=user_id,
        declared_risk_profile=declared,
        observed_risk_profile=observed,
        investor_type=(
            behaviour.investor_archetype
        ),
        alignment=alignment,
        behaviour_score=(
            behaviour.behaviour_score
        ),
        profile_confidence=confidence,
        recommendations=recommendations,
        behaviour_flags=(
            behaviour.behaviour_flags
        ),
    )
