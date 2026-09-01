# StIC MCP / SI Terminal & Person 4 Personalization Integration Plan

## 1. Executive Summary & Objectives
This document establishes the architecture, boundaries, and integration mechanics for connecting the **StIC MCP / SI Terminal Intelligence Platform** (Stitch Design Project ID: `15879964569093521067`) with the completed **Person 4 Personalization & Portfolio Intelligence Service**.

### Core Tenets
1. **Zero Rebuilding**: Neither Person 4 nor the StIC design system will be rewritten or duplicated.
2. **Person 4 Remains Single Source of Truth**: User profiles, portfolios, risk engines, behavioral models, suitability context, security, logging, and database persistence reside exclusively in Person 4.
3. **Public HTTP API Integration Boundary**: StIC interacts with Person 4 strictly via the versioned REST API (`/api/v1/...`) or typed HTTP client adapters, ensuring loose coupling and clean boundary separation.
4. **Design System & MCP Harmonization**: The StIC design system (High-Precision Terminal theme, Dark mode `#051424`, Desaturated Teal `#2DD4BF`, Inter/JetBrains Mono typography) is dynamically powered by Person 4 live endpoints.

---

## 2. Architecture & System Inspection

### A. Person 4 (Personalization & Portfolio Intelligence)
- **Primary Entry Points**: `person4_personalization/app.py` (FastAPI server on port 8000), `person4_personalization/api/v1_routes.py`
- **Core Capabilities**:
  - Phase 1: Core Personalization Engine (Suitability scoring, risk matching, guardrails)
  - Phase 2: Portfolio Intelligence (Allocation, Herfindahl concentration, diversification health)
  - Phase 3: Advanced Quantitative Risk (Annualized volatility, max drawdown, historical stress factors)
  - Phase 4: Behavioral Profiling (Trade cadence, holding periods, behavioral archetype alignment)
  - Phase 5: Database & Persistence (SQLAlchemy models: Users, Profiles, Portfolios, Analysis Sessions, Audit Logs)
  - Phase 6: Production API (Versioned `/api/v1/`, OpenAPI 3.0, custom error schemas)
  - Phase 7: Logging & Telemetry (Structured JSON logger, X-Request-ID tracing, in-memory latency metrics)
  - Phase 8: Security & Validation (Finite number validation, regex sanitization, rate limiting, security headers)
  - Phase 9: Integration Contract (`examples/person4_client.py`, `docs/integration_contract.md`)
  - Phase 10: Hackathon Demo Suite (`mock_data/`, `tests/test_demo_flow.py`, `scripts/smoke_test.py`)
- **Dependencies**: `fastapi`, `uvicorn`, `pydantic`, `sqlalchemy`, `pytest`, `httpx`
- **Database**: SQLite (`personalization.db`)

### B. StIC MCP / SI Terminal Platform
- **Stitch Project ID**: `15879964569093521067` ("SI Terminal Intelligence Platform")
- **Design System Tokens**:
  - Theme: High-Precision Intelligence (Glassmorphism + Dark Terminal)
  - Background: `#051424` / Surface: `#122131` / Border: `#252A30` / Outline: `#3c4a46`
  - Accent (AI): Desaturated Teal (`#2DD4BF` / `#57f1db`)
  - Bullish / Bearish: Muted Emerald (`#10B981`) / Coral Red (`#F43F5E`)
  - Typography: `Inter` (UI/Headlines) & `JetBrains Mono` (Financial data, tickers, metrics)
- **Screens Identified**:
  1. `SI Terminal - Dashboard` (`1306827099d548d3bf58c9e9f6906178`): Overview, top cards, quick metrics
  2. `SI Terminal - Portfolio` (`1734dd1519464039808c52c8ddf7ac98`): Holdings table, asset/sector exposure, performance SVG chart
  3. `SI Terminal - AI Insights` (`9c2f77e131c34fe7bbc64ad2465d19b3`): Live AI synthesis, technical/fundamental indicators, market sentiment meter, consensus action
  4. `SI Terminal - Stock Analysis` (`6c0a397e522d4cadb2120f29206788e1`): Single asset deep-dive
  5. `SI Terminal - Market Overview` (`5a10ca669fdc4ab9b8a27192c7f65c4d`): Macro indicators
  6. `SI Terminal - Wallet` (`5b036d234150451e9fa3a0973bb87fd2`): Cash and funding status
  7. `SI Terminal - Watchlist` (`10798dffa01e42a5a5d5036a08249328`): Monitored tickers
  8. `SI Terminal - Settings` (`4e94d5dbe00140faa950ef261a6e40a8`): User configuration & risk preferences

---

## 3. Ownership & Separation of Concerns

