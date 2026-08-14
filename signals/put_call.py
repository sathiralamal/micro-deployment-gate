import numpy as np
import pandas as pd

def calculate_put_call_score(vix_series: pd.Series) -> dict:
    """
    Calculate Put/Call Sentiment Proxy Score (0-100) using VIX 20-day Rate of Change (ROC).
    
    Logic:
    - VIX 20-day ROC = ((VIX_current - VIX_20d) / VIX_20d) * 100
    - Rapidly rising VIX = Fear / Hedging Demand = Low Score
    - Rapidly declining VIX = Calm / Complacency = High Score
    - Mapping:
      * ROC -30% -> 100
      * ROC +50% -> 0
    - Score clamped to [0, 100].
    """
    if vix_series is None or vix_series.empty or len(vix_series) < 21:
        return {
            "score": 50.0,
            "roc_20d": 0.0,
            "current_vix": 20.0,
            "vix_20d_ago": 20.0,
            "regime": "Neutral Sentiment",
            "explanation": "Insufficient VIX history to calculate 20-day ROC. Returning neutral score."
        }
        
    clean_vix = vix_series.dropna()
    current_vix = float(clean_vix.iloc[-1])
    
    # 20 trading days prior
    lookback = min(20, len(clean_vix) - 1)
    vix_20d_ago = float(clean_vix.iloc[-(lookback + 1)])
    
    if vix_20d_ago == 0:
        roc_20d = 0.0
    else:
        roc_20d = float(((current_vix - vix_20d_ago) / vix_20d_ago) * 100.0)
        
    # Linear mapping: -30% -> 100, +50% -> 0
    if roc_20d <= -30.0:
        score = 100.0
    elif roc_20d >= 50.0:
        score = 0.0
    else:
        score = 100.0 - ((roc_20d - (-30.0)) / (50.0 - (-30.0))) * 100.0
        
    score = float(np.clip(score, 0.0, 100.0))
    
    if roc_20d <= -20.0:
        regime = "Collapsing Volatility (Strong Risk-On Sentiment)"
    elif roc_20d <= 10.0:
        regime = "Stable Sentiment"
    elif roc_20d <= 35.0:
        regime = "Rising Hedging Demand / Caution"
    else:
        regime = "Panic Hedging / Acute Volatility Spike"
        
    explanation = (
        f"VIX 20-day Rate of Change is {roc_20d:+.1f}% "
        f"(Current VIX: {current_vix:.2f}, 20D Ago: {vix_20d_ago:.2f}). "
        f"Regime: {regime}."
    )
    
    return {
        "score": round(score, 1),
        "roc_20d": round(roc_20d, 1),
        "current_vix": round(current_vix, 2),
        "vix_20d_ago": round(vix_20d_ago, 2),
        "regime": regime,
        "explanation": explanation
    }
