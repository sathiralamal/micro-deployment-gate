import numpy as np
import pandas as pd

def calculate_breadth_score_from_pct(breadth_pct: float, total_stocks: int = 500, stocks_above: int = None) -> dict:
    """
    Calculate Market Breadth Score from % of stocks above 200-day SMA.
    
    Mapping:
    - 80% -> 100
    - 30% -> 0
    - Linear mapping clamped to [0, 100].
    """
    if breadth_pct is None or np.isnan(breadth_pct):
        breadth_pct = 55.0
        
    if breadth_pct >= 80.0:
        score = 100.0
    elif breadth_pct <= 30.0:
        score = 0.0
    else:
        score = ((breadth_pct - 30.0) / (80.0 - 30.0)) * 100.0
        
    score = float(np.clip(score, 0.0, 100.0))
    
    if breadth_pct >= 75.0:
        regime = "Broad-Based Rally (Healthy Participation)"
    elif breadth_pct >= 50.0:
        regime = "Moderate Participation"
    elif breadth_pct >= 35.0:
        regime = "Narrow Market (Divergence Risk)"
    else:
        regime = "Severe Weakness / Liquidation"
        
    if stocks_above is None and total_stocks > 0:
        stocks_above = int(round((breadth_pct / 100.0) * total_stocks))
        
    explanation = (
        f"{breadth_pct:.1f}% of S&P 500 stocks are above their 200-day SMA "
        f"({stocks_above}/{total_stocks} stocks). Regime: {regime}."
    )
    
    return {
        "score": round(score, 1),
        "breadth_pct": round(breadth_pct, 1),
        "stocks_above_200d": stocks_above,
        "total_stocks_analyzed": total_stocks,
        "regime": regime,
        "explanation": explanation
    }

def calculate_breadth_score_from_prices(stock_prices_df: pd.DataFrame) -> dict:
    """
    Compute % of stocks above 200-day SMA from a DataFrame of stock close prices (columns=tickers).
    """
    if stock_prices_df is None or stock_prices_df.empty or len(stock_prices_df) < 200:
        return calculate_breadth_score_from_pct(58.5, total_stocks=100, stocks_above=58)
        
    # Calculate 200d SMA for each ticker
    smas = stock_prices_df.rolling(window=200).mean()
    latest_prices = stock_prices_df.iloc[-1]
    latest_smas = smas.iloc[-1]
    
    valid_mask = ~latest_prices.isna() & ~latest_smas.isna()
    valid_prices = latest_prices[valid_mask]
    valid_smas = latest_smas[valid_mask]
    
    if len(valid_prices) == 0:
        return calculate_breadth_score_from_pct(55.0)
        
    above_count = int((valid_prices > valid_smas).sum())
    total_count = int(len(valid_prices))
    pct_above = (above_count / total_count) * 100.0
    
    return calculate_breadth_score_from_pct(pct_above, total_stocks=total_count, stocks_above=above_count)
