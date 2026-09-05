from models.preferences import (
    MarketCapPreference,
    UserPreferences,
    VolatilityPreference,
)


def sector_preference_score(
    preferences: UserPreferences,
    sector: str,
) -> tuple[float, list[str], list[str]]:
    normalized_sector = sector.strip().lower()

    reasons: list[str] = []
    warnings: list[str] = []

    if normalized_sector in preferences.normalized_excluded_sectors:
        return (
            0.0,
            [],
            [f"{sector} is explicitly excluded by the user."],
        )

    if (
        preferences.normalized_preferred_sectors
        and normalized_sector
        in preferences.normalized_preferred_sectors
    ):
        reasons.append(f"{sector} is one of the user's preferred sectors.")
        return 100.0, reasons, warnings

    if preferences.normalized_preferred_sectors:
        reasons.append(
            f"{sector} is not among the user's preferred sectors."
        )
        return 55.0, reasons, warnings

    return 75.0, reasons, warnings


def market_cap_preference_score(
    preferences: UserPreferences,
    market_cap: str,
) -> tuple[float, list[str], list[str]]:
    normalized = market_cap.strip().upper()

    if MarketCapPreference.ANY in preferences.preferred_market_caps:
        return 75.0, [], []

    try:
        market_cap_enum = MarketCapPreference(normalized)
    except ValueError:
        return (
            50.0,
            [],
            [f"Unknown market-cap category: {market_cap}."],
        )

    if market_cap_enum in preferences.preferred_market_caps:
        return 100.0, [
            f"{market_cap} market-cap matches the user's preference."
        ], []

    return (
        45.0,
        [f"{market_cap} market-cap is outside the user's preferred categories."],
        [],
    )


def volatility_preference_score(
    preferences: UserPreferences,
    volatility: str,
) -> tuple[float, list[str], list[str]]:
    normalized = volatility.strip().upper()

    if preferences.volatility_preference == VolatilityPreference.ANY:
        return 75.0, [], []

    if normalized == preferences.volatility_preference.value:
        return (
            100.0,
            [f"{volatility} volatility matches the user's preference."],
            [],
        )

    return (
        35.0,
        [
            f"{volatility} volatility does not match the user's "
            f"{preferences.volatility_preference.value} preference."
        ],
        [],
    )    