import re

def get_sentiment(news_items: list) -> dict:
    """
    Provides sentiment DATA only based on analyzed financial news items.
    
    Returns:
    - label: 'POSITIVE', 'NEUTRAL', or 'NEGATIVE'
    - score: float between 0.0 (very negative) and 1.0 (very positive)
    - supporting_headlines: list of relevant headlines backing the score
    - counts: breakdown of positive vs negative indicators found
    """
    if not news_items or not isinstance(news_items, list):
        return {
            "label": "NEUTRAL",
            "score": 0.5,
            "supporting_headlines": [],
            "counts": {"positive": 0, "negative": 0, "total_articles": 0}
        }

    positive_keywords = {
        "growth", "surge", "gain", "profit", "beats", "rally", "record", "jump", 
        "dividend", "expansion", "buy", "bullish", "outperform", "upgrade", 
        "strong", "high", "order win", "improves", "milestone"
    }
    
    negative_keywords = {
        "drop", "loss", "decline", "fall", "miss", "slump", "down", "bearish", 
        "downgrade", "underperform", "plunge", "concern", "probe", "fine", 
        "fraud", "investigation", "weak", "debt", "headwind"
    }

    pos_score = 0
    neg_score = 0
    supporting = []

    for item in news_items:
        headline = item.get("headline", "")
        summary = item.get("summary", "")
        combined_text = f"{headline} {summary}".lower()

        # Tokenize words
        words = set(re.findall(r'\b[a-z]+\b', combined_text))
        
        pos_matches = words.intersection(positive_keywords)
        neg_matches = words.intersection(negative_keywords)

        if len(pos_matches) > len(neg_matches):
            pos_score += (len(pos_matches) - len(neg_matches))
            supporting.append({"headline": headline, "sentiment": "positive", "keywords": list(pos_matches)})
        elif len(neg_matches) > len(pos_matches):
            neg_score += (len(neg_matches) - len(pos_matches))
            supporting.append({"headline": headline, "sentiment": "negative", "keywords": list(neg_matches)})

    total_hits = pos_score + neg_score
    if total_hits == 0:
        base_score = 0.50
        label = "NEUTRAL"
    else:
        # Scale score from 0.0 to 1.0
        base_score = 0.50 + ((pos_score - neg_score) / (2.0 * max(total_hits, 4)))
        base_score = max(0.05, min(0.95, base_score))
        
        if base_score >= 0.58:
            label = "POSITIVE"
        elif base_score <= 0.42:
            label = "NEGATIVE"
        else:
            label = "NEUTRAL"

    return {
        "label": label,
        "score": round(float(base_score), 2),
        "supporting_headlines": [s["headline"] for s in supporting[:5]],
        "counts": {
            "positive_signals": pos_score,
            "negative_signals": neg_score,
            "total_articles": len(news_items)
        }
    }