| Responsibility | Owner | Integration Mechanism |
| :--- | :--- | :--- |
| User Profile & Preferences | Person 4 | `GET /api/v1/users/{user_id}/profile` |
| Portfolio Holdings & Cash | Person 4 | `GET /api/v1/users/{user_id}/portfolio` |
| Allocation & Concentration Analytics | Person 4 | `GET /api/v1/users/{user_id}/portfolio/allocation`, `/concentration` |
| Risk Score & Quantitative Drawdown | Person 4 | `GET /api/v1/users/{user_id}/portfolio/risk/advanced` |
| Portfolio Health & Diversification | Person 4 | `GET /api/v1/users/{user_id}/portfolio/health` |
| Single Asset Personalization Context | Person 4 | `GET /api/v1/users/{user_id}/context/{symbol}` |
| Behavioral Profiling & Archetypes | Person 4 | `GET /api/v1/users/{user_id}/investor-profile` |
| Audit Logging & Session Persistence | Person 4 | `POST /api/v1/db/sessions`, `POST /api/v1/db/logs` |
| UI Design System & Terminal Layout | StIC | Tailwind tokens, glassmorphism, responsive views |
| MCP Tool Exposure for Agents | StIC Adapter | Standalone MCP Server exposing Person 4 tools |
| Dynamic UI Data Binding | StIC UI Bridge | Consumes Person 4 REST APIs via `fetch`/HTTP |

---

## 4. End-to-End Data Flow Architecture

```
                  ┌────────────────────────────────────────┐
                  │      StIC MCP & SI Terminal UI         │
                  │ (Figma / Stitch: 15879964569093521067) │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼ HTTP REST (JSON)
                  ┌────────────────────────────────────────┐
                  │          Person 4 Public API           │
                  │       http://localhost:8000/api/v1     │
                  └───────────────────┬────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        ▼                             ▼                             ▼
  ┌───────────┐                 ┌───────────┐                 ┌───────────┐
  │  Profile  │                 │ Portfolio │                 │ Behaviour │
  │  Engine   │                 │ Analytics │                 │ Profiler  │
  └─────┬─────┘                 └─────┬─────┘                 └─────┬─────┘
        │                             │                             │
        └─────────────────────────────┼─────────────────────────────┘
                                      ▼
                        ┌───────────────────────────┐
                        │   Personalization Engine  │
                        │    & Advanced Risk Core   │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │ Structured JSON Response  │
                        │ + Tracing (X-Request-ID)  │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │  Rendered SI Terminal Dashboard / UI   │
                  │    & Agent Synthesis (Person 1 / 2)    │
                  └────────────────────────────────────────┘
```

---

## 5. StIC MCP Tools & Adapters Specification

A standalone, non-intrusive module `stic/` will be structured as follows:

```
person4_personalization/
  stic/
    __init__.py
    config.py                  # StIC configuration (API URLs, Project ID)
    client/
      __init__.py
      stic_person4_client.py   # Robust HTTP client to Person 4 API
    schemas/
      __init__.py
      stic_models.py           # Pydantic schemas tailored for StIC/UI contracts
    adapters/
      __init__.py
      portfolio_adapter.py     # Adapts Person 4 data to SI Terminal UI formats
      ai_insights_adapter.py   # Formats risk/suitability for AI Insights screen
    mcp/
      __init__.py
      server.py                # StIC MCP Server exposing Person 4 tools
    ui/
      __init__.py
      terminal_dashboard.html  # Live, interactive SI Terminal powered by Person 4
```

### StIC MCP Tools Catalog:
1. `stic_get_portfolio_intelligence`: Retrieves total portfolio value, holdings, allocation, health status, and concentration score.
2. `stic_get_personalization_context`: Computes suitability score, warnings, and constraints for a given ticker and user.
3. `stic_get_advanced_risk_report`: Retrieves quantitative volatility, max drawdown, and risk factors.
4. `stic_get_investor_behavior_profile`: Returns user trading archetype, alignment score, and behavioral recommendations.
5. `stic_get_terminal_dashboard_data`: Single aggregated payload powering all SI Terminal screens simultaneously.

---

## 6. Environment Configuration

The environment file `.env.example` will include:
```ini
# Person 4 Core Service
APP_ENV=development
LOG_LEVEL=INFO
SECURITY_ENABLED=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,http://localhost:8080
RATE_LIMIT=120
RATE_LIMIT_WINDOW=60
MAX_REQUEST_SIZE=1048576
DATABASE_URL=sqlite:///./personalization.db

# StIC MCP & Design System Integration
PERSON4_API_URL=http://localhost:8000
STIC_API_URL=http://localhost:8080
STIC_PROJECT_ID=15879964569093521067
```

---

## 7. Verification & Testing Strategy
1. **Regression Safety**: Execute full Person 4 test suite (`python -m pytest tests/ -v`) — all 122 tests must pass with 0 regressions.
2. **Adapter & MCP Unit Tests**: Create `tests/test_stic_integration.py` verifying client connectivity, data formatting, and MCP tool execution.
3. **End-to-End Live UI / Flow Test**: Validate that deterministic demo users (`moderate_001`, `conservative_001`, `aggressive_001`) correctly populate the SI Terminal UI and StIC MCP tools.
