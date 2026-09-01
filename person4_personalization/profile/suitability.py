from typing import List
from models.profile import UserProfile
from models.preferences import UserPreferences
from models.constraints import InvestmentConstraints
from models.suitability import SuitabilityAssessment, SuitabilityLevel
from profile.constraints import evaluate_constraints


def calculate_suitability(
    profile: UserProfile,
    preferences: UserPreferences,
    constraints: InvestmentConstraints,
    symbol: str,
    sector: str,
    volatility: str,
    combined_risk_score: float,
    position_exposure_pct: float = 0.0,
) -> SuitabilityAssessment:
    reasons: List[str] = []
    warnings: List[str] = []
    
    breaches, constraint_warns = evaluate_constraints(
        constraints=constraints,
        symbol=symbol,
        sector=sector,
        position_exposure_pct=position_exposure_pct,
    )
    warnings.extend(constraint_warns)

    # Base suitability calculation from alignment with user risk profile
    if profile.risk_tolerance == "CONSERVATIVE":
        if volatility == "HIGH":
            base_score = 30.0
            warnings.append("High volatility assets carry excessive risk for conservative profile.")
        elif volatility == "MEDIUM":
            base_score = 65.0
            reasons.append("Moderate risk asset matches conservative growth portion.")
        else:
            base_score = 90.0
            reasons.append("Low volatility asset aligns well with conservative preservation objective.")
    elif profile.risk_tolerance == "MODERATE":
        if volatility == "HIGH":
            base_score = 55.0
            reasons.append("High volatility is acceptable in moderate allocation.")
        elif volatility == "MEDIUM":
            base_score = 85.0
            reasons.append("Asset risk level aligns well with moderate risk tolerance.")
        else:
            base_score = 75.0
            reasons.append("Asset provides stable ballast to portfolio.")
    else:  # AGGRESSIVE
        if volatility == "HIGH":
            base_score = 90.0
            reasons.append("High volatility asset aligns well with aggressive growth mandate.")
        elif volatility == "MEDIUM":
            base_score = 75.0
            reasons.append("Asset provides solid core growth with managed volatility.")
        else:
            base_score = 60.0
            reasons.append("Low volatility asset offers capital stability.")

    # Preferred sectors bonus
    if preferences and sector in preferences.preferred_sectors:
        base_score += 10.0
        reasons.append(f"Sector '{sector}' is in user's preferred sectors list.")

    # Deductions for breaches
    if breaches:
        base_score = max(0.0, base_score - 40.0 * len(breaches))
        warnings.extend(breaches)

    final_score = max(0.0, min(100.0, base_score))

    if not reasons:
        reasons.append(f"Investment evaluated for user risk tolerance '{profile.risk_tolerance}'.")

    if breaches:
        suitability_label = SuitabilityLevel.UNSUITABLE.value
    elif final_score >= 70.0:
        suitability_label = SuitabilityLevel.SUITABLE.value
    elif final_score >= 40.0:
        suitability_label = SuitabilityLevel.CAUTION.value
    else:
        suitability_label = SuitabilityLevel.UNSUITABLE.value

    return SuitabilityAssessment(
        suitability_score=round(final_score, 2),
        suitability=suitability_label,
        reasons=reasons,
        warnings=warnings,
        constraint_breaches=breaches,
    )
