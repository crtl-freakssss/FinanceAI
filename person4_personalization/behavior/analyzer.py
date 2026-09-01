from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any

from models.behavior import (
    BehaviourAssessment,
    BehaviourDataQuality,
    BehaviourFlag,
    HoldingPeriodStatistics,
    TradingPerformance,
    TradingStatistics,
)

from behavior.pattern_detector import (
    calculate_consistency_score,
    detect_behavior_flags,
    determine_investor_archetype,
    determine_loss_tolerance,
)

from behavior.transaction_analyzer import (
    calculate_holding_periods,
    calculate_trading_statistics,
)


DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "mock_data"
    / "behavior.json"
)


def load_behavior_data() -> dict:
    if not DATA_FILE.exists():
        return {}

    with DATA_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def get_transactions(
    user_id: str,
) -> list[dict]:

    data = load_behavior_data()

    user_data = data.get(
        user_id,
        {},
    )

    return user_data.get(
        "transactions",
        [],
    )


def _holding_statistics(
    transactions: list,
) -> HoldingPeriodStatistics:

    periods = calculate_holding_periods(
        transactions
    )

    if not periods:
        return HoldingPeriodStatistics(
            average_holding_days=None,
            shortest_holding_days=None,
            longest_holding_days=None,
            holding_style="NO_DATA",
        )

    average = mean(periods)

    if average < 30:
        style = "SHORT_TERM"

    elif average < 180:
        style = "MEDIUM_TERM"

    else:
        style = "LONG_TERM"

    return HoldingPeriodStatistics(
        average_holding_days=round(
            average,
            2,
        ),
        shortest_holding_days=min(
            periods
        ),
        longest_holding_days=max(
            periods
        ),
        holding_style=style,
    )


def _performance(
    transactions: list,
) -> TradingPerformance:

    ordered = sorted(
        transactions,
        key=lambda x: str(
            x.get("date", "")
        ),
    )

    positions: dict[str, list[dict]] = {}

    winning = 0
    losing = 0

    realized_profit = 0.0
    realized_loss = 0.0

    for transaction in ordered:

        symbol = str(
            transaction.get(
                "symbol",
                "",
            )
        ).upper()

        transaction_type = str(
            transaction.get(
                "transaction_type",
                "",
            )
        ).upper()

        quantity = float(
            transaction.get(
                "quantity",
                0,
            )
        )

        price = float(
            transaction.get(
                "price",
                0,
            )
        )

        if quantity <= 0 or price <= 0:
            continue

        if transaction_type == "BUY":

            positions.setdefault(
                symbol,
                [],
            ).append(
                {
                    "quantity": quantity,
                    "price": price,
                }
            )

        elif transaction_type == "SELL":

            remaining = quantity

            queue = positions.get(
                symbol,
                [],
            )

            while (
                remaining > 0
                and queue
            ):

                buy = queue[0]

                matched = min(
                    remaining,
                    buy["quantity"],
                )

                pnl = (
                    price - buy["price"]
                ) * matched

                if pnl >= 0:
                    winning += 1
                    realized_profit += pnl

                else:
                    losing += 1
                    realized_loss += abs(pnl)

                remaining -= matched
                buy["quantity"] -= matched

                if buy["quantity"] <= 0:
                    queue.pop(0)

    completed = winning + losing

    if completed:
        win_rate = (
            winning / completed
        ) * 100
    else:
        win_rate = None

    if realized_loss > 0:
        profit_factor = (
            realized_profit
            / realized_loss
        )
    elif realized_profit > 0:
        profit_factor = None
    else:
        profit_factor = None

    return TradingPerformance(
        completed_trades=completed,
        winning_trades=winning,
        losing_trades=losing,
        win_rate=(
            round(win_rate, 2)
            if win_rate is not None
            else None
        ),
        realized_profit=round(
            realized_profit,
            2,
        ),
        realized_loss=round(
            realized_loss,
            2,
        ),
        profit_factor=(
            round(
                profit_factor,
                2,
            )
            if profit_factor is not None
            else None
        ),
    )


def _risk_level(
    score: float,
) -> str:

    if score < 30:
        return "LOW"

    if score < 60:
        return "MEDIUM"

    if score < 80:
        return "HIGH"

    return "CRITICAL"


def analyze_behavior(
    user_id: str,
) -> BehaviourAssessment:

    transactions = get_transactions(
        user_id
    )

    trading_data = (
        calculate_trading_statistics(
            transactions
        )
    )

    trading = TradingStatistics(
        **trading_data
    )

    holding = _holding_statistics(
        transactions
    )

    performance = _performance(
        transactions
    )

    consistency = (
        calculate_consistency_score(
            trading,
            performance,
        )
    )

    loss_tolerance = (
        determine_loss_tolerance(
            performance
        )
    )

    archetype = (
        determine_investor_archetype(
            trading,
            holding,
            performance,
        )
    )

    flags = detect_behavior_flags(
        trading,
        holding,
        performance,
    )

    # --------------------------------------------------------
    # Behaviour risk score
    # --------------------------------------------------------

    score = 0.0

    if trading.trading_frequency == "HIGH":
        score += 30

    elif trading.trading_frequency == "MEDIUM":
        score += 15

    if trading.turnover_level == "HIGH":
        score += 25

    elif trading.turnover_level == "MEDIUM":
        score += 12

    if holding.holding_style == "SHORT_TERM":
        score += 25

    elif holding.holding_style == "MEDIUM_TERM":
        score += 10

    if performance.win_rate is not None:
        if performance.win_rate < 40:
            score += 15

        elif performance.win_rate < 50:
            score += 8

    if (
        performance.profit_factor is not None
        and performance.profit_factor < 1
    ):
        score += 15

    score = min(
        100.0,
        score,
    )

    warnings = [
        flag.message
        for flag in flags
    ]

    if not transactions:
        warnings.append(
            "Insufficient transaction history for behavioural profiling."
        )

    if len(transactions) < 3:
        transaction_quality = (
            "insufficient_data"
        )
    else:
        transaction_quality = "calculated"

    if performance.completed_trades < 2:
        performance_quality = (
            "insufficient_data"
        )
    else:
        performance_quality = "calculated"

    if holding.average_holding_days is None:
        holding_quality = (
            "insufficient_data"
        )
    else:
        holding_quality = "calculated"

    quality_values = [
        transaction_quality,
        performance_quality,
        holding_quality,
    ]

    if all(
        value == "calculated"
        for value in quality_values
    ):
        overall = "complete"

    elif any(
        value == "calculated"
        for value in quality_values
    ):
        overall = "partial"

    else:
        overall = "insufficient_data"

    return BehaviourAssessment(
        user_id=user_id,
        behaviour_score=round(
            score,
            2,
        ),
        behaviour_risk_level=_risk_level(
            score
        ),
        trading=trading,
        holding_period=holding,
        performance=performance,
        consistency_score=round(
            consistency,
            2,
        ),
        loss_tolerance=loss_tolerance,
        investor_archetype=archetype,
        behaviour_flags=flags,
        warnings=warnings,
        data_quality=BehaviourDataQuality(
            transaction_history=transaction_quality,
            performance_history=performance_quality,
            holding_period_history=holding_quality,
            overall=overall,
        ),
    )
