import numpy as np
import pandas as pd

def calculate_vix_level_score(vix_series: pd.Series) -> dict:
    """
    Calculate VIX Level Score (0-100).
    
    Logic:
    - Percentile-rank current VIX against trailing 1 year (252 days).
    - Base Score = 100 - Percentile (Low VIX = Low percentile = High deployment score).
    - Bonus +5 if VIX < 15.
    - Penalty -10 if VIX > 30.
    - Score clamped to [0, 100].
    """
    if vix_series is None or vix_series.empty:
        return {
            "score": 50.0,
            "current_vix": 20.0,
            "percentile": 50.0,
            "bonus": 0,
            "penalty": 0,
            "explanation": "No VIX data available. Returning neutral score."
        }
    
    clean_vix = vix_series.dropna()
    current_vix = float(clean_vix.iloc[-1])
    
    # Trailing 1 year (last 252 trading days)
    history_1y = clean_vix.tail(252)
    percentile = float((history_1y <= current_vix).mean() * 100.0)
    
    # Base score (lower VIX = higher score)
    base_score = 100.0 - percentile
    
    # Bonus / Penalty
    bonus = 5.0 if current_vix < 15.0 else 0.0
    penalty = -10.0 if current_vix > 30.0 else 0.0
    
    raw_score = base_score + bonus + penalty
    score = float(np.clip(raw_score, 0.0, 100.0))
    
    if current_vix < 15.0:
        regime = "Low Volatility (Complacent / Calm)"
    elif current_vix <= 22.0:
        regime = "Normal Volatility"
    elif current_vix <= 30.0:
        regime = "Elevated Volatility (Caution)"
    else:
        regime = "High Volatility (Fear / Stress)"
        
    explanation = f"Current VIX is {current_vix:.2f} ({percentile:.1f}th percentile over 1Y). {regime}."
    if bonus > 0:
        explanation += " Received +5 bonus for VIX < 15."
    if penalty < 0:
        explanation += " Received -10 penalty for VIX > 30."

    return {
        "score": round(score, 1),
        "current_vix": round(current_vix, 2),
        "percentile": round(percentile, 1),
        "base_score": round(base_score, 1),
        "bonus": bonus,
        "penalty": penalty,
        "regime": regime,
        "explanation": explanation
    }
