# Hackverse Demo & Final Readiness Guide — Person 4

## Person 4: Personalization & Portfolio Intelligence Service

---

## A. Installation

1. Navigate to the project root directory:
   ```bash
   cd person4_personalization
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## B. Environment Configuration

Copy the example configuration:
```bash
cp .env.example .env
```

Default `.env` settings:
```ini
APP_ENV=development
LOG_LEVEL=INFO
SECURITY_ENABLED=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173
RATE_LIMIT=120
RATE_LIMIT_WINDOW=60
MAX_REQUEST_SIZE=1048576
DATABASE_URL=sqlite:///./personalization.db
```

---

## C. Starting the API

Launch the production FastAPI server:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

---

## D. Health & Readiness Verification

- **Root Health:**
  ```bash
  curl -X GET "http://localhost:8000/health"
  ```
  `{"status": "ok", "service": "finance-personalization", "version": "1.0.0"}`

- **Database Readiness:**
  ```bash
  curl -X GET "http://localhost:8000/api/v1/readiness"
  ```
  `{"status": "ready", "database": "connected", "service": "finance-personalization"}`

- **Observability Metrics:**
  ```bash
  curl -X GET "http://localhost:8000/api/v1/metrics"
  ```

---

## E. Deterministic Demo Profiles

| User ID | Risk Tolerance | Capital | Top Holdings | Target Scenario |
| :--- | :--- | :--- | :--- | :--- |
| `moderate_001` *(Default Demo)* | `MODERATE` | ₹5,00,000 | RELIANCE.NS, TCS.NS, ITC.NS | Balanced growth with energy & tech exposure |
| `conservative_001` | `CONSERVATIVE` | ₹10,00,000 | HDFCBANK.NS, ITC.NS | Capital preservation, low volatility |
| `aggressive_001` | `AGGRESSIVE` | ₹2,50,000 | RELIANCE.NS, INFY.NS, TCS.NS | High alpha growth, higher volatility acceptance |

---

## F. Step-by-Step Demo API Walkthrough

### Step 1: Query User Profile
```bash
curl -X GET "http://localhost:8000/api/v1/users/moderate_001/profile"
```

### Step 2: Fetch Current Portfolio
```bash
curl -X GET "http://localhost:8000/api/v1/users/moderate_001/portfolio"
```

### Step 3: Run Portfolio Intelligence Analysis
```bash
curl -X GET "http://localhost:8000/api/v1/users/moderate_001/portfolio/analysis"
```

### Step 4: Run Advanced Quantitative Risk Engine
```bash
curl -X GET "http://localhost:8000/api/v1/users/moderate_001/portfolio/risk/advanced"
```

### Step 5: Evaluate Behavioral Trading Pattern
```bash
curl -X GET "http://localhost:8000/api/v1/users/moderate_001/investor-profile"
```

### Step 6: Generate Personalization Context (Person 1 Hand-Off)
```bash
curl -X GET "http://localhost:8000/api/v1/users/moderate_001/context/RELIANCE.NS?sector=Energy&market_cap=LARGE&volatility=HIGH"
```

---

## G. How Person 1 (Agent Synthesis) Consumes Person 4

Person 1 calls the context endpoint before formulating final recommendations:
```python
from examples.person4_client import Person4Client

client = Person4Client("http://localhost:8000")
context = client.get_personalization_context(
    user_id="moderate_001",
    symbol="RELIANCE.NS",
    sector="Energy",
    market_cap="LARGE",
    volatility="HIGH"
)

# Use context["suitability"], context["risk_score"], context["warnings"] in recommendation logic
```

---

## H. How Person 3 (Frontend) Consumes Person 4

Person 3 fetches:
1. `GET /api/v1/users/{user_id}/portfolio/analysis` for asset breakdown & health gauge.
2. `GET /api/v1/users/{user_id}/investor-profile` for behavioral archetype badge & alignment alerts.

---

## I. Troubleshooting

1. **Port 8000 already in use:**
   ```bash
   uvicorn app:app --port 8001 --reload
   ```
2. **Database migration / reset:**
   Delete `personalization.db` and restart `uvicorn app:app`. Database tables will automatically initialize.
3. **Run automated smoke test:**
   ```bash
   python scripts/smoke_test.py
   ```
