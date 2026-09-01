from models.profile import UserProfile


def calculate_profile_risk_score(profile: UserProfile) -> float:
    base_scores = {
        "CONSERVATIVE": 25.0,
        "MODERATE": 50.0,
        "AGGRESSIVE": 80.0,
    }
    score = base_scores.get(profile.risk_tolerance.upper(), 50.0)

    # Adjust for risk capacity
    capacity_adj = {
        "LOW": -5.0,
        "MEDIUM": 0.0,
        "HIGH": 5.0,
    }
    score += capacity_adj.get(profile.risk_capacity.upper(), 0.0)

    # Adjust for horizon
    horizon_adj = {
        "SHORT_TERM": -5.0,
        "MEDIUM_TERM": 0.0,
        "LONG_TERM": 5.0,
    }
    score += horizon_adj.get(profile.investment_horizon.upper(), 0.0)

    return max(0.0, min(100.0, score))


def calculate_combined_risk_score(
    profile_risk_score: float,
    volatility: str = "MEDIUM",
    market_cap: str = "ANY",
) -> float:
    vol_weights = {
        "LOW": -10.0,
        "MEDIUM": 0.0,
        "HIGH": 15.0,
    }
    cap_weights = {
        "LARGE": -5.0,
        "MID": 0.0,
        "SMALL": 10.0,
        "MICRO": 15.0,
        "ANY": 0.0,
    }
    score = profile_risk_score + vol_weights.get(volatility.upper(), 0.0) + cap_weights.get(market_cap.upper(), 0.0)
    return max(0.0, min(100.0, score))


def get_risk_level(risk_score: float) -> str:
    if risk_score <= 35.0:
        return "LOW"
    elif risk_score <= 65.0:
        return "MEDIUM"
    else:
        return "HIGH"
