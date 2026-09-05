# FinanceApp — High-Precision Personalization & Financial AI Platform

**FinanceApp** is a unified, multi-agent financial intelligence and portfolio personalization platform built for high-precision investment decision support. It bridges multi-agent LLM analysis, quantitative portfolio risk modeling, behavioral profiling, real-time market indicators, corporate filing RAG search, and Model Context Protocol (MCP) tool-calling into a cohesive financial terminal.

---

## 1. Unified Architecture

```
                          StIC Terminal UI (:8000/dashboard)
                                         │
                                         ▼
                               StICApiClient (api.js)
                      (Centralized requests, timeouts, errors)
                                         │
                                         ▼
                              UNIFIED FASTAPI BACKEND
                          (person4_personalization/app.py)
                                  Port: 8000
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
  Person 4 (Core)                 Person 2 (Data)                  Person 1 (AI)
  - /users/{id}/portfolio         - /market/{sym} (Live quotes)    - POST /ai/analyze
  - /users/{id}/portfolio/analysis- /market/{sym}/indicators       - 5-Agent parallel
  - /users/{id}/portfolio/risk    - /news/{sym} (Sentiments)         execution
  - /users/{id}/behavior          - /rag/query (ChromaDB)          - Consensus verdict
  - /users/{id}/context/{sym}
        │                                │                                │
        └────────────────────────────────┼────────────────────────────────┘
                                         ▼
                            FinancialDataBridge (In-Process)
                                         │
                                         ▼
                                  StIC MCP Server
                           (stic/mcp/server.py: 12 Tools)
```

---

## 2. Core Subsystems & Features

### Person 1: Multi-Agent AI System
- **5-Agent Parallel Pipeline**: Asynchronously runs `TechnicalAgent`, `FundamentalAgent`, `SentimentAgent`, `RiskAgent`, and `SynthesisAgent` using `asyncio.gather`.
- **Consensus Engine**: Produces a unified investment verdict (`BUY`, `HOLD`, `SELL`, `AVOID`), confidence score, key drivers, risk warnings, and latency telemetry.

### Person 2: Market Data & Semantic RAG
- **Live / Cached Quotes**: Normalized pricing for NSE equities and US stocks (`RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `HDFCBANK.NS`, `ITC.NS`, `AAPL`, `NVDA`).
- **Technical Indicators**: Computed RSI (14), MACD, EMA 20, EMA 50, Momentum, Volatility.
- **Financial News & Sentiment**: Rule-based sentiment scoring across corporate headlines.
- **Corporate Filings RAG**: Semantic vector retrieval over 10-K/10-Q filing documents with citations and confidence scoring.

### Person 3: StIC MCP & High-Precision Terminal UI
- **Dark High-Precision Terminal**: Real-time reactive web interface (`/dashboard`, `/terminal`) rendered with JetBrains Mono typography, interactive SVG portfolio curves, sector progress bars, and independent error boundaries.
- **StIC MCP Server**: Exposes 12 MCP tools for AI agents and LLMs to interact with portfolio intelligence, market data, and risk analytics.

### Person 4: Personalization Engine & Portfolio Intelligence (Authority)
- **Portfolio Intelligence**: Real-time Net Asset Value (NAV), Day PnL, diversification health score (0–100), sector concentration.
- **Quantitative Risk Engine**: Parametric Value at Risk (VaR 95%), Conditional VaR (CVaR), Annualized Volatility, Max Drawdown, and factor breakdowns.
- **Behavioral Profiling**: Detects trading patterns, holding styles, risk tolerance consistency, and assigns investor archetypes.
- **Security & Persistence**: Strict CORS, CSP headers, rate limiting (120 req/min), SQLite persistence (`personalization.db`), and sensitive data masking.

---

## 3. Getting Started

### Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### Installation
```bash
# Clone repository
git clone https://github.com/crtl-freakssss/financeapp.git
cd financeapp

# Install dependencies
pip install -r requirements.txt
```

### Running the Unified Application
Start the primary FastAPI backend (port 8000):
```bash
python person4_personalization/app.py
```
*Or run directly with uvicorn:*
```bash
uvicorn person4_personalization.app:app --host 127.0.0.1 --port 8000 --reload
```

---

## 4. Access Points

- **StIC Terminal Dashboard UI**: [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard) (or `/terminal`)
- **Interactive Swagger OpenAPI Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc API Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Readiness Probe**: [http://127.0.0.1:8000/ready](http://127.0.0.1:8000/ready)

---

## 5. Demo Investor Profiles

| User ID | Name / Archetype | Risk Tolerance | Investment Horizon |
| :--- | :--- | :--- | :--- |
| `moderate_001` | Balanced Growth Investor | MODERATE | 5 Years |
| `conservative_001` | Capital Preserver | CONSERVATIVE | 10 Years |
| `aggressive_001` | Alpha Momentum Trader | AGGRESSIVE | 2 Years |

---

## 6. StIC MCP Tools Catalog

AI agents can connect to the StIC MCP server (`person4_personalization/stic/mcp/server.py`) to invoke the following tools:

1. `stic_run_multi_agent_analysis` — 5-Agent parallel AI synthesis for a user & ticker.
2. `stic_query_financial_rag` — Semantic vector search over corporate filings with citations.
3. `stic_get_market_data` — Normalized market quote and pricing range.
4. `stic_get_market_indicators` — Computed technical indicators (RSI, MACD, EMA20/50).
5. `stic_get_news` — Financial news headlines and sentiment scores.
6. `stic_get_portfolio_intelligence` — Holdings, asset allocation, health gauge.
7. `stic_get_user_behavior` — Trading frequency, holding style, risk flags.
8. `stic_get_advanced_risk` — Quantitative VaR, CVaR, stress factors.
9. `stic_get_personalization_context` — Personalized suitability scoring & constraints.
10. `stic_get_terminal_dashboard_data` — Consolidated full dashboard payload.
11. `stic_get_user_profile` — Investor preferences and horizon.
12. `stic_get_user_holdings` — Raw positions and cash balances.

---

## 7. Automated Testing Suite

The repository includes a comprehensive test suite across all subsystems:

```bash
# Run the complete repository test suite:
python -m pytest -q

# Run Person 1 tests:
pytest person1/tests/ -v

# Run Person 2 tests:
pytest person2/tests/ -v

# Run Person 4 & Integration tests:
pytest person4_personalization/tests/ -v
```

### Verified Test Results:
- **Repository Total**: **228 / 228 Passed (100%)**
- **Person 1**: 2 / 2 Passed
- **Person 2**: 32 / 32 Passed
- **Person 4 + Integration**: 194 / 194 Passed
- **Failures**: 0

---

## 8. License & Security
- All sensitive credentials, database files (`personalization.db`), and `.env` files are excluded via `.gitignore`.
- Rate limiting and input validation are active on all public endpoints.