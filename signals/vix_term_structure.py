import numpy as np
import pandas as pd

def calculate_vix_term_structure_score(vix_spot_series: pd.Series, vix_3m_series: pd.Series) -> dict:
    """
    Calculate VIX Term Structure Score (0-100).
    
    Logic:
    - Ratio = front-month VIX / VIX3M
    - Ratio < 1.0 = Contango (calm, normal) = High Score
    - Ratio >= 1.0 = Backwardation (stress, inverted curve) = Low Score
    - Linear Mapping:
      * 0.85 -> 100
      * 1.15 -> 0
    - Score clamped to [0, 100].
    """
    if vix_spot_series is None or vix_3m_series is None or vix_spot_series.empty or vix_3m_series.empty:
        return {
            "score": 50.0,
            "vix_spot": 20.0,
            "vix_3m": 22.0,
            "ratio": 0.91,
            "regime": "Contango (Normal)",
            "explanation": "No VIX term structure data available. Returning neutral score."
        }
    
    clean_spot = vix_spot_series.dropna()
    clean_3m = vix_3m_series.dropna()
    
    if hasattr(clean_spot.index, 'tz') and clean_spot.index.tz is not None:
        clean_spot.index = clean_spot.index.tz_localize(None)
    if hasattr(clean_3m.index, 'tz') and clean_3m.index.tz is not None:
        clean_3m.index = clean_3m.index.tz_localize(None)
    
    # Align dates
    combined = pd.concat([clean_spot, clean_3m], axis=1, join="inner").dropna()
    if combined.empty:
        vix_spot_val = float(clean_spot.iloc[-1])
        vix_3m_val = float(clean_3m.iloc[-1])
    else:
        vix_spot_val = float(combined.iloc[-1, 0])
        vix_3m_val = float(combined.iloc[-1, 1])
        
    if vix_3m_val == 0:
        ratio = 1.0
    else:
        ratio = vix_spot_val / vix_3m_val
        
    # Linear interpolation: 0.85 -> 100, 1.15 -> 0
    if ratio <= 0.85:
        score = 100.0
    elif ratio >= 1.15:
        score = 0.0
    else:
        score = 100.0 - ((ratio - 0.85) / (1.15 - 0.85)) * 100.0
        
    score = float(np.clip(score, 0.0, 100.0))
    
    if ratio < 0.92:
        regime = "Deep Contango (Very Low Stress)"
    elif ratio < 1.0:
        regime = "Contango (Normal Market Calm)"
    elif ratio < 1.08:
        regime = "Mild Backwardation (Early Volatility Spike)"
    else:
        regime = "Severe Backwardation (Acute Market Panic)"
        
    explanation = (
        f"VIX / VIX3M ratio is {ratio:.3f} (VIX: {vix_spot_val:.2f}, VIX3M: {vix_3m_val:.2f}). "
        f"Market is in {regime}."
    )
    
    return {
        "score": round(score, 1),
        "vix_spot": round(vix_spot_val, 2),
        "vix_3m": round(vix_3m_val, 2),
        "ratio": round(ratio, 3),
        "regime": regime,
        "explanation": explanation
    }
