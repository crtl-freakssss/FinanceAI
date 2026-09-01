def parse_news(raw_news: dict) -> dict:
    """
    Standardizes a raw news article record into a uniform dictionary.
    Guarantees no missing fields and sanitizes strings.
    """
    if not isinstance(raw_news, dict):
        return {
            "headline": "No Headline Available",
            "source": "Unknown",
            "url": "",
            "published_time": "",
            "symbol": "",
            "summary": "",
            "raw_text": ""
        }

    return {
        "headline": str(raw_news.get("headline") or raw_news.get("title") or "No Headline Available").strip(),
        "source": str(raw_news.get("source") or raw_news.get("publisher") or "Unknown").strip(),
        "url": str(raw_news.get("url") or raw_news.get("link") or "").strip(),
        "published_time": str(raw_news.get("published_time") or raw_news.get("pubDate") or "").strip(),
        "symbol": str(raw_news.get("symbol") or "").strip().upper(),
        "summary": str(raw_news.get("summary") or raw_news.get("description") or "").strip(),
        "raw_text": str(raw_news.get("raw_text") or raw_news.get("content") or "").strip()
    }
