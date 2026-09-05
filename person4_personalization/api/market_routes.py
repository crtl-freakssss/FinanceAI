"""
Market & News API routes bridging Person 2 services into the unified FastAPI application.
Exposes endpoints for quotes, price history, technical indicators, and news sentiment.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Path, status
from pydantic import BaseModel, Field

from data_bridge import (
    normalize_symbol_pair,
    p2_get_market_data,
    p2_get_price_history,
    p2_get_indicators,
    p2_get_news,
    p2_get_sentiment,
    SymbolNotFoundError,
)

market_router = APIRouter(tags=["Market & Financial Data"])


@market_router.get("/market/{symbol}", summary="Get Market Quote")
def get_market_quote(
    symbol: str = Path(..., description="Stock ticker symbol (e.g., RELIANCE.NS, TCS, AAPL)")
):
    """
    Retrieves live or cached market quote for the specified stock symbol.
    """
    try:
        req_sym, norm_sym = normalize_symbol_pair(symbol)
    except SymbolNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    if not p2_get_market_data:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Market data provider is currently unavailable.",
        )

    try:
        data = p2_get_market_data(norm_sym)
        data["requested_symbol"] = req_sym
        data["normalized_symbol"] = norm_sym
        return data
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving market quote: {str(exc)}",
        )


@market_router.get("/market/{symbol}/history", summary="Get Price History")
def get_stock_price_history(
    symbol: str = Path(..., description="Stock ticker symbol"),
    period: str = Query("1mo", description="Historical period: 1mo, 3mo, 6mo, 1y"),
):
    """
    Retrieves historical OHLCV pricing records for technical analysis and charting.
    """
    try:
        req_sym, norm_sym = normalize_symbol_pair(symbol)
    except SymbolNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    if not p2_get_price_history:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Price history provider is currently unavailable.",
        )

    try:
        data = p2_get_price_history(norm_sym, period=period)
        data["requested_symbol"] = req_sym
        data["normalized_symbol"] = norm_sym
        return data
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving price history: {str(exc)}",
        )


@market_router.get("/market/{symbol}/indicators", summary="Get Technical Indicators")
def get_technical_indicators(
    symbol: str = Path(..., description="Stock ticker symbol"),
    period: str = Query("3mo", description="History period used to compute indicators"),
):
    """
    Retrieves computed technical indicators (RSI, MACD, Moving Averages, Volatility, Momentum).
    """
    try:
        req_sym, norm_sym = normalize_symbol_pair(symbol)
    except SymbolNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    if not p2_get_indicators or not p2_get_price_history:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Indicator calculation service is currently unavailable.",
        )

    try:
        history = p2_get_price_history(norm_sym, period=period)
        indicators = p2_get_indicators(norm_sym, history)
        indicators["requested_symbol"] = req_sym
        indicators["normalized_symbol"] = norm_sym
        return indicators
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error computing indicators: {str(exc)}",
        )


@market_router.get("/news/{symbol}", summary="Get Financial News & Sentiment")
def get_stock_news(
    symbol: str = Path(..., description="Stock ticker symbol"),
):
    """
    Retrieves latest news headlines, summaries, and rule-based sentiment scores.
    """
    try:
        req_sym, norm_sym = normalize_symbol_pair(symbol)
    except SymbolNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    if not p2_get_news:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="News service is currently unavailable.",
        )

    try:
        news_data = p2_get_news(norm_sym)
        articles = news_data.get("news", [])
        sentiment_summary = {}

        if articles and p2_get_sentiment:
            sentiment_summary = p2_get_sentiment(articles)

        return {
            "requested_symbol": req_sym,
            "normalized_symbol": norm_sym,
            "source": news_data.get("source", "unknown"),
            "status": news_data.get("status", "ok"),
            "count": len(articles),
            "sentiment": sentiment_summary,
            "articles": articles,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving news: {str(exc)}",
        )
