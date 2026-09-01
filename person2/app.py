import os
import sys
import json
import time

from market.market_data import get_market_data, normalize_symbol
from market.price_history import get_price_history
from market.indicators import get_indicators
from news.news_fetcher import get_news
from news.sentiment_data import get_sentiment
from filings.filing_fetcher import get_filings
from rag.retriever import retrieve
from rag.citations import format_citation, format_all_citations
from rag.ingest import ingest_documents

DEMO_SYMBOLS = [
    ("1", "RELIANCE.NS", "Reliance Industries Ltd"),
    ("2", "TCS.NS", "Tata Consultancy Services"),
    ("3", "INFY.NS", "Infosys Ltd"),
    ("4", "HDFCBANK.NS", "HDFC Bank Ltd"),
    ("5", "ITC.NS", "ITC Ltd")
]

def select_symbol_menu(prompt="Select a company: ") -> str:
    print("\nSupported Demo Equities:")
    for num, sym, name in DEMO_SYMBOLS:
        print(f"  [{num}] {sym:<12} ({name})")
    print("  [C] Custom Symbol")
    
    choice = input(f"{prompt}").strip()
    for num, sym, _ in DEMO_SYMBOLS:
        if choice == num or choice.upper() == sym:
            return sym
    if choice.upper() == 'C':
        custom = input("Enter custom ticker (e.g. AAPL, SBIN.NS): ").strip()
        return custom if custom else "RELIANCE.NS"
    
    # Try normalized directly
    return normalize_symbol(choice) if choice else "RELIANCE.NS"

def print_header():
    print("\n" + "=" * 60)
    print("                FINAI DATA & RAG ENGINE")
    print("            Person 2 — Standalone Subsystem")
    print("=" * 60)

def print_menu():
    print_header()
    print("1. Current Market Quote (Live / Cache / Mock Fallback)")
    print("2. Historical OHLCV Price Data")
    print("3. Technical Indicators (EMA9, EMA21, RSI, MACD, Volatility)")
    print("4. Financial News & Sentiment Analysis")
    print("5. Local Financial Documents / Filings")
    print("6. Semantic RAG Search & Evidence Citations")
    print("7. Rebuild / Ingest Vector Store (ChromaDB)")
    print("8. Exit")
    print("=" * 60)

def handle_market_data():
    sym = select_symbol_menu()
    print(f"\n[Fetching Market Data for {sym}...]")
    data = get_market_data(sym)
    
    print("\n" + "-" * 50)
    print(f" MARKET DATA: {data.get('symbol')}")
    print("-" * 50)
    print(f" Price:          {data.get('currency', 'INR')} {data.get('price'):,}")
    print(f" Change:         {data.get('change'):+} ({data.get('change_percentage'):+.2f}%)")
    print(f" Open / High / Low: {data.get('open')} / {data.get('high')} / {data.get('low')}")
    print(f" Prev Close:     {data.get('previous_close')}")
    print(f" Volume:         {data.get('volume'):,}")
    print(f" Timestamp:      {data.get('timestamp')}")
    print(f" Source:         [{data.get('source', '').upper()}] ({data.get('status')})")
    print("-" * 50)

def handle_price_history():
    sym = select_symbol_menu()
    print("\nPeriods: 1mo, 3mo, 6mo, 1y")
    period = input("Select period [default: 1mo]: ").strip() or "1mo"
    
    data = get_price_history(sym, period)
    history = data.get("history", [])
    
    print("\n" + "-" * 50)
    print(f" PRICE HISTORY: {data.get('symbol')} ({data.get('period')})")
    print(f" Source: [{data.get('source', '').upper()}] | Total Records: {len(history)}")
    print("-" * 50)
    
    if history:
        print(f"{'Date':<12} {'Open':<10} {'High':<10} {'Low':<10} {'Close':<10} {'Volume':<12}")
        print("-" * 66)
        # Show latest 5 rows
        for row in history[-5:]:
            print(f"{row['Date']:<12} {row['Open']:<10.2f} {row['High']:<10.2f} {row['Low']:<10.2f} {row['Close']:<10.2f} {row['Volume']:<12,}")
        if len(history) > 5:
            print(f"... and {len(history)-5} earlier records.")
    print("-" * 50)

