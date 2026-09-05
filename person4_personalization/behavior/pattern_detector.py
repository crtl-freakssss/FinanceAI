from __future__ import annotations

from typing import Any

from models.behavior import BehaviourFlag


def detect_behavior_flags(
    trading: Any,
    holding: Any,
    performance: Any,
) -> list[BehaviourFlag]:

    flags: list[BehaviourFlag] = []

    frequency = str(
        getattr(
            trading,
            "trading_frequency",
            "",
        )
    ).upper()

    turnover = str(
        getattr(
            trading,
            "turnover_level",
            "",
        )
    ).upper()

    holding_style = str(
        getattr(
            holding,
            "holding_style",
            "",
        )
    ).upper()

    win_rate = getattr(
        performance,
        "win_rate",
        None,
    )

    profit_factor = getattr(
        performance,
        "profit_factor",
        None,
    )

    if frequency == "HIGH":
        flags.append(
            BehaviourFlag(
                code="HIGH_TRADING_FREQUENCY",
                severity="HIGH",
                message=(
                    "Trading activity is unusually frequent."
                ),
            )
        )

    if turnover == "HIGH":
        flags.append(
            BehaviourFlag(
                code="HIGH_TURNOVER",
                severity="HIGH",
                message=(
                    "Portfolio transaction turnover is high."
                ),
            )
        )

    if holding_style == "SHORT_TERM":
        flags.append(
            BehaviourFlag(
                code="SHORT_TERM_TRADING",
                severity="MEDIUM",
                message=(
                    "Observed completed positions tend to be held "
                    "for relatively short periods."
                ),
            )
        )

    if (
        win_rate is not None
        and win_rate < 40
    ):
        flags.append(
            BehaviourFlag(
                code="LOW_WIN_RATE",
                severity="MEDIUM",
                message=(
                    "Historical completed trades have a low win rate."
                ),
            )
        )

    if (
        profit_factor is not None
        and profit_factor < 1
    ):
        flags.append(
            BehaviourFlag(
                code="NEGATIVE_TRADE_EFFICIENCY",
                severity="HIGH",
                message=(
                    "Realized losses exceed realized profits."
                ),
            )
        )

    return flags


def calculate_consistency_score(
    trading: Any,
    performance: Any,
) -> float:

    total = getattr(
        trading,
        "total_transactions",
        0,
    )

    if total < 3:
        return 0.0

    frequency = str(
        getattr(
            trading,
            "trading_frequency",
            "",
        )
    ).upper()

    win_rate = getattr(
        performance,
        "win_rate",
        None,
    )

    score = 50.0

    if frequency in {
        "LOW",
        "MEDIUM",
    }:
        score += 15

    if win_rate is not None:
        if 45 <= win_rate <= 70:
            score += 20
        elif win_rate >= 35:
            score += 10

    return min(
        100.0,
        max(0.0, score),
    )


def determine_loss_tolerance(
    performance: Any,
) -> str:

    losses = getattr(
        performance,
        "losing_trades",
        0,
    )

    wins = getattr(
        performance,
        "winning_trades",
        0,
    )

    total = losses + wins

    if total < 3:
        return "UNKNOWN"

    loss_ratio = losses / total

    if loss_ratio >= 0.65:
        return "HIGH"

    if loss_ratio >= 0.45:
        return "MEDIUM"

    return "LOW"


def determine_investor_archetype(
    trading: Any,
    holding: Any,
    performance: Any,
) -> str:

    frequency = str(
        getattr(
            trading,
            "trading_frequency",
            "",
        )
    ).upper()

    turnover = str(
        getattr(
            trading,
            "turnover_level",
            "",
        )
    ).upper()

    holding_style = str(
        getattr(
            holding,
            "holding_style",
            "",
        )
    ).upper()

    if (
        frequency == "HIGH"
        and holding_style == "SHORT_TERM"
    ):
        return "ACTIVE_TRADER"

    if (
        frequency in {"MEDIUM", "HIGH"}
        and turnover in {"MEDIUM", "HIGH"}
    ):
        return "ACTIVE_GROWTH"

    if holding_style == "LONG_TERM":
        return "LONG_TERM_INVESTOR"

    if (
        frequency == "LOW"
        and turnover == "LOW"
    ):
        return "PASSIVE_INVESTOR"

    return "BALANCED_INVESTOR"