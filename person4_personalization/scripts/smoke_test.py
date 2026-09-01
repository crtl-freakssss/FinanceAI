"""
Quick standalone smoke test script for Person 4 Personalization & Portfolio Intelligence service.
Usage:
    python scripts/smoke_test.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app import app
from examples.person4_client import Person4Client


def main():
    print("==================================================")
    print("[RUNNING] Person 4 - Live API Smoke Test & Readiness Check")
    print("==================================================")

    client = TestClient(app)
    sdk = Person4Client(client_session=client)

    # 1. Health & Readiness
    print("1. Checking Health & Readiness...")
    health = sdk.get_health()
    readiness = sdk.get_readiness()
    print(f"   Status: {health['status']}, DB: {readiness['database']}")

    # 2. User & Portfolio
    print("2. Fetching Demo User 'moderate_001'...")
    profile = sdk.get_profile("moderate_001")
    portfolio = sdk.get_portfolio("moderate_001")
    print(f"   Risk Tolerance: {profile['risk_tolerance']}, Holdings: {len(portfolio['holdings'])}")

    # 3. Portfolio Intelligence
    print("3. Calculating Portfolio Analysis...")
    analysis = sdk.get_portfolio_analysis("moderate_001")
    print(f"   Total Value: Rs. {analysis['total_value']}, Health Score: {analysis['health']['health_score']}")

    # 4. Advanced Risk Engine
    print("4. Executing Advanced Risk Engine...")
    adv_risk = sdk.get_advanced_risk("moderate_001")
    print(f"   Risk Level: {adv_risk['risk_level']}, Volatility: {adv_risk['volatility']['annualized_volatility']}%")

    # 5. Personalization Context
    print("5. Generating Personalization Context for RELIANCE.NS...")
    ctx = sdk.get_personalization_context(
        user_id="moderate_001",
        symbol="RELIANCE.NS",
        sector="Energy",
        market_cap="LARGE",
        volatility="HIGH",
    )
    print(f"   Suitability: {ctx['suitability']} (Score: {ctx['suitability_score']}/100)")
    print(f"   Combined Risk Score: {ctx['risk_score']}/100")

    print("\n==================================================")
    print("[SUCCESS] All Person 4 Services Ready & Verified!")
    print("==================================================")


if __name__ == "__main__":
    main()
