from typing import List, Tuple
from models.constraints import InvestmentConstraints


def evaluate_constraints(
    constraints: InvestmentConstraints,
    symbol: str,
    sector: str,
    position_exposure_pct: float = 0.0,
) -> Tuple[List[str], List[str]]:
    breaches = []
    warnings = []

    if not constraints:
        return breaches, warnings

    if sector in constraints.excluded_sectors:
        breaches.append(f"Sector '{sector}' is in user's excluded sectors list.")

    if symbol in constraints.restricted_symbols:
        breaches.append(f"Symbol '{symbol}' is restricted by investment policy.")

    if position_exposure_pct > constraints.max_single_position_pct:
        breaches.append(
            f"Position exposure {position_exposure_pct:.1f}% exceeds maximum single position limit of {constraints.max_single_position_pct:.1f}%."
        )
    elif position_exposure_pct > constraints.max_single_position_pct * 0.8:
        warnings.append(
            f"Position exposure {position_exposure_pct:.1f}% is nearing max single position limit of {constraints.max_single_position_pct:.1f}%."
        )

    return breaches, warnings