def handle_indicators():
    sym = select_symbol_menu()
    hist_data = get_price_history(sym, period="3mo")
    indicators = get_indicators(sym, hist_data)
    
    print("\n" + "-" * 50)
    print(f" TECHNICAL INDICATORS: {sym}")
    print(" (Provided as data for technical analysis agents)")
    print("-" * 50)
    print(f" EMA (9):                  {indicators.get('ema9')}")
    print(f" EMA (21):                 {indicators.get('ema21')}")
    print(f" SMA (20):                 {indicators.get('sma20')}")
    print(f" RSI (14):                 {indicators.get('rsi')}")
    print(f" MACD:                     {indicators.get('macd')}")
    print(f" MACD Signal:              {indicators.get('macd_signal')}")
    print(f" MACD Histogram:           {indicators.get('macd_histogram')}")
    print(f" Volatility (Annualized):  {indicators.get('volatility')}")
    print(f" Momentum (ROC):           {indicators.get('momentum')}")
    print(f" 20-Day Avg Volume:        {indicators.get('average_volume'):,}" if indicators.get('average_volume') else " Avg Vol: N/A")
    print(f" Period Price Change:      {indicators.get('percentage_price_change'):+.2f}%")
    print(f" Calculation Status:       {indicators.get('status')}")
    print("-" * 50)

def handle_news():
    sym = select_symbol_menu()
    news_res = get_news(sym)
    articles = news_res.get("news", [])
    
    sentiment = get_sentiment(articles)
    
    print("\n" + "-" * 50)
    print(f" NEWS & SENTIMENT: {sym}")
    print(f" Source: [{news_res.get('source', '').upper()}] | Status: {news_res.get('status')}")
    print("-" * 50)
    print(f" Overall Sentiment: {sentiment.get('label')} (Score: {sentiment.get('score'):.2f})")
    print(f" Articles Analyzed: {len(articles)}")
    print("-" * 50)
    
    for idx, item in enumerate(articles[:4], 1):
        print(f"\n[{idx}] {item.get('headline')}")
        print(f"    Publisher: {item.get('source')} | Time: {item.get('published_time')}")
        if item.get('summary'):
            print(f"    Summary: {item.get('summary')}")
    print("-" * 50)

def handle_filings():
    sym = select_symbol_menu()
    filings_res = get_filings(sym)
    docs = filings_res.get("documents", [])
    
    print("\n" + "-" * 50)
    print(f" FINANCIAL FILINGS & CORPUS: {sym}")
    print(f" Source: [{filings_res.get('source')}] | Available Documents: {len(docs)}")
    print("-" * 50)
    for idx, d in enumerate(docs, 1):
        print(f" [{idx}] {d.get('title')} ({d.get('path')})")
    print("-" * 50)

def handle_rag_search():
    print("\nExample RAG Questions:")
    print("  - What was Reliance's EBITDA growth in Q3 FY25?")
    print("  - What is TCS operating margin and order book TCV?")
    print("  - What were Infosys large deal wins and AI Topaz adoption?")
    print("  - What was HDFC Bank post-merger net profit and asset quality?")
    print("  - What dividend did ITC declare in Q3?")
    
    query = input("\nEnter your financial research query: ").strip()
    if not query:
        print("Query cannot be empty.")
        return

    sym_filter = input("Filter by symbol (e.g. RELIANCE.NS, or press Enter for all): ").strip()
    sym_arg = normalize_symbol(sym_filter) if sym_filter else None
    
    print(f"\n[Retrieving evidence from ChromaDB vector store...]")
    t0 = time.time()
    rag_result = retrieve(query, symbol=sym_arg, top_k=4)
    elapsed = time.time() - t0
    
    results = rag_result.get("results", [])
    
    print("\n==================================================")
    print("                   RAG RESULT")
    print(f" Query:   {query}")
    print(f" Latency: {elapsed*1000:.1f}ms | Matches: {len(results)}")
    print("==================================================")
    
    if not results:
        print(f"\n{rag_result.get('message', 'No reliable evidence was found for this query.')}")
    else:
        print("\nRetrieved Evidence & Citations:")
        for idx, res in enumerate(results, 1):
            print(f"\n[{idx}]")
            print(format_citation(res))
            print("-" * 40)
    print("==================================================")

def handle_ingest():
    print("\nRebuilding ChromaDB vector store from local documents...")
    res = ingest_documents(rebuild=True)
    print(f"Result: {json.dumps(res, indent=2)}")

def main():
    while True:
        try:
            print_menu()
            choice = input("Select an option (1-8): ").strip()
            
            if choice == '1':
                handle_market_data()
            elif choice == '2':
                handle_price_history()
            elif choice == '3':
                handle_indicators()
            elif choice == '4':
                handle_news()
            elif choice == '5':
                handle_filings()
            elif choice == '6':
                handle_rag_search()
            elif choice == '7':
                handle_ingest()
            elif choice == '8' or choice.lower() in ['q', 'exit']:
                print("\nExiting FINAI Data Engine. Goodbye!")
                break
            else:
                print("Invalid choice. Please select 1-8.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\n[Error] {e}")

if __name__ == "__main__":
    main()
