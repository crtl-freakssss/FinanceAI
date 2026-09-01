"""
StIC Portfolio Adapter
Transforms raw Person 4 Portfolio Intelligence data into the SI Terminal UI layout and models.
"""

from typing import Any, Dict, List
from stic.client.stic_person4_client import StICPerson4Client
from stic.schemas.stic_models import (
    SITerminalHolding,
    SITerminalSectorAllocation,
    SITerminalPortfolioView,
)


class StICPortfolioAdapter:
    """Adapts Person 4 API responses into SI Terminal portfolio models."""

    def __init__(self, client: StICPerson4Client):
        self.client = client

    def get_terminal_portfolio_view(self, user_id: str) -> SITerminalPortfolioView:
        """
        Fetches portfolio, analysis, and health data from Person 4 API,
        then transforms it into the SI Terminal UI layout.
        """
        # Fetch from Person 4 REST endpoints via client
        portfolio_raw = self.client.get_portfolio(user_id)
        analysis_raw = self.client.get_portfolio_analysis(user_id)

        holdings_raw = portfolio_raw.get("holdings", [])
        total_val = float(analysis_raw.get("total_value", 0.0))
        holdings_val = float(analysis_raw.get("holdings_value", 0.0))
        cash_val = float(analysis_raw.get("cash_value", 0.0))

        # Format holdings table
        terminal_holdings: List[SITerminalHolding] = []
        for h in holdings_raw:
            sym = h.get("symbol", "")
            shares = float(h.get("shares", 0.0))
            avg_price = float(h.get("avg_price", 0.0))
            cur_price = float(h.get("current_price", avg_price))
            val = float(h.get("value", shares * cur_price))
            pnl_amt = float(h.get("pnl", val - (shares * avg_price)))
            pnl_pct = float(h.get("pnl_percent", ((cur_price - avg_price) / avg_price * 100.0) if avg_price > 0 else 0.0))
            weight = round((val / total_val * 100.0), 2) if total_val > 0 else 0.0

            terminal_holdings.append(
                SITerminalHolding(
                    symbol=sym,
                    shares=shares,
                    avg_price=avg_price,
                    current_price=cur_price,
                    total_value=round(val, 2),
                    pnl_amount=round(pnl_amt, 2),
                    pnl_percent=round(pnl_pct, 2),
                    weight_percent=weight,
                    sector=h.get("sector", "General"),
                )
            )

        # Sector breakdown
        alloc_data = analysis_raw.get("allocation", {})
        by_sector = alloc_data.get("by_sector", [])
        sector_breakdown = [
            SITerminalSectorAllocation(
                sector=sec.get("sector", "Other"),
                value=float(sec.get("value", 0.0)),
                percentage=float(sec.get("percentage", 0.0)),
            )
            for sec in by_sector
        ]

        conc = analysis_raw.get("concentration", {})
        health = analysis_raw.get("health", {})
        risk = analysis_raw.get("risk", {})

        return SITerminalPortfolioView(
            user_id=user_id,
            total_value=round(total_val, 2),
            holdings_value=round(holdings_val, 2),
            cash_value=round(cash_val, 2),
            risk_level=str(risk.get("risk_level", "MEDIUM")),
            health_score=float(health.get("health_score", 75.0)),
            health_status=str(health.get("status", "HEALTHY")),
            diversification_score=float(health.get("diversification_score", 70.0)),
            top_holding_symbol=str(conc.get("top_holding_symbol", "N/A")),
            top_holding_percent=float(conc.get("top_holding_percent", 0.0)),
            sector_breakdown=sector_breakdown,
            holdings=terminal_holdings,
            warnings=health.get("warnings", []),
        )
