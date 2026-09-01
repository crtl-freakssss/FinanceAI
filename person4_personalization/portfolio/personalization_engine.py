from models.personalization import PersonalizationContext
from profile.service import get_profile, get_preferences, get_constraints
from profile.risk_profile import calculate_profile_risk_score, calculate_combined_risk_score, get_risk_level
from profile.suitability import calculate_suitability
from portfolio.service import get_portfolio
from portfolio.intelligence import calculate_portfolio_intelligence
from app_logging.structured_logger import get_logger

logger = get_logger("personalization_engine")


def build_personalization_context(
    user_id: str,
    symbol: str,
    sector: str,
    market_cap: str = "ANY",
    volatility: str = "MEDIUM",
) -> PersonalizationContext:
    logger.debug(f"Starting personalization evaluation for user '{user_id}', symbol '{symbol}'", extra={"user_id": user_id, "symbol": symbol})
    # 1. Load the user's profile
    profile = get_profile(user_id)
    if not profile:
        raise ValueError(f"User '{user_id}' not found")

    # 2. Load the user's preferences
    preferences = get_preferences(user_id) or profile.preferences

    # 3. Load the user's investment constraints
    constraints = get_constraints(user_id) or profile.constraints

    # 4. Load the user's portfolio
    portfolio = get_portfolio(user_id)

    # 5. Calculate portfolio intelligence
    portfolio_intel = calculate_portfolio_intelligence(
        portfolio=portfolio,
        symbol=symbol,
        sector=sector,
    )
    position_exposure_pct = portfolio_intel.get("position_exposure_percent", 0.0)

    # 6. Calculate the user's profile risk score
    profile_risk_score = calculate_profile_risk_score(profile)

    # 7. Calculate the combined risk score
    combined_risk_score = calculate_combined_risk_score(
        profile_risk_score=profile_risk_score,
        volatility=volatility,
        market_cap=market_cap,
    )
    risk_lvl = get_risk_level(combined_risk_score)

    # 8. Calculate suitability
    suitability_assessment = calculate_suitability(
        profile=profile,
        preferences=preferences,
        constraints=constraints,
        symbol=symbol,
        sector=sector,
        volatility=volatility,
        combined_risk_score=combined_risk_score,
        position_exposure_pct=position_exposure_pct,
    )

    # 9. Return PersonalizationContext
    return PersonalizationContext(
        user_id=profile.user_id,
        risk_tolerance=profile.risk_tolerance,
        risk_capacity=profile.risk_capacity,
        investment_horizon=profile.investment_horizon,
        investor_style=profile.investor_style,
        capital=profile.capital,
        portfolio=portfolio,
        portfolio_snapshot=portfolio,
        symbol=symbol,
        sector=sector,
        market_cap=market_cap,
        volatility=volatility,
        position_exposure_percent=position_exposure_pct,
        risk_score=round(combined_risk_score, 2),
        risk_level=risk_lvl,
        suitability_score=suitability_assessment.suitability_score,
        suitability=suitability_assessment.suitability,
        reasons=suitability_assessment.reasons,
        warnings=suitability_assessment.warnings,
        constraint_breaches=suitability_assessment.constraint_breaches,
    )
