import numpy as np
import pandas as pd

def calculate_credit_spreads_score(hyg_series: pd.Series, tlt_series: pd.Series) -> dict:
    """
    Calculate Credit Spreads Score (0-100) using HYG vs TLT spread proxy.
    
    Logic:
    - Credit Spread Proxy = TLT / HYG (Treasuries relative to High Yield Corporate Bonds).
    - Higher ratio = Flight to Quality / Widening Spreads.
    - Lower ratio = Risk-On / Tight Credit Spreads.
    - Z-Score calculated against 1-year trailing history (252 days).
    - Linear Mapping:
      * Tight Spreads (z = -2.0) -> Score 100
      * Wide Spreads (z = +2.0) -> Score 0
    - Score clamped to [0, 100].
    """
    if hyg_series is None or tlt_series is None or hyg_series.empty or tlt_series.empty:
        return {
            "score": 50.0,
            "z_score": 0.0,
            "current_ratio": 1.10,
            "mean_ratio": 1.10,
            "regime": "Neutral Credit Environment",
            "explanation": "No HYG/TLT credit data available. Returning neutral score."
        }
        
    clean_hyg = hyg_series.dropna()
    clean_tlt = tlt_series.dropna()
    
    if hasattr(clean_hyg.index, 'tz') and clean_hyg.index.tz is not None:
        clean_hyg.index = clean_hyg.index.tz_localize(None)
    if hasattr(clean_tlt.index, 'tz') and clean_tlt.index.tz is not None:
        clean_tlt.index = clean_tlt.index.tz_localize(None)
        
    combined = pd.concat([clean_hyg, clean_tlt], axis=1, join="inner").dropna()
    combined.columns = ["HYG", "TLT"]
    
    if len(combined) < 20:
        return {
            "score": 50.0,
            "z_score": 0.0,
            "current_ratio": 1.10,
            "mean_ratio": 1.10,
            "regime": "Insufficient Data",
            "explanation": "Insufficient overlapping HYG and TLT history."
        }
        
    # Spread proxy: TLT / HYG ratio (higher = wider credit spread stress)
    spread_ratio = combined["TLT"] / combined["HYG"]
    history_1y = spread_ratio.tail(252)
    
    current_ratio = float(history_1y.iloc[-1])
    mean_ratio = float(history_1y.mean())
    std_ratio = float(history_1y.std())
    
    if std_ratio == 0:
        z_score = 0.0
    else:
        z_score = float((current_ratio - mean_ratio) / std_ratio)
        
    # Mapping: z = -2 -> 100, z = +2 -> 0
    # score = 50 - 25 * z
    raw_score = 50.0 - 25.0 * z_score
    score = float(np.clip(raw_score, 0.0, 100.0))
    
    if z_score <= -1.2:
        regime = "Ultra-Tight Spreads (Strong Risk-On Credit Appetite)"
    elif z_score <= 0.0:
        regime = "Normal / Tight Credit Spreads"
    elif z_score <= 1.2:
        regime = "Moderately Widening Spreads (Credit Caution)"
    else:
        regime = "Distressed Credit Spreads (Flight to Treasuries)"
        
    explanation = (
        f"HYG vs TLT spread proxy z-score is {z_score:+.2f} "
        f"(Current TLT/HYG Ratio: {current_ratio:.3f}, 1Y Mean: {mean_ratio:.3f}). "
        f"Regime: {regime}."
    )
    
    return {
        "score": round(score, 1),
        "z_score": round(z_score, 2),
        "current_ratio": round(current_ratio, 3),
        "mean_ratio": round(mean_ratio, 3),
        "std_ratio": round(std_ratio, 3),
        "regime": regime,
        "explanation": explanation
    }
