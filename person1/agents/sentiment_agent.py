from typing import Dict, Any

from agents.base_agent import BaseAgent
from models.agent_result import AgentResult


class SentimentAgent(BaseAgent):
    """
    Sentiment Analysis Agent

    Uses:
    - sentiment_score
    - positive_news
    - negative_news
    - headlines
    """

    def __init__(self):
        super().__init__("sentiment")

    async def analyze(self, data: Dict[str, Any]) -> AgentResult:
        news = data.get("news_data", {})

        sentiment_score = news.get("sentiment_score", 0)
        positive_news = news.get("positive_news", 0)
        negative_news = news.get("negative_news", 0)
        headlines = news.get("headlines", [])

        score = 0
        reasons = []
        risks = []

        # Overall sentiment score
        if sentiment_score >= 0.7:
            score += 30
            reasons.append("Overall market sentiment is strongly positive.")
        elif sentiment_score >= 0.5:
            score += 18
            reasons.append("Market sentiment is moderately positive.")
        elif sentiment_score >= 0.3:
            score += 8
            reasons.append("Market sentiment is neutral.")
        else:
            score -= 15
            risks.append("Overall market sentiment is negative.")

        # News balance
        difference = positive_news - negative_news

        if difference >= 5:
            score += 20
            reasons.append(f"{positive_news} positive news articles outweigh negative news.")
        elif difference >= 2:
            score += 12
            reasons.append("Positive news coverage is greater than negative coverage.")
        elif difference == 0:
            reasons.append("Positive and negative news coverage are balanced.")
        else:
            score -= 15
            risks.append("Negative news coverage dominates.")

        # Headlines
        bullish_keywords = [
            "growth",
            "profit",
            "expansion",
            "record",
            "approval",
            "upgrade",
            "strong",
            "beat",
        ]

        bearish_keywords = [
            "loss",
            "downgrade",
            "decline",
            "fraud",
            "penalty",
            "lawsuit",
            "fall",
            "miss",
        ]

        bullish_hits = 0
        bearish_hits = 0

        for headline in headlines:
            text = headline.lower()

            if any(word in text for word in bullish_keywords):
                bullish_hits += 1

            if any(word in text for word in bearish_keywords):
                bearish_hits += 1

        if bullish_hits > bearish_hits:
            score += 15
            reasons.append("News headlines contain mostly bullish keywords.")
        elif bearish_hits > bullish_hits:
            score -= 10
            risks.append("News headlines contain bearish keywords.")
        else:
            reasons.append("Headlines are mixed.")

        # Final Signal
        if score >= 55:
            signal = "BUY"
        elif score >= 35:
            signal = "HOLD"
        elif score >= 15:
            signal = "SELL"
        else:
            signal = "AVOID"

        confidence = min(max(score / 70, 0), 1)

        return AgentResult(
            agent="sentiment",
            signal=signal,
            confidence=round(confidence, 2),
            reasons=reasons,
            risks=risks,
            sources=["Financial News Feed", "News Headlines"],
            metadata={
                "sentiment_score": sentiment_score,
                "positive_news": positive_news,
                "negative_news": negative_news,
                "bullish_headlines": bullish_hits,
                "bearish_headlines": bearish_hits,
                "sentiment_score_total": score,
            },
        )