from __future__ import annotations

from math import sqrt
from statistics import mean, stdev
from typing import Any, Iterable, Optional

from models.risk_engine import (
    AdvancedRiskAssessment,
    DrawdownRisk,
    LiquidityRisk,
    RiskDataQuality,
    RiskFactor,
    SectorRisk,
    VolatilityRisk,
)


# ============================================================
# GENERAL HELPERS
# ============================================================

def _get(data: Any, key: str, default: Any = None) -> Any:
    """
    Safely read a value from either a dictionary or an object.
    """
    if isinstance(data, dict):
        return data.get(key, default)

    return getattr(data, key, default)


def _safe_float(value: Any) -> Optional[float]:
    """
    Convert a value to float safely.
    """
    try:
        if value is None:
            return None

        result = float(value)

        if result != result:
            return None

        return result

    except (TypeError, ValueError):
        return None


def _holdings(portfolio: Any) -> list:
    """
    Return portfolio holdings as a list.
    """
    holdings = _get(portfolio, "holdings", [])

    if holdings is None:
        return []

    if isinstance(holdings, Iterable) and not isinstance(
        holdings,
        (str, bytes, dict),
    ):
        return list(holdings)

    return []


def _prices_from_holding(holding: Any) -> list[float]:
    """
    Extract available historical prices from a holding.

    Supported forms:
    - price_history
    - historical_prices
    - prices

    If none exists, an empty list is returned.
    """
    for field in (
        "price_history",
        "historical_prices",
        "prices",
    ):
        values = _get(holding, field)

        if values is None:
            continue

        if isinstance(values, dict):
            values = list(values.values())

        if not isinstance(values, Iterable) or isinstance(
            values,
            (str, bytes),
        ):
            continue

        prices = []

        for value in values:
            number = _safe_float(value)

            if number is not None and number > 0:
                prices.append(number)

        if prices:
            return prices

    return []


# ============================================================
# RETURNS
# ============================================================

def calculate_returns(
    prices: Iterable[float],
) -> list[float]:
    """
    Calculate simple period returns.

    Example:
        [100, 110, 99]

    becomes:

        [0.10, -0.10]
    """
    clean_prices = []

    for price in prices:
        value = _safe_float(price)

        if value is not None and value > 0:
            clean_prices.append(value)

    if len(clean_prices) < 2:
        return []

    returns = []

    for previous, current in zip(
        clean_prices,
        clean_prices[1:],
    ):
        if previous <= 0:
            continue

        returns.append(
            (current - previous) / previous
        )

    return returns


# ============================================================
# VOLATILITY
# ============================================================

def calculate_volatility(
    prices: Iterable[float],
    annualize: bool = True,
) -> VolatilityRisk:
    """
    Calculate historical volatility.

    At least two returns are required for standard deviation.

    If insufficient data exists, the result explicitly reports
    insufficient_data instead of falsely returning zero risk.
    """
    returns = calculate_returns(prices)

    if len(returns) < 2:
        return VolatilityRisk(
            value=None,
            annualized_volatility=None,
            score=0.0,
            status="insufficient_data",
        )

    volatility = stdev(returns)

    if annualize:
        annualized = volatility * sqrt(252)
    else:
        annualized = volatility

    volatility_percent = annualized * 100.0

    # Risk scoring:
    # <10%   = very low
    # 10-20% = low
    # 20-30% = moderate
    # 30-50% = high
    # >50%   = extreme
    score = min(
        100.0,
        max(
            0.0,
            volatility_percent * 2.0,
        ),
    )

    return VolatilityRisk(
        value=volatility_percent,
        annualized_volatility=volatility_percent,
        score=score,
        status="calculated",
    )


# ============================================================
# MAXIMUM DRAWDOWN
# ============================================================

def calculate_maximum_drawdown(
    prices: Iterable[float],
) -> DrawdownRisk:
    """
    Calculate maximum drawdown.

    Drawdown is represented as a positive percentage magnitude.

    Example:

        100 -> 120 -> 90

    Maximum drawdown = 25%.
    """
    clean_prices = []

    for price in prices:
        value = _safe_float(price)

        if value is not None and value > 0:
            clean_prices.append(value)

    if len(clean_prices) < 2:
        return DrawdownRisk(
            value=None,
            maximum_drawdown=None,
            score=0.0,
            status="insufficient_data",
        )

    peak = clean_prices[0]
    maximum_drawdown = 0.0

    for price in clean_prices:
        if price > peak:
            peak = price

        if peak <= 0:
            continue

        drawdown = (
            (peak - price) / peak
        )

        maximum_drawdown = max(
            maximum_drawdown,
            drawdown,
        )

    drawdown_percent = (
        maximum_drawdown * 100.0
    )

    # 0-10% = low
    # 10-20% = moderate
    # 20-30% = high
    # >30% = extreme
    score = min(
        100.0,
        drawdown_percent * 2.5,
    )

    return DrawdownRisk(
        value=drawdown_percent,
        maximum_drawdown=drawdown_percent,
        score=score,
        status="calculated",
    )


# ============================================================
# LIQUIDITY
# ============================================================

def calculate_liquidity_risk(
    portfolio: Any,
) -> LiquidityRisk:
    """
    Estimate liquidity risk only when the portfolio actually
    contains liquidity-related information.

    Supported fields:
    - liquidity_score
    - liquidity
    - average_volume
    - volume

    Missing liquidity information is explicitly reported.
    """
    direct_score = _get(
        portfolio,
        "liquidity_score",
    )

    if direct_score is not None:
        score = _safe_float(direct_score)

        if score is not None:
            score = min(
                100.0,
                max(0.0, score),
            )

            return LiquidityRisk(
                value=score,
                liquidity_score=score,
                score=score,
                status="calculated",
            )

    holdings = _holdings(portfolio)

    liquidity_values = []

    for holding in holdings:
        value = (
            _get(holding, "liquidity_score")
        )

        if value is None:
            value = _get(
                holding,
                "liquidity",
            )

        number = _safe_float(value)

        if number is not None:
            liquidity_values.append(number)

    if liquidity_values:
        score = mean(liquidity_values)

        score = min(
            100.0,
            max(0.0, score),
        )

        return LiquidityRisk(
            value=score,
            liquidity_score=score,
            score=score,
            status="calculated",
        )

    # Try a simple volume/position-size signal.
    volume_available = False

    for holding in holdings:
        volume = _get(
            holding,
            "average_volume",
        )

        if volume is None:
            volume = _get(
                holding,
                "volume",
            )

        if _safe_float(volume) is not None:
            volume_available = True
            break

    if not volume_available:
        return LiquidityRisk(
            value=None,
            liquidity_score=0.0,
            score=0.0,
            status="unavailable",
        )

    # We have volume information but no reliable normalized
    # liquidity model. Do not invent a score.
    return LiquidityRisk(
        value=None,
        liquidity_score=0.0,
        score=0.0,
        status="insufficient_data",
    )


# ============================================================
# PORTFOLIO PRICE SERIES
# ============================================================

def _portfolio_price_series(
    portfolio: Any,
) -> list[float]:
    """
    Build a representative portfolio price series.

    If an explicit portfolio-level history exists, use it.

    Otherwise use the first holding with usable historical data.
    This avoids fabricating a portfolio history.
    """
    for field in (
        "portfolio_price_history",
        "price_history",
        "historical_prices",
    ):
        values = _get(portfolio, field)

        if values is not None:
            if isinstance(values, dict):
                values = list(values.values())

            if isinstance(values, Iterable) and not isinstance(
                values,
                (str, bytes),
            ):
                prices = []

                for value in values:
                    number = _safe_float(value)

                    if number is not None and number > 0:
                        prices.append(number)

                if len(prices) >= 2:
                    return prices

    holdings = _holdings(portfolio)

    for holding in holdings:
        prices = _prices_from_holding(
            holding
        )

        if len(prices) >= 2:
            return prices

    return []


# ============================================================
# SECTOR RISK
# ============================================================

def calculate_sector_risk(
    allocation: Any,
    sector_limit: Optional[float] = None,
) -> list[SectorRisk]:
    """
    Convert Phase 2 sector allocation into Phase 3 risk objects.
    """
    results = []

    by_sector = _get(
        allocation,
        "by_sector",
        [],
    )

    for item in by_sector:
        sector = _get(
            item,
            "name",
            "Unknown",
        )

        exposure = _safe_float(
            _get(
                item,
                "percentage",
                0,
            )
        )

        if exposure is None:
            exposure = 0.0

        limit = sector_limit

        breach = (
            limit is not None
            and exposure > limit
        )

        results.append(
            SectorRisk(
                sector=str(sector),
                exposure_percent=min(
                    100.0,
                    max(0.0, exposure),
                ),
                limit_percent=limit,
                breach=breach,
            )
        )

    return results


