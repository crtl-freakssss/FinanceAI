# FinanceAI — Autonomous Multi-Agent Financial Intelligence Platform

**FinanceAI** (PS-01) is an autonomous multi-agent financial intelligence and portfolio personalization platform built for high-precision investment decision support. It bridges quantitative portfolio risk modeling, behavioral investor profiling, real-time market indicators, corporate filing RAG search, and an enterprise dashboard into a unified decision platform.

---

## 1. Unified Architecture

```
                       Enterprise Dashboard UI (:8000/dashboard)
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
   - /users/{id}/portfolio/analysis- /market/{sym}/indicators       - 4-Agent parallel
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

## 2. Technology Stack

* **Backend & API:** Python 3.10+, FastAPI, Uvicorn ASGI
* **Concurrency & Orchestration:** `asyncio` parallel agent execution (`asyncio.gather`)
* **Vector Store & Embeddings:** ChromaDB (`PersistentClient`), `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dimensions) with deterministic normalized hash fallback
* **Market Data & Indicators:** `yfinance` API with local caching and deterministic fallback; computed RSI (14), MACD, EMA 20, EMA 50, Momentum, Volatility
* **Database & Persistence:** SQLite (`personalization.db`), SQLAlchemy 2.0 ORM
* **Portfolio Risk Modeling:** Parametric Value at Risk (VaR 95%), Conditional VaR (CVaR), Annualized Volatility, Max Drawdown, Herfindahl-Hirschman Concentration Index (HHI)
* **Personalization Engine:** Investor risk capacity, single-position limits, sector allocation ceilings, pre-trade suitability checks, and behavioral profiling
* **Frontend UI:** Self-contained Single-Page Application (Vanilla HTML5, Modern CSS3 Enterprise Design System, Vanilla JavaScript ES6)

---

## 3. Core Subsystems & Features

### Person 1: Multi-Agent Parallel AI System
* **4-Agent Parallel Pipeline:** Asynchronously executes `TechnicalAgent`, `FundamentalAgent`, `SentimentAgent`, and `RiskAgent` simultaneously using `asyncio.gather`.
* **Heuristic & Rule-Based Scoring:** The agents utilize deterministic, quantitative scoring models (indicator thresholds, valuation ratios, headline sentiment balance, and exposure limits) for rapid (<100ms), reliable execution without external LLM dependencies.
* **Consensus Engine:** Combines the individual agent votes with weighted criteria (Technical 30%, Fundamental 30%, Sentiment 20%, Risk 20%) into a unified verdict (`BUY`, `HOLD`, `SELL`, `AVOID`) and discounts confidence if agents disagree.

### Person 2: Market Data & Semantic RAG
* **Live / Cached Quotes:** Normalized pricing for NSE equities and US stocks (`RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `HDFCBANK.NS`, `ITC.NS`, `AAPL`, `NVDA`).
* **Technical Indicators:** Computed RSI (14), MACD, EMA 20, EMA 50, Momentum, Volatility.
* **Financial News & Sentiment:** Rule-based sentiment scoring across corporate headlines and positive/negative article balance.
* **Corporate Filings RAG:** Semantic vector retrieval over audited 10-K/Q3 financial reports in ChromaDB with document citations and match confidence scores.

### Person 3: Enterprise Decision Platform UI & MCP Server
* **Enterprise Dashboard:** Clean light-theme interface matching modern enterprise decision platforms: fixed 260px sidebar, top header with live backend status dot, 12px rounded cards with subtle borders, and 8 dedicated views:
  1. **Executive Dashboard** (NAV, Return, Holdings, Risk KPIs, Top AI Insight, Quick Actions, Tracked Equities)
  2. **Stock Analysis** (Live quote header, AI synthesis verdict, 4 agent cards, 5-step reasoning trace, suitability evaluation)
  3. **Market Analysis** (Live price, 6 technical indicators, news sentiment feed)
  4. **Research / RAG** (Corporate filings semantic vector search with citations)
  5. **Portfolio** (NAV, cash, holdings ledger, sector allocation progress, SVG equity curve)
  6. **Risk Analysis** (VaR 95%, CVaR, annualized volatility, max drawdown, concentration audits)
  7. **Investor Profile** (Capital base, risk tolerance, horizon, sector constraints, behavioral style)
  8. **Watchlist** (Curated multi-stock table with live prices, 24h change, AI signals, and one-click analysis)
* **StIC MCP Server:** Exposes 12 Model Context Protocol tools for AI agents and LLMs to interact with portfolio intelligence, market data, and risk analytics.

### Person 4: Personalization Engine & Portfolio Intelligence
* **Portfolio Intelligence:** Real-time Net Asset Value (NAV), Day P&L, diversification health score (0–100), sector concentration.
* **Quantitative Risk Engine:** Parametric Value at Risk (VaR 95%), Conditional VaR (CVaR), Annualized Volatility, Max Drawdown, and factor breakdowns.
* **Personalized Recommendations:** Tested and verified signal divergence where conservative and aggressive investor profiles receive different recommendations and confidence scores on the exact same stock.
* **Behavioral Profiling:** Detects trading cadence, holding style, risk consistency, and assigns investor archetypes.
* **Persistence & Observability:** SQLite persistence (`personalization.db`), structured JSON request logging, correlation IDs (`X-Request-ID`), and latency metrics (`X-Process-Time`).

---

## 4. Getting Started

### Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### Installation
```bash
# Clone repository
git clone https://github.com/crtl-freakssss/FinanceAI.git
cd FinanceAI

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
Start the primary FastAPI backend (port 8000):
```bash
python person4_personalization/app.py
```
*Or run directly with uvicorn:*
```bash
uvicorn person4_personalization.app:app --host 127.0.0.1 --port 8000 --reload
```

---

## 5. Access Points

- **Enterprise Dashboard UI**: [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard) (or `/` and `/terminal`)
- **Interactive Swagger OpenAPI Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc API Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Readiness Probe**: [http://127.0.0.1:8000/ready](http://127.0.0.1:8000/ready)

---

## 6. Demo Investor Profiles

| User ID | Name / Archetype | Risk Tolerance | Risk Capacity | Investment Horizon |
| :--- | :--- | :--- | :--- | :--- |
| `moderate_001` | Balanced Growth Investor | MODERATE | MEDIUM | 1 - 3 Years |
| `conservative_001` | Capital Preserver | CONSERVATIVE | LOW | Short-Term (<1 Year) |
| `aggressive_001` | Alpha Momentum Trader | AGGRESSIVE | HIGH | Long-Term (>3 Years) |

---

## 7. StIC MCP Tools Catalog

1. `stic_run_multi_agent_analysis` — 4-Agent parallel AI synthesis for a user & ticker.
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

## 8. License & Security
- All sensitive credentials, database binaries, virtual environments, and `.env` files are excluded via `.gitignore`.
- Security headers, CORS configuration, and input validation are active across all endpoints.
- Distributed under the MIT License.