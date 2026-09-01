from typing import Any, Dict, Optional


def calculate_portfolio_intelligence(
    portfolio: Optional[Dict[str, Any]],
    symbol: str,
    sector: str,
) -> Dict[str, Any]:
    if not portfolio:
        return {
            "total_value": 0.0,
            "position_exposure_percent": 0.0,
            "sector_exposure_percent": 0.0,
            "existing_shares": 0,
        }

    total_value = float(portfolio.get("total_value", 0.0))
    holdings = portfolio.get("holdings", [])

    position_value = 0.0
    sector_value = 0.0
    existing_shares = 0

    for holding in holdings:
        h_val = float(holding.get("value", 0.0))
        if holding.get("symbol") == symbol:
            position_value += h_val
            existing_shares += int(holding.get("shares", 0))
        if holding.get("sector") == sector:
            sector_value += h_val

    position_pct = (position_value / total_value * 100.0) if total_value > 0 else 0.0
    sector_pct = (sector_value / total_value * 100.0) if total_value > 0 else 0.0

    return {
        "total_value": total_value,
        "position_exposure_percent": round(position_pct, 2),
        "sector_exposure_percent": round(sector_pct, 2),
        "existing_shares": existing_shares,
    }
