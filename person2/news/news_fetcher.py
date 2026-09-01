import json
import os
import yfinance as yf
from .news_parser import parse_news

MOCK_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "mock_data", "news.json")

def get_news(symbol: str) -> dict:
    """
    Fetches and parses financial news for a given stock symbol.
    
    Fallback chain:
    1. yfinance live news feed (if available)
    2. mock_data/news.json
    
    Source is explicitly marked as 'live' or 'mock'.
    """
    sym = symbol.strip().upper()
    normalized = sym if "." in sym else f"{sym}.NS"
    
    # 1. Attempt live news via yfinance
    try:
        ticker = yf.Ticker(normalized)
        yf_news = getattr(ticker, "news", None)
        if yf_news and isinstance(yf_news, list) and len(yf_news) > 0:
            parsed_articles = []
            for item in yf_news:
                content = item.get("content", item)
                parsed = parse_news({
                    "headline": content.get("title") or item.get("title"),
                    "source": content.get("provider", {}).get("displayName") or item.get("publisher", "Live Financial News"),
                    "url": content.get("canonicalUrl", {}).get("url") or item.get("link", ""),
                    "published_time": content.get("pubDate") or item.get("providerPublishTime", ""),
                    "symbol": normalized,
                    "summary": content.get("summary") or item.get("summary", ""),
                    "raw_text": content.get("description") or ""
                })
                parsed_articles.append(parsed)
                
            if parsed_articles:
                return {
                    "symbol": normalized,
                    "source": "live",
                    "status": "Live news successfully retrieved.",
                    "count": len(parsed_articles),
                    "news": parsed_articles
                }
    except Exception:
        pass

    # 2. Fallback to mock_data/news.json
    if os.path.exists(MOCK_DATA_PATH):
        try:
            with open(MOCK_DATA_PATH, 'r', encoding='utf-8') as f:
                mock_articles = json.load(f)
            
            matching = [
                parse_news(a) for a in mock_articles 
                if a.get("symbol", "").upper() == normalized or a.get("symbol", "").upper() == sym
            ]
            
            # If no exact symbol match, return general demo financial news tagged with symbol
            if not matching:
                matching = [parse_news(a) for a in mock_articles]
                
            return {
                "symbol": normalized,
                "source": "mock",
                "status": "Live news unavailable. Using demo news.",
                "count": len(matching),
                "news": matching
            }
        except Exception as e:
            return {
                "symbol": normalized,
                "source": "mock",
                "status": f"Error loading mock news: {str(e)}",
                "count": 0,
                "news": []
            }

    return {
        "symbol": normalized,
        "source": "mock",
        "status": "Live news unavailable. Using demo news.",
        "count": 0,
        "news": []
    }
