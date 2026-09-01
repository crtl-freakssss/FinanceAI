import pandas as pd
import numpy as np

def get_indicators(symbol, history_data):
    """
    Computes technical indicators for a given symbol based on historical OHLCV data.
    Provides DATA ONLY — does not make investment recommendations or decisions.
    
    Indicators computed:
    - ema9, ema21
    - sma20, sma50
    - rsi (14 period)
    - macd (line, signal, histogram)
    - volatility (annualized standard deviation of returns)
    - momentum (10-period rate of change)
    - average_volume (20-period rolling average)
    - percentage_price_change (period return)
    """
    empty_result = {
        "symbol": symbol,
        "ema9": None,
        "ema21": None,
        "sma20": None,
        "sma50": None,
        "rsi": None,
        "macd": None,
        "macd_signal": None,
        "macd_histogram": None,
        "volatility": None,
        "momentum": None,
        "average_volume": None,
        "percentage_price_change": None,
        "data_points": 0,
        "status": "Insufficient data"
    }

    if not history_data or "history" not in history_data or not history_data["history"]:
        return empty_result

    df = pd.DataFrame(history_data["history"])
    if 'Close' not in df.columns or len(df) < 2:
        return empty_result

    close = pd.to_numeric(df['Close'], errors='coerce')
    volume = pd.to_numeric(df['Volume'], errors='coerce') if 'Volume' in df.columns else None

    # EMA 9 & 21
    ema9_series = close.ewm(span=9, adjust=False).mean()
    ema21_series = close.ewm(span=21, adjust=False).mean()
    ema9 = ema9_series.iloc[-1]
    ema21 = ema21_series.iloc[-1]

    # SMA 20 & 50
    sma20 = close.rolling(window=min(20, len(close))).mean().iloc[-1]
    sma50 = close.rolling(window=min(50, len(close))).mean().iloc[-1] if len(close) >= 10 else None

    # RSI (14 period standard Wilder's method approximation)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0.0)).rolling(window=min(14, len(close)-1)).mean()
    loss = ((-delta).where(delta < 0, 0.0)).rolling(window=min(14, len(close)-1)).mean()
    
    last_loss = loss.iloc[-1] if not loss.empty else 0.0
    last_gain = gain.iloc[-1] if not gain.empty else 0.0
    
    if last_loss == 0.0 or pd.isna(last_loss):
        rsi = 100.0 if last_gain > 0 else 50.0
    else:
        rs = last_gain / last_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))

    # MACD (12, 26, 9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    macd_signal = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - macd_signal

    # Volatility (Annualized std dev of daily percentage returns)
    returns = close.pct_change().dropna()
    volatility = (returns.std() * np.sqrt(252)) if len(returns) > 1 else None

    # Momentum (10-period rate of change)
    if len(close) >= 11:
        prev_close = close.iloc[-11]
        momentum = ((close.iloc[-1] - prev_close) / prev_close) if prev_close != 0 else 0.0
    else:
        first_close = close.iloc[0]
        momentum = ((close.iloc[-1] - first_close) / first_close) if first_close != 0 else 0.0

    # Average Volume
    avg_vol = volume.rolling(window=min(20, len(volume))).mean().iloc[-1] if volume is not None else None

    # Percentage price change over entire available history
    first_val = close.iloc[0]
    last_val = close.iloc[-1]
    pct_change = ((last_val - first_val) / first_val * 100.0) if first_val != 0 else 0.0

    return {
        "symbol": symbol,
        "ema9": round(float(ema9), 2) if pd.notna(ema9) else None,
        "ema21": round(float(ema21), 2) if pd.notna(ema21) else None,
        "sma20": round(float(sma20), 2) if pd.notna(sma20) else None,
        "sma50": round(float(sma50), 2) if pd.notna(sma50) else None,
        "rsi": round(float(rsi), 2) if pd.notna(rsi) else None,
        "macd": round(float(macd_line.iloc[-1]), 2) if pd.notna(macd_line.iloc[-1]) else None,
        "macd_signal": round(float(macd_signal.iloc[-1]), 2) if pd.notna(macd_signal.iloc[-1]) else None,
        "macd_histogram": round(float(macd_hist.iloc[-1]), 2) if pd.notna(macd_hist.iloc[-1]) else None,
        "volatility": round(float(volatility), 4) if pd.notna(volatility) else None,
        "momentum": round(float(momentum), 4) if pd.notna(momentum) else None,
        "average_volume": int(avg_vol) if pd.notna(avg_vol) else None,
        "percentage_price_change": round(float(pct_change), 2) if pd.notna(pct_change) else None,
        "data_points": len(df),
        "status": "Calculated"
    }
