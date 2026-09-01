# Person 4 Public Integration Contract (API v1)

## Overview
**Person 4 (Personalization & Portfolio Intelligence)** provides the personalization context, portfolio intelligence, advanced quantitative risk analytics, and behavioral profiling services for the Hackverse AI financial system.

All team members must communicate with Person 4 **strictly through the HTTP API** or the provided [Person4Client](file:///c:/Users/yagna/OneDrive/Documents/hackverse/person4_personalization/examples/person4_client.py). No internal Python modules should be directly imported by other agents.

- **Base URL:** `http://localhost:8000`
- **API Version:** `v1` (`/api/v1/...`)
- **Interactive Documentation:** `http://localhost:8000/docs`
- **Machine-Readable OpenAPI Spec:** `http://localhost:8000/openapi.json`

---

## HOW THE OTHER 3 TEAM MEMBERS USE PERSON 4

### 1. Person 1 (Agent & Recommendation Synthesis Layer)
**Goal:** Retrieve user constraints, risk tolerances, suitability scores, and portfolio exposure before generating or synthesizing final stock recommendations.

**Primary Endpoint:**
```http
GET /api/v1/users/{user_id}/context/{symbol}?sector={sector}&market_cap={market_cap}&volatility={volatility}
```

**Example Curl:**
```bash
curl -X GET "http://localhost:8000/api/v1/users/moderate_001/context/RELIANCE.NS?sector=Energy&market_cap=LARGE&volatility=HIGH"
```

**Response Format (Pydantic `PersonalizationContext`):**
```json
{
  "user_id": "moderate_001",
  "risk_tolerance": "MODERATE",
  "risk_capacity": "MEDIUM",
  "investment_horizon": "MEDIUM_TERM",
  "investor_style": "BALANCED",
  "capital": 500000.0,
  "symbol": "RELIANCE.NS",
  "sector": "Energy",
  "market_cap": "LARGE",
  "volatility": "HIGH",
  "position_exposure_percent": 27.59,
  "risk_score": 62.0,
  "risk_level": "HIGH",
  "suitability_score": 67.5,
  "suitability": "CAUTION",
  "reasons": [
    "Combined risk score is in the upper moderate zone.",
    "Stock aligns with moderate investor profile."
  ],
  "warnings": [
    "Existing position exposure is 27.59%, which is relatively high."
  ],
  "constraint_breaches": []
}
```

---

### 2. Person 2 (Quantitative Models & Valuation Layer)
**Goal:** Query comprehensive risk metrics, volatility estimates, historical drawdown, and sector concentrations.

**Primary Endpoint:**
```http
GET /api/v1/users/{user_id}/portfolio/risk/advanced
```

**Example Curl:**
```bash
curl -X GET "http://localhost:8000/api/v1/users/moderate_001/portfolio/risk/advanced"
```

**Response Format (Pydantic `AdvancedRiskAssessment`):**
```json
{
  "user_id": "moderate_001",
  "risk_score": 52.5,
  "risk_level": "MEDIUM",
  "risk_factors": [
    {
      "code": "VOLATILITY_FACTOR",
      "name": "Historical Volatility Risk",
      "risk_level": "MEDIUM",
      "score": 48.0,
      "description": "Historical annualized volatility across portfolio assets is moderate."
    }
  ],
  "volatility": {
    "annualized_volatility": 18.45,
    "confidence": 0.85
  },
  "drawdown": {
    "maximum_drawdown_percent": 12.3,
    "recovery_status": "RECOVERED"
  },
  "liquidity": {
    "liquidity_score": 85.0,
    "cash_ratio_percent": 14.5
  },
  "sector_risk": {
    "top_sector": "Energy",
    "top_sector_percent": 42.1
  },
  "data_quality": {
    "status": "complete"
  }
}
```

---

### 3. Person 3 (Frontend & User Dashboard Layer)
**Goal:** Render user portfolio dashboard, allocation charts, concentration gauges, portfolio health status, and behavioral trade analysis.

#### A. Complete Portfolio Analysis
```http
GET /api/v1/users/{user_id}/portfolio/analysis
```
```bash
curl -X GET "http://localhost:8000/api/v1/users/moderate_001/portfolio/analysis"
```
**Response Format (`PortfolioAnalysis`):**
```json
{
  "user_id": "moderate_001",
  "total_value": 435000.0,
  "holdings_value": 372000.0,
  "cash_value": 63000.0,
  "allocation": {
    "by_symbol": [
      {"symbol": "RELIANCE.NS", "value": 120000.0, "percentage": 27.59},
      {"symbol": "TCS.NS", "value": 140000.0, "percentage": 32.18},
      {"symbol": "ITC.NS", "value": 112000.0, "percentage": 25.75}
    ],
    "by_sector": [
      {"sector": "Technology", "value": 140000.0, "percentage": 32.18},
      {"sector": "Energy", "value": 120000.0, "percentage": 27.59},
      {"sector": "Consumer Defensive", "value": 112000.0, "percentage": 25.75}
    ]
  },
  "concentration": {
    "concentration_score": 32.4,
    "top_holding_symbol": "TCS.NS",
    "top_holding_percent": 32.18
  },
  "risk": {
    "risk_score": 45.0,
    "risk_level": "MEDIUM"
  },
  "health": {
    "health_score": 78.5,
    "status": "HEALTHY",
    "diversification_score": 75.0,
    "warnings": []
  }
}
```

#### B. Investor Behavioral Profile
```http
GET /api/v1/users/{user_id}/investor-profile
```
```bash
curl -X GET "http://localhost:8000/api/v1/users/moderate_001/investor-profile"
```
**Response Format (`InvestorProfileAssessment`):**
```json
{
  "user_id": "moderate_001",
  "declared_risk_profile": "MODERATE",
  "observed_risk_profile": "MODERATE",
  "investor_type": "BALANCED_INVESTOR",
  "alignment": "ALIGNED",
  "behaviour_score": 42.0,
  "profile_confidence": 90.0,
  "recommendations": [
    "Observed behaviour is broadly consistent with the available investor profile data."
  ],
  "behaviour_flags": []
}
```

---

## Public API Endpoints Reference Table

| Method | Endpoint | Description | Request Query / Body | Expected Status |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | Root service health | None | `200 OK` |
| `GET` | `/api/v1/health` | Versioned service health | None | `200 OK` |
| `GET` | `/api/v1/readiness` | Live database connectivity check | None | `200 OK` / `503 Service Unavailable` |
| `GET` | `/api/v1/metrics` | Observability & latency telemetry | None | `200 OK` |
| `GET` | `/api/v1/users/{user_id}/profile` | User risk profile & preferences | Path: `user_id` | `200 OK` / `404 Not Found` |
| `GET` | `/api/v1/users/{user_id}/portfolio` | Holdings & cash balances | Path: `user_id` | `200 OK` / `404 Not Found` |
| `GET` | `/api/v1/users/{user_id}/context/{symbol}` | Personalization context for recommendation | Path: `user_id`, `symbol`; Query: `sector`, `market_cap`, `volatility` | `200 OK` / `404 Not Found` / `422 Validation Error` |
| `GET` | `/api/v1/users/{user_id}/portfolio/analysis` | Complete analytics & health | Path: `user_id` | `200 OK` / `404 Not Found` |
| `GET` | `/api/v1/users/{user_id}/portfolio/allocation` | Asset & sector allocation breakdown | Path: `user_id` | `200 OK` / `404 Not Found` |
| `GET` | `/api/v1/users/{user_id}/portfolio/concentration` | Herfindahl score & top positions | Path: `user_id` | `200 OK` / `404 Not Found` |
| `GET` | `/api/v1/users/{user_id}/portfolio/risk` | Baseline portfolio risk score | Path: `user_id` | `200 OK` / `404 Not Found` |
| `GET` | `/api/v1/users/{user_id}/portfolio/risk/advanced` | Quantitative volatility & drawdown | Path: `user_id` | `200 OK` / `404 Not Found` |
| `GET` | `/api/v1/users/{user_id}/portfolio/health` | Diversification health & warnings | Path: `user_id` | `200 OK` / `404 Not Found` |
| `GET` | `/api/v1/users/{user_id}/portfolio/exposure/{symbol}` | Single stock & sector exposure | Path: `user_id`, `symbol`; Query: `sector` | `200 OK` / `404 Not Found` |
| `GET` | `/api/v1/users/{user_id}/behavior` | Behavioral pattern assessment | Path: `user_id` | `200 OK` / `404 Not Found` |
| `GET` | `/api/v1/users/{user_id}/investor-profile` | Alignment between declared & observed | Path: `user_id` | `200 OK` / `404 Not Found` |
| `GET` | `/api/v1/db/users` | Paginated user records | Query: `skip` (default 0), `limit` (default 20, max 100) | `200 OK` / `422 Validation Error` |
| `POST` | `/api/v1/db/users` | Create user record | JSON: `{"user_id": str, "name": str}` | `200 OK` / `400 Bad Request` / `422 Validation Error` |
| `POST` | `/api/v1/db/sessions` | Persist analysis session | JSON: `{"user_id": str, "symbol": str, "analysis_type": str, "result_data": dict}` | `200 OK` / `422 Validation Error` |
| `POST` | `/api/v1/db/logs` | Append analysis log | JSON: `{"user_id": str, "message": str, "level": str}` | `200 OK` / `422 Validation Error` |

---

## Standard Error Response Format
All errors return clean, machine-readable JSON payloads accompanied by correlation headers:
- `X-Request-ID`: Trace identifier for debugging.
- `X-Process-Time`: Request duration in milliseconds.

```json
{
  "detail": "User 'unknown_user_999' not found"
}
```

HTTP Status Codes:
- `400 Bad Request`: Empty or invalid payload fields.
- `404 Not Found`: Unknown user or portfolio.
- `413 Content Too Large`: Request body exceeds 1MB.
- `422 Unprocessable Entity`: Schema/regex validation violation.
- `429 Too Many Requests`: Client exceeded rate limit window.
- `500 Internal Server Error`: Sanitized internal error (no stack traces leaked).