# ============================================================
# RISK LEVEL
# ============================================================

def risk_level_from_score(
    score: float,
) -> str:
    """
    Centralized risk classification.
    """
    score = min(
        100.0,
        max(0.0, score),
    )

    if score < 30:
        return "LOW"

    if score < 60:
        return "MEDIUM"

    if score < 80:
        return "HIGH"

    return "CRITICAL"


# ============================================================
# COMPLETE RISK ENGINE
# ============================================================

def calculate_advanced_risk(
    portfolio: Any,
    user_profile: Any,
    concentration: Any = None,
    allocation: Any = None,
) -> AdvancedRiskAssessment:
    """
    Calculate the complete Phase 3 advanced risk assessment.

    Existing Phase 2 concentration and allocation results are
    consumed instead of being recalculated independently.
    """

    user_id = str(
        _get(
            portfolio,
            "user_id",
            _get(
                user_profile,
                "user_id",
                "",
            ),
        )
    )

    # --------------------------------------------------------
    # Phase 2 values
    # --------------------------------------------------------

    if concentration is None:
        try:
            from portfolio.analytics import (
                calculate_concentration,
            )

            concentration = (
                calculate_concentration(
                    portfolio
                )
            )
        except Exception:
            concentration = None

    if allocation is None:
        try:
            from portfolio.analytics import (
                calculate_allocation,
            )

            allocation = calculate_allocation(
                portfolio
            )
        except Exception:
            allocation = None

    concentration_score = _safe_float(
        _get(
            concentration,
            "concentration_score",
            0.0,
        )
    ) or 0.0

    # Phase 2 diversification score
    diversification_score = 100.0

    try:
        from portfolio.analytics import (
            calculate_diversification_score,
        )

        diversification_score = (
            _safe_float(
                calculate_diversification_score(
                    portfolio,
                    concentration,
                )
            )
            or 0.0
        )

    except Exception:
        # If the Phase 2 implementation does not expose this
        # function, use concentration as the inverse signal.
        diversification_score = max(
            0.0,
            100.0 - concentration_score,
        )

    diversification_score = min(
        100.0,
        max(0.0, diversification_score),
    )

    # --------------------------------------------------------
    # Market history
    # --------------------------------------------------------

    prices = _portfolio_price_series(
        portfolio
    )

    volatility = calculate_volatility(
        prices
    )

    drawdown = calculate_maximum_drawdown(
        prices
    )

    liquidity = calculate_liquidity_risk(
        portfolio
    )

    # --------------------------------------------------------
    # User risk profile
    # --------------------------------------------------------

    risk_profile = str(
        _get(
            user_profile,
            "risk_tolerance",
            _get(
                user_profile,
                "risk_profile",
                "MODERATE",
            ),
        )
    ).upper()

    # Profile-specific tolerance multiplier.
    profile_multiplier = {
        "CONSERVATIVE": 1.15,
        "MODERATE": 1.0,
        "AGGRESSIVE": 0.85,
    }.get(
        risk_profile,
        1.0,
    )

    # --------------------------------------------------------
    # Sector risk
    # --------------------------------------------------------

    sector_limit = _safe_float(
        _get(
            user_profile,
            "max_sector_percent",
        )
    )

    sector_risk = calculate_sector_risk(
        allocation,
        sector_limit,
    )

    # --------------------------------------------------------
    # Base risk components
    # --------------------------------------------------------

    concentration_component = (
        concentration_score
    )

    diversification_component = (
        100.0 - diversification_score
    )

    volatility_component = (
        volatility.score
        if volatility.status == "calculated"
        else 0.0
    )

    drawdown_component = (
        drawdown.score
        if drawdown.status == "calculated"
        else 0.0
    )

    liquidity_component = (
        liquidity.score
        if liquidity.status == "calculated"
        else 0.0
    )

    sector_breaches = sum(
        1
        for item in sector_risk
        if item.breach
    )

    sector_component = min(
        100.0,
        sector_breaches * 25.0,
    )

    # --------------------------------------------------------
    # Weighted risk score
    # --------------------------------------------------------

    weighted_score = (
        volatility_component * 0.25
        + drawdown_component * 0.20
        + concentration_component * 0.20
        + diversification_component * 0.15
        + liquidity_component * 0.10
        + sector_component * 0.10
    )

    weighted_score *= profile_multiplier

    risk_score = min(
        100.0,
        max(
            0.0,
            weighted_score,
        ),
    )

    risk_level = risk_level_from_score(
        risk_score
    )

    # --------------------------------------------------------
    # Risk factors
    # --------------------------------------------------------

    factors: list[RiskFactor] = []
    warnings: list[str] = []

    largest_position = _safe_float(
        _get(
            concentration,
            "largest_position_percent",
            0.0,
        )
    ) or 0.0

    max_position = _safe_float(
        _get(
            user_profile,
            "max_position_percent",
        )
    )

    if (
        max_position is not None
        and largest_position > max_position
    ):
        factors.append(
            RiskFactor(
                code="HIGH_CONCENTRATION",
                severity="HIGH",
                message=(
                    "Largest portfolio position "
                    "exceeds the configured user limit."
                ),
            )
        )

        warnings.append(
            "Portfolio concentration exceeds the user's preferred limit."
        )

    if (
        volatility.status == "calculated"
        and volatility.annualized_volatility is not None
        and volatility.annualized_volatility > 30
    ):
        factors.append(
            RiskFactor(
                code="HIGH_VOLATILITY",
                severity="HIGH",
                message=(
                    "Portfolio volatility is elevated."
                ),
            )
        )

        warnings.append(
            "Portfolio volatility is high."
        )

    if (
        drawdown.status == "calculated"
        and drawdown.maximum_drawdown is not None
        and drawdown.maximum_drawdown > 20
    ):
        factors.append(
            RiskFactor(
                code="HIGH_DRAWDOWN",
                severity="HIGH",
                message=(
                    "Historical maximum drawdown is elevated."
                ),
            )
        )

        warnings.append(
            "Historical maximum drawdown exceeds 20%."
        )

    if diversification_score < 40:
        factors.append(
            RiskFactor(
                code="LOW_DIVERSIFICATION",
                severity="MEDIUM",
                message=(
                    "Portfolio diversification is weak."
                ),
            )
        )

        warnings.append(
            "Portfolio diversification is low."
        )

    if sector_breaches > 0:
        factors.append(
            RiskFactor(
                code="HIGH_SECTOR_EXPOSURE",
                severity="HIGH",
                message=(
                    "One or more sectors exceed "
                    "the configured exposure limit."
                ),
            )
        )

        warnings.append(
            "Sector exposure exceeds the configured limit."
        )

    if liquidity.status == "calculated":
        if liquidity.score >= 60:
            factors.append(
                RiskFactor(
                    code="LIQUIDITY_RISK",
                    severity="HIGH",
                    message=(
                        "Portfolio liquidity risk is elevated."
                    ),
                )
            )

            warnings.append(
                "Portfolio liquidity risk is elevated."
            )

    elif liquidity.status in {
        "unavailable",
        "insufficient_data",
    }:
        warnings.append(
            "Liquidity risk could not be fully assessed from the available data."
        )

    # --------------------------------------------------------
    # Data quality
    # --------------------------------------------------------

    quality_states = [
        volatility.status,
        drawdown.status,
        liquidity.status,
    ]

    if all(
        state == "calculated"
        for state in quality_states
    ):
        overall_quality = "complete"

    elif any(
        state == "calculated"
        for state in quality_states
    ):
        overall_quality = "partial"

    else:
        overall_quality = "insufficient_data"

    data_quality = RiskDataQuality(
        volatility=volatility.status,
        drawdown=drawdown.status,
        liquidity=liquidity.status,
        overall=overall_quality,
    )

    return AdvancedRiskAssessment(
        user_id=user_id,
        risk_score=round(
            risk_score,
            2,
        ),
        risk_level=risk_level,
        volatility=volatility,
        drawdown=drawdown,
        liquidity=liquidity,
        concentration_score=round(
            concentration_score,
            2,
        ),
        diversification_score=round(
            diversification_score,
            2,
        ),
        sector_risk=sector_risk,
        risk_factors=factors,
        warnings=warnings,
        data_quality=data_quality,
    )