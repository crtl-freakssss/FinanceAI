# FINAI — Data & RAG Engine (Person 2 Subsystem)

**Standalone Financial Data & Semantic Evidence Retrieval Pipeline**

---

## 1. Overview

This module provides the core **Financial Data and RAG Evidence Infrastructure** for FINAI. It operates completely **independently** from other team modules (`person1_ai`, `person3_frontend`, `person4_personalization`), delivering:

1. **Market Data & Quotes**: Real-time quotes with multi-tier graceful fallback (`Live API` $\to$ `Cache` $\to$ `Deterministic Mock`).
2. **Historical Price Data**: Standardized OHLCV data across multiple timeframes (`1mo`, `3mo`, `6mo`, `1y`).
3. **Technical Indicators**: Mathematical technical indicators (`EMA9`, `EMA21`, `SMA20`, `SMA50`, `RSI`, `MACD`, `Volatility`, `Momentum`, `Average Volume`).
4. **News & Sentiment Data**: Structured news ingestion, summary extraction, and deterministic keyword sentiment analysis.
5. **Financial Document Parsing**: TXT and PDF parser preserving page numbers and document hierarchy without fabrication.
6. **RAG Vector Search & Citations**: ChromaDB-backed semantic retrieval returning verified evidence snippets with standard formatted citations and a **strict zero-hallucination policy**.

---

## 2. Architecture

```
                    FINAI DATA ENGINE
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
       MARKET            NEWS           FILINGS
          │                │                │
          ▼                ▼                ▼
    PRICE HISTORY      PARSING        DOCUMENT PARSING
          │                │                │
          ▼                ▼                ▼
     INDICATORS       SENTIMENT          CHUNKS
          │                │                │
          │                │                ▼
          │                │            EMBEDDINGS (MiniLM / OpenAI)
          │                │                │
          │                │                ▼
          │                │            CHROMADB (.chroma/)
          │                │                │
          └────────────────┴────────────────┘
                           │
                           ▼
                       RETRIEVER (rag.retriever.retrieve)
                           │
                           ▼
                        EVIDENCE
                           │
                           ▼
                       CITATIONS (rag.citations.format_citation)
```

---

## 3. Directory Layout

```
person2/
├── README.md               # Complete documentation
├── requirements.txt        # Production dependencies
├── pytest.ini             # Pytest discovery configuration
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── app.py                  # Standalone interactive CLI demonstration
│
├── market/                 # Market quotes, price history, indicators, cache
│   ├── __init__.py
│   ├── market_data.py      # Entry point for real-time market data
│   ├── price_history.py    # Historical OHLCV records (1mo, 3mo, 6mo, 1y)
│   ├── indicators.py       # Technical indicator calculations
│   └── cache.py            # Local TTL file cache
│
├── news/                   # News gathering & sentiment analysis
│   ├── __init__.py
│   ├── news_fetcher.py     # Live/mock news retrieval
│   ├── news_parser.py      # Uniform article structure parser
│   └── sentiment_data.py   # Sentiment classification & score computation
│
├── filings/                # Financial filing parsers
│   ├── __init__.py
│   ├── filing_fetcher.py   # Local document discovery
│   └── filing_parser.py    # TXT and PDF (PyMuPDF) structured parser
│
├── rag/                    # Semantic retrieval & vector database
│   ├── __init__.py
│   ├── ingest.py           # Document ingestion & vectorization pipeline
│   ├── chunker.py          # Boundary-aware text chunking
│   ├── embeddings.py       # SentenceTransformers / OpenAI embedding provider
│   ├── vector_store.py     # Persistent ChromaDB client & collection manager
│   ├── retriever.py        # Semantic search with company filtering & thresholding
│   └── citations.py        # Standardized evidence citation formatting
│
├── documents/              # Local financial document corpus
│   ├── reliance/           # Q3 FY25 financial results & annual report
│   ├── tcs/                # Q3 FY25 earnings release
│   ├── infosys/            # Q3 FY25 financial statement
│   ├── hdfcbank/           # Q3 FY25 performance review
│   └── itc/                # Q3 FY25 financial report
│
├── mock_data/              # Deterministic offline mock records
│   ├── market.json         # Quotes & historical OHLCV data
│   ├── news.json           # Curated financial news items
│   └── filings.json        # Financial filing metadata
│
└── tests/                  # Pytest unit & integration test suite (32 tests)
    ├── test_market.py      # Quotes, history, indicators, cache tests
    ├── test_news.py        # News parsing & sentiment tests
    ├── test_rag.py         # Chunking, embeddings, parsing tests
    ├── test_retriever.py   # Semantic search & citation tests
    └── test_degraded.py    # Graceful degradation & fallback tests
```

---

## 4. Supported Demo Stocks

The module provides full out-of-the-box data for the 5 primary hackathon equities:

| Symbol | Company | Sector |
| :--- | :--- | :--- |
| `RELIANCE.NS` | Reliance Industries Ltd | Conglomerate / Energy / Retail |
| `TCS.NS` | Tata Consultancy Services Ltd | IT Services & Consulting |
| `INFY.NS` | Infosys Ltd | IT Services & Consulting |
| `HDFCBANK.NS` | HDFC Bank Ltd | Banking & Financial Services |
| `ITC.NS` | ITC Ltd | FMCG / Cigarettes / Hotels / Agri |

---

## 5. Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
```bash
cp .env.example .env
```
*(Optional)* Add `OPENAI_API_KEY=your-key` if you wish to use OpenAI embeddings. If omitted, the system defaults to the local `SentenceTransformer('all-MiniLM-L6-v2')` model for 100% offline reliability.

---

## 6. How to Run

### Interactive Standalone CLI Demo
Run the interactive demonstration menu:
```bash
python app.py
```

### Re-ingest Documents into ChromaDB
To parse all financial filings in `documents/` and build the vector database:
```bash
python -c "from rag.ingest import ingest_documents; ingest_documents(rebuild=True)"
```

### Run Full Test Suite
Run the 32 automated tests across all modules:
```bash
pytest -v
```

---

## 7. Graceful Degradation & Fallback Strategy

The module never crashes when external networks or APIs fail:

```
[Live yfinance API] ──(Failure)──> [Local Cache .cache/] ──(Failure)──> [Deterministic Mock Data]
```

- **Source Transparency**: Every response clearly indicates its source (`"source": "live"`, `"source": "cache"`, or `"source": "mock"`).
- **Zero Hallucination Guarantee**: If no relevant evidence exists in the document corpus for a RAG query, the system returns `"No reliable evidence was found for this query."` without inventing figures or citations.

---

## 8. Public Integration Contract (For Person 1 & Person 4)

External modules (e.g. Person 1's LangGraph agents or Person 4's portfolio service) can consume this module via clean, predictable Python functions:

```python
from market import get_market_data, get_price_history, get_indicators
from news import get_news, get_sentiment
from rag import retrieve, format_citation

# 1. Market Quote
quote = get_market_data("RELIANCE.NS")

# 2. Historical Prices
history = get_price_history("TCS.NS", period="3mo")

# 3. Indicators
indicators = get_indicators("TCS.NS", history)

# 4. News & Sentiment
news_data = get_news("INFY.NS")
sentiment = get_sentiment(news_data["news"])

# 5. Semantic Evidence Retrieval
evidence = retrieve(
    query="What was Reliance's EBITDA growth?",
    symbol="RELIANCE.NS",
    top_k=3
)

# 6. Format Citation
for item in evidence["results"]:
    print(format_citation(item))
```
