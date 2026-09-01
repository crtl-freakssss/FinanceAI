import pytest
from news.news_fetcher import get_news
from news.news_parser import parse_news
from news.sentiment_data import get_sentiment

def test_news_fetcher_valid_symbol():
    news_res = get_news("RELIANCE.NS")
    assert news_res is not None
    assert "source" in news_res
    assert news_res["source"] in ["live", "mock"]
    assert "news" in news_res
    assert isinstance(news_res["news"], list)
    assert len(news_res["news"]) > 0

def test_news_parser_structure():
    raw = {
        "title": "Reliance Q3 Profit Rises",
        "publisher": "Reuters",
        "link": "https://example.com/rel",
        "pubDate": "2025-01-20",
        "description": "Reliance reported strong quarterly numbers."
    }
    parsed = parse_news(raw)
    assert parsed["headline"] == "Reliance Q3 Profit Rises"
    assert parsed["source"] == "Reuters"
    assert parsed["url"] == "https://example.com/rel"
    assert parsed["published_time"] == "2025-01-20"
    assert parsed["summary"] == "Reliance reported strong quarterly numbers."

def test_news_parser_missing_fields():
    parsed = parse_news({})
    assert parsed["headline"] == "No Headline Available"
    assert parsed["source"] == "Unknown"
    assert parsed["url"] == ""

def test_sentiment_calculation_positive():
    news_items = [
        {"headline": "TCS beats profit estimates with record surge and dividend rally", "summary": "Strong growth"}
    ]
    sentiment = get_sentiment(news_items)
    assert sentiment["label"] == "POSITIVE"
    assert sentiment["score"] > 0.50
    assert len(sentiment["supporting_headlines"]) == 1

def test_sentiment_calculation_negative():
    news_items = [
        {"headline": "Major slump and profit drop due to investigation and fraud concerns", "summary": "Underperform rating"}
    ]
    sentiment = get_sentiment(news_items)
    assert sentiment["label"] == "NEGATIVE"
    assert sentiment["score"] < 0.50

def test_sentiment_empty():
    sentiment = get_sentiment([])
    assert sentiment["label"] == "NEUTRAL"
    assert sentiment["score"] == 0.5
