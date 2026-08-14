import numpy as np
import pandas as pd

def calculate_spy_trend_score(spy_series: pd.Series) -> dict:
    """
    Calculate S&P 500 Trend & Momentum Score (0-100).
    
    Logic:
    - SPY distance relative to 200-day SMA: dist_200d = ((SPY - SMA_200) / SMA_200) * 100
    - Mapping:
      * +10% or higher -> 100
      * -10% or lower -> 0
    - Golden Cross check (50-day SMA > 200-day SMA) adds +5 bonus (clamped to 100).
    """
    if spy_series is None or spy_series.empty or len(spy_series) < 50:
        return {
            "score": 50.0,
            "spy_price": 500.0,
            "sma_200": 480.0,
            "sma_50": 490.0,
            "dist_200d_pct": 4.17,
            "golden_cross": True,
            "regime": "Uptrend",
            "explanation": "Insufficient SPY data available. Returning neutral score."
        }
        
    clean_spy = spy_series.dropna()
    spy_price = float(clean_spy.iloc[-1])
    
    sma_200 = float(clean_spy.rolling(200).mean().iloc[-1]) if len(clean_spy) >= 200 else float(clean_spy.mean())
    sma_50 = float(clean_spy.rolling(50).mean().iloc[-1]) if len(clean_spy) >= 50 else float(clean_spy.mean())
    
    dist_200d_pct = float(((spy_price - sma_200) / sma_200) * 100.0)
    golden_cross = bool(sma_50 > sma_200)
    
    if dist_200d_pct >= 10.0:
        base_score = 100.0
    elif dist_200d_pct <= -10.0:
        base_score = 0.0
    else:
        base_score = ((dist_200d_pct - (-10.0)) / (10.0 - (-10.0))) * 100.0
        
    bonus = 5.0 if golden_cross else 0.0
    raw_score = base_score + bonus
    score = float(np.clip(raw_score, 0.0, 100.0))
    
    if dist_200d_pct >= 5.0:
        regime = "Strong Bullish Trend (Above 200D SMA)"
    elif dist_200d_pct >= 0.0:
        regime = "Mild Bullish Trend"
    elif dist_200d_pct >= -5.0:
        regime = "Pullback / Mild Bearish Trend"
    else:
        regime = "Downtrend / Below 200D SMA"
        
    explanation = (
        f"S&P 500 (SPY) is at ${spy_price:.2f}, which is {dist_200d_pct:+.2f}% relative to 200-day SMA (${sma_200:.2f}). "
        f"Golden Cross (50D > 200D): {'Yes' if golden_cross else 'No'}. Regime: {regime}."
    )
    
    return {
        "score": round(score, 1),
        "spy_price": round(spy_price, 2),
        "sma_200": round(sma_200, 2),
        "sma_50": round(sma_50, 2),
        "dist_200d_pct": round(dist_200d_pct, 2),
        "golden_cross": golden_cross,
        "regime": regime,
        "explanation": explanation
    }
