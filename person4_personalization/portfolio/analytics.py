from __future__ import annotations

from typing import Any

from models.portfolio_analysis import (
    AllocationItem,
    AllocationResult,
    ConcentrationResult,
    ExposureResult,
    PortfolioAnalysis,
    PortfolioHealthResult,
    PortfolioRiskResult,
)


def _get_attr(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _value(holding: Any) -> float:
    """
    Safely calculate the current value of a holding.

    Supports both:
    - dict or model with value / current_value
    - dict or model with shares/quantity and current_price
    """
    val = _get_attr(holding, "value")
    if val is not None:
        return float(val)

    current_val = _get_attr(holding, "current_value")
    if current_val is not None:
        return float(current_val)

    quantity = _get_attr(holding, "shares")
    if quantity is None:
        quantity = _get_attr(holding, "quantity", 0)
    quantity = float(quantity)

    current_price = float(_get_attr(holding, "current_price", 0))

    return quantity * current_price


def _symbol(holding: Any) -> str:
    return str(_get_attr(holding, "symbol", "UNKNOWN")).upper()


def _sector(holding: Any) -> str:
    return str(_get_attr(holding, "sector", "Unknown")).strip().title()


def _holdings(portfolio: Any) -> list[Any]:
    if portfolio is None:
        return []
    return list(_get_attr(portfolio, "holdings", []) or [])


def total_holdings_value(portfolio: Any) -> float:
    return round(
        sum(_value(holding) for holding in _holdings(portfolio)),
        2,
    )


def cash_value(portfolio: Any) -> float:
    return round(float(_get_attr(portfolio, "cash", 0.0)), 2)


def total_portfolio_value(portfolio: Any) -> float:
    return round(
        total_holdings_value(portfolio) + cash_value(portfolio),
        2,
    )


def cash_percent(portfolio: Any) -> float:
    total = total_portfolio_value(portfolio)

    if total <= 0:
        return 0.0

    return round(cash_value(portfolio) / total * 100, 2)


def equity_percent(portfolio: Any) -> float:
    total = total_portfolio_value(portfolio)

    if total <= 0:
        return 0.0

    return round(total_holdings_value(portfolio) / total * 100, 2)


def calculate_allocation(portfolio: Any) -> AllocationResult:
    total = total_portfolio_value(portfolio)

    if total <= 0:
        return AllocationResult(
            by_symbol=[],
            by_sector=[],
        )

    symbol_values: dict[str, float] = {}
    sector_values: dict[str, float] = {}

    for holding in _holdings(portfolio):
        value = _value(holding)

        if value <= 0:
            continue

        symbol = _symbol(holding)
        sector = _sector(holding)

        symbol_values[symbol] = (
            symbol_values.get(symbol, 0.0) + value
        )

        sector_values[sector] = (
            sector_values.get(sector, 0.0) + value
        )

    by_symbol = [
        AllocationItem(
            name=name,
            value=round(value, 2),
            percentage=round(value / total * 100, 2),
        )
        for name, value in sorted(
            symbol_values.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

    by_sector = [
        AllocationItem(
            name=name,
            value=round(value, 2),
            percentage=round(value / total * 100, 2),
        )
        for name, value in sorted(
            sector_values.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

    cash = cash_value(portfolio)

    if cash > 0:
        by_symbol.append(
            AllocationItem(
                name="CASH",
                value=round(cash, 2),
                percentage=round(cash / total * 100, 2),
            )
        )

        by_sector.append(
            AllocationItem(
                name="Cash",
                value=round(cash, 2),
                percentage=round(cash / total * 100, 2),
            )
        )

    return AllocationResult(
        by_symbol=by_symbol,
        by_sector=by_sector,
    )


def calculate_concentration(
    portfolio: Any,
) -> ConcentrationResult:
    total = total_portfolio_value(portfolio)

    if total <= 0:
        return ConcentrationResult(
            largest_position_percent=0.0,
            top_three_position_percent=0.0,
            largest_sector_percent=0.0,
            concentration_score=0.0,
            concentration_level="LOW",
        )

    symbol_values: dict[str, float] = {}
    sector_values: dict[str, float] = {}

    for holding in _holdings(portfolio):
        value = _value(holding)

        if value <= 0:
            continue

        symbol = _symbol(holding)
        sector = _sector(holding)

        symbol_values[symbol] = (
            symbol_values.get(symbol, 0.0) + value
        )

        sector_values[sector] = (
            sector_values.get(sector, 0.0) + value
        )

    position_percentages = sorted(
        (
            value / total * 100
            for value in symbol_values.values()
        ),
        reverse=True,
    )

    sector_percentages = sorted(
        (
            value / total * 100
            for value in sector_values.values()
        ),
        reverse=True,
    )

    largest_position = (
        position_percentages[0]
        if position_percentages
        else 0.0
    )

    top_three = min(
        sum(position_percentages[:3]),
        100.0,
    )

    largest_sector = (
        sector_percentages[0]
        if sector_percentages
        else 0.0
    )

    # Concentration score:
    # position concentration contributes 65%
    # sector concentration contributes 35%.
    score = min(
        100.0,
        largest_position * 0.65
        + largest_sector * 0.35,
    )

    score = round(score, 2)

    if score >= 60:
        level = "HIGH"
    elif score >= 35:
        level = "MEDIUM"
    else:
        level = "LOW"

    return ConcentrationResult(
        largest_position_percent=round(
            largest_position,
            2,
        ),
        top_three_position_percent=round(
            top_three,
            2,
        ),
        largest_sector_percent=round(
            largest_sector,
            2,
        ),
        concentration_score=score,
        concentration_level=level,
    )


def calculate_diversification_score(
    portfolio: Any,
    concentration: ConcentrationResult | None = None,
) -> float:
    if concentration is None:
        concentration = calculate_concentration(portfolio)

    holdings = _holdings(portfolio)

    unique_symbols = {
        _symbol(holding)
        for holding in holdings
        if _value(holding) > 0
    }

    unique_sectors = {
        _sector(holding)
        for holding in holdings
        if _value(holding) > 0
    }

    holding_count = len(unique_symbols)
    sector_count = len(unique_sectors)

    # Holdings component.
    holding_score = min(
        holding_count / 10 * 100,
        100,
    )

    # Sector component.
    sector_score = min(
        sector_count / 6 * 100,
        100,
    )

    # Concentration directly reduces diversification.
    concentration_penalty = concentration.concentration_score

    score = (
        holding_score * 0.30
        + sector_score * 0.30
        + (100 - concentration_penalty) * 0.40
    )

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


def calculate_portfolio_risk(
    portfolio: Any,
    concentration: ConcentrationResult | None = None,
) -> PortfolioRiskResult:
    if concentration is None:
        concentration = calculate_concentration(portfolio)

    diversification = calculate_diversification_score(
        portfolio,
        concentration,
    )

    cash = cash_percent(portfolio)

    warnings: list[str] = []

    score = 50.0

    # Concentration.
    score += concentration.concentration_score * 0.40

    # Poor diversification increases risk.
    score += (100 - diversification) * 0.25

    # Very low cash increases risk.
    if cash < 5:
        score += 15
        warnings.append(
            "Cash allocation is below 5%."
        )
    elif cash < 10:
        score += 7
        warnings.append(
            "Cash allocation is below 10%."
        )
    elif cash > 40:
        score -= 8
        warnings.append(
            "High cash allocation may reduce portfolio exposure."
        )

    # Small portfolios are naturally less diversified.
    holding_count = len(
        {
            _symbol(holding)
            for holding in _holdings(portfolio)
            if _value(holding) > 0
        }
    )

    if holding_count <= 2:
        score += 12
        warnings.append(
            "Portfolio contains very few holdings."
        )
    elif holding_count <= 4:
        score += 5
        warnings.append(
            "Portfolio diversification is limited."
        )

    score = round(
        max(0.0, min(100.0, score)),
        2,
    )

    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return PortfolioRiskResult(
        risk_score=score,
        risk_level=level,
        concentration_score=concentration.concentration_score,
        diversification_score=diversification,
        cash_percent=cash,
        warnings=list(dict.fromkeys(warnings)),
    )


def calculate_portfolio_health(
    portfolio: Any,
    concentration: ConcentrationResult | None = None,
    risk: PortfolioRiskResult | None = None,
) -> PortfolioHealthResult:
    if concentration is None:
        concentration = calculate_concentration(portfolio)

    if risk is None:
        risk = calculate_portfolio_risk(
            portfolio,
            concentration,
        )

    warnings = list(risk.warnings)

    score = (
        risk.diversification_score * 0.45
        + (100 - concentration.concentration_score) * 0.35
        + min(risk.cash_percent * 2, 20) * 0.20
    )

    if risk.risk_level == "HIGH":
        score -= 10

    score = round(
        max(0.0, min(100.0, score)),
        2,
    )

    if score >= 70:
        status = "HEALTHY"
    elif score >= 45:
        status = "MODERATE"
    else:
        status = "STRESSED"

    return PortfolioHealthResult(
        health_score=score,
        status=status,
        diversification_score=risk.diversification_score,
        concentration_score=concentration.concentration_score,
        warnings=list(dict.fromkeys(warnings)),
    )


def calculate_exposure(
    portfolio: Any,
    user: Any,
    symbol: str,
    sector: str = "Unknown",
) -> ExposureResult:
    normalized_symbol = symbol.upper()
    normalized_sector = sector.strip().title()

    total = total_portfolio_value(portfolio)

    position_value = sum(
        _value(holding)
        for holding in _holdings(portfolio)
        if _symbol(holding) == normalized_symbol
    )

    sector_value = sum(
        _value(holding)
        for holding in _holdings(portfolio)
        if _sector(holding) == normalized_sector
    )

    position_percent = (
        position_value / total * 100
        if total > 0
        else 0.0
    )

    sector_percent = (
        sector_value / total * 100
        if total > 0
        else 0.0
    )

    constraints = _get_attr(user, "constraints")
    max_position = _get_attr(user, "max_position_percent")
    if max_position is None and constraints:
        max_position = _get_attr(constraints, "max_single_position_pct") or _get_attr(constraints, "max_position_percent")
    if max_position is None:
        max_position = 100.0
    max_position = float(max_position)

    max_sector = _get_attr(user, "max_sector_percent")
    if max_sector is None and constraints:
        max_sector = _get_attr(constraints, "max_sector_exposure_pct") or _get_attr(constraints, "max_sector_percent")
    if max_sector is None:
        max_sector = 100.0
    max_sector = float(max_sector)

    user_id = str(_get_attr(user, "user_id", ""))

    return ExposureResult(
        user_id=user_id,
        symbol=normalized_symbol,
        sector=normalized_sector,
        position_value=round(position_value, 2),
        position_exposure_percent=round(
            position_percent,
            2,
        ),
        sector_value=round(sector_value, 2),
        sector_exposure_percent=round(
            sector_percent,
            2,
        ),
        max_position_percent=max_position,
        max_sector_percent=max_sector,
        position_breach=position_percent > max_position,
        sector_breach=sector_percent > max_sector,
    )


def calculate_portfolio_analysis(
    portfolio: Any,
) -> PortfolioAnalysis:
    allocation = calculate_allocation(portfolio)

    concentration = calculate_concentration(
        portfolio,
    )

    risk = calculate_portfolio_risk(
        portfolio,
        concentration,
    )

    health = calculate_portfolio_health(
        portfolio,
        concentration,
        risk,
    )

    total = total_portfolio_value(portfolio)
    holdings = total_holdings_value(portfolio)
    cash = cash_value(portfolio)

    return PortfolioAnalysis(
        user_id=str(_get_attr(portfolio, "user_id", "")),
        total_value=total,
        holdings_value=holdings,
        cash_value=cash,
        cash_percent=cash_percent(portfolio),
        equity_percent=equity_percent(portfolio),
        allocation=allocation,
        concentration=concentration,
        risk=risk,
        health=health,
    )