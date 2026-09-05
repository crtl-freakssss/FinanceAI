from __future__ import annotations

from datetime import date
from statistics import mean
from typing import Any, Iterable, Optional


def _get(obj: Any, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def _float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None

        return float(value)

    except (TypeError, ValueError):
        return None


def transaction_value(transaction: Any) -> float:
    quantity = _float(
        _get(transaction, "quantity", 0)
    ) or 0.0

    price = _float(
        _get(transaction, "price", 0)
    ) or 0.0

    return quantity * price


def normalize_transactions(
    transactions: Iterable[Any],
) -> list[Any]:
    return list(transactions or [])


def calculate_trading_statistics(
    transactions: Iterable[Any],
) -> dict:
    transactions = normalize_transactions(
        transactions
    )

    buys = []
    sells = []

    for transaction in transactions:
        transaction_type = str(
            _get(
                transaction,
                "transaction_type",
                "",
            )
        ).upper()

        if transaction_type == "BUY":
            buys.append(transaction)

        elif transaction_type == "SELL":
            sells.append(transaction)

    buy_value = sum(
        transaction_value(transaction)
        for transaction in buys
    )

    sell_value = sum(
        transaction_value(transaction)
        for transaction in sells
    )

    total_value = (
        buy_value + sell_value
    )

    count = len(transactions)

    average_value = (
        total_value / count
        if count
        else 0.0
    )

    if count == 0:
        frequency = "NO_DATA"

    elif count <= 4:
        frequency = "LOW"

    elif count <= 10:
        frequency = "MEDIUM"

    else:
        frequency = "HIGH"

    # Transaction turnover classification.
    if total_value == 0:
        turnover = "NO_DATA"

    elif total_value < 100000:
        turnover = "LOW"

    elif total_value < 500000:
        turnover = "MEDIUM"

    else:
        turnover = "HIGH"

    return {
        "total_transactions": count,
        "buy_transactions": len(buys),
        "sell_transactions": len(sells),
        "total_buy_value": buy_value,
        "total_sell_value": sell_value,
        "average_transaction_value": average_value,
        "trading_frequency": frequency,
        "turnover_level": turnover,
    }


def parse_date(value: Any) -> Optional[date]:
    if isinstance(value, date):
        return value

    if not value:
        return None

    try:
        return date.fromisoformat(
            str(value)
        )

    except ValueError:
        return None


def calculate_holding_periods(
    transactions: Iterable[Any],
) -> list[int]:
    """
    Match SELL transactions against earlier BUY
    transactions using FIFO.

    Returns completed holding periods in days.
    """
    transactions = normalize_transactions(
        transactions
    )

    ordered = sorted(
        transactions,
        key=lambda x: (
            parse_date(
                _get(x, "date")
            )
            or date.min
        ),
    )

    buy_queues: dict[str, list[dict]] = {}

    holding_periods = []

    for transaction in ordered:
        symbol = str(
            _get(
                transaction,
                "symbol",
                "",
            )
        ).upper()

        transaction_type = str(
            _get(
                transaction,
                "transaction_type",
                "",
            )
        ).upper()

        quantity = _float(
            _get(
                transaction,
                "quantity",
                0,
            )
        ) or 0.0

        transaction_date = parse_date(
            _get(
                transaction,
                "date",
            )
        )

        if (
            not symbol
            or quantity <= 0
            or transaction_date is None
        ):
            continue

        if transaction_type == "BUY":

            buy_queues.setdefault(
                symbol,
                [],
            ).append(
                {
                    "quantity": quantity,
                    "date": transaction_date,
                }
            )

        elif transaction_type == "SELL":

            remaining = quantity

            queue = buy_queues.get(
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

                days = (
                    transaction_date
                    - buy["date"]
                ).days

                holding_periods.append(
                    max(0, days)
                )

                remaining -= matched
                buy["quantity"] -= matched

                if buy["quantity"] <= 0:
                    queue.pop(0)

    return holding_periods