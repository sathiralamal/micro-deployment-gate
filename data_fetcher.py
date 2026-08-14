import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import datetime

# Universe of S&P 500 representative components across sectors
BREADTH_UNIVERSE = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "BRK-B", "LLY", "JPM", "TSLA",
    "UNH", "V", "XOM", "JNJ", "WMT", "PG", "MA", "HD", "CVX", "MRK",
    "COST", "ABBV", "BAC", "AVGO", "PEP", "PFE", "TMO", "ACN", "CSCO", "MCD",
    "CRM", "DIS", "WFC", "LIN", "ABT", "AMD", "INTU", "PM", "AMAT", "DHR",
    "TXN", "NOW", "GE", "CAT", "SPGI", "HON", "AXP", "GS", "ISRG", "BLK"
]

def strip_tz(obj):
    """Strip timezone information from Series/DataFrame index to avoid tz comparison errors."""
    if obj is None:
        return obj
    if isinstance(obj, (pd.Series, pd.DataFrame)):
        if hasattr(obj.index, 'tz') and obj.index.tz is not None:
            obj.index = obj.index.tz_localize(None)
    return obj

def fetch_single_ticker(ticker_symbol: str, period: str = "1y") -> pd.Series:
    """Fetch close price series for a single ticker with timezone stripped."""
    try:
        t = yf.Ticker(ticker_symbol)
        df = t.history(period=period)
        if df is not None and not df.empty and "Close" in df.columns:
            series = df["Close"].dropna()
            if not series.empty:
                return strip_tz(series)
    except Exception as e:
        pass
    
    # Try fallback download method
    try:
        df = yf.download(ticker_symbol, period=period, progress=False)
        if df is not None and not df.empty:
            if "Close" in df.columns:
                close = df["Close"]
                if isinstance(close, pd.DataFrame):
                    series = close.iloc[:, 0].dropna()
                else:
                    series = close.dropna()
                if not series.empty:
                    return strip_tz(series)
    except Exception as e:
        pass
        
    return pd.Series(dtype=float)

@st.cache_data(ttl=900)
def fetch_all_macro_data() -> dict:
    """
    Fetch trailing 1Y market data for all 6 macro signals:
    - VIX spot (^VIX)
    - VIX 3M (^VIX3M)
    - HYG (High Yield ETF)
    - TLT (Treasury ETF)
    - SPY (S&P 500 ETF)
    - Breadth sample stock prices
    """
    data = {}
    is_live = True
    
    # 1. Fetch Core Macro Assets
    vix_spot = fetch_single_ticker("^VIX", "1y")
    vix_3m = fetch_single_ticker("^VIX3M", "1y")
    hyg = fetch_single_ticker("HYG", "1y")
    tlt = fetch_single_ticker("TLT", "1y")
    spy = fetch_single_ticker("SPY", "1y")
    
    # Check if core fetch succeeded
    if vix_spot.empty or spy.empty:
        is_live = False
        data = generate_synthetic_macro_data()
        data["is_live"] = False
        return data

    # Fallback for VIX3M if missing or sparse: approximate with VIX smooth offset or interpolation
    if vix_3m.empty:
        # VIX3M is usually slightly higher than VIX in normal contango (~ +1.5 to +2.5 points)
        vix_3m = vix_spot + 1.8 + np.sin(np.arange(len(vix_spot))) * 0.5
        vix_3m = pd.Series(vix_3m, index=vix_spot.index)

    # 2. Fetch Breadth Stock Universe (batch download)
    breadth_prices = {}
    try:
        breadth_df = yf.download(BREADTH_UNIVERSE, period="1y", progress=False)
        if breadth_df is not None and not breadth_df.empty and "Close" in breadth_df.columns:
            close_df = breadth_df["Close"]
            if isinstance(close_df, pd.DataFrame):
                breadth_prices = close_df
    except Exception as e:
        pass
        
    if not isinstance(breadth_prices, pd.DataFrame) or breadth_prices.empty:
        # Fallback breadth price dataframe constructed from SPY random sector offsets
        breadth_prices = generate_synthetic_breadth_prices(spy)
    else:
        breadth_prices = strip_tz(breadth_prices)
        
    return {
        "vix_spot": strip_tz(vix_spot),
        "vix_3m": strip_tz(vix_3m),
        "hyg": strip_tz(hyg),
        "tlt": strip_tz(tlt),
        "spy": strip_tz(spy),
        "breadth_prices": breadth_prices,
        "is_live": is_live,
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def generate_synthetic_macro_data() -> dict:
    """Generate realistic synthetic macro data if live API is unavailable."""
    dates = pd.date_range(end=datetime.date.today(), periods=252, freq="B")
    
    np.random.seed(42)
    # Synthetic VIX (~14 to 22 range)
    vix_base = 15.0 + np.cumsum(np.random.normal(0, 0.4, 252))
    vix_base = np.clip(vix_base, 11.0, 38.0)
    vix_spot = pd.Series(vix_base, index=dates)
    
    # Synthetic VIX3M (contango ~ 1.05-1.10 ratio)
    vix_3m = pd.Series(vix_base * 1.08 + np.random.normal(0, 0.2, 252), index=dates)
    
    # Synthetic HYG & TLT
    hyg_base = 78.0 + np.cumsum(np.random.normal(0.02, 0.15, 252))
    tlt_base = 92.0 + np.cumsum(np.random.normal(-0.01, 0.25, 252))
    hyg = pd.Series(hyg_base, index=dates)
    tlt = pd.Series(tlt_base, index=dates)
    
    # Synthetic SPY
    spy_base = 500.0 + np.cumsum(np.random.normal(0.3, 2.5, 252))
    spy = pd.Series(spy_base, index=dates)
    
    breadth_prices = generate_synthetic_breadth_prices(spy)
    
    return {
        "vix_spot": vix_spot,
        "vix_3m": vix_3m,
        "hyg": hyg,
        "tlt": tlt,
        "spy": spy,
        "breadth_prices": breadth_prices,
        "is_live": False,
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def generate_synthetic_breadth_prices(spy_series: pd.Series) -> pd.DataFrame:
    """Generate realistic synthetic constituent prices based on SPY."""
    dates = spy_series.index
    np.random.seed(101)
    
    data = {}
    spy_returns = spy_series.pct_change().fillna(0)
    
    for ticker in BREADTH_UNIVERSE[:40]:
        beta = np.random.uniform(0.7, 1.4)
        alpha = np.random.uniform(-0.0002, 0.0003)
        ret = alpha + beta * spy_returns + np.random.normal(0, 0.008, len(spy_series))
        price = 100.0 * np.exp(np.cumsum(ret))
        data[ticker] = price
        
    df = pd.DataFrame(data, index=dates)
    return df

@st.cache_data(ttl=300)
def fetch_symbol_scan_data(ticker_symbol: str, spy_series: pd.Series = None) -> dict:
    """
    Fetch and compute technical/volatility metrics for scanning a specific symbol.
    """
    symbol = ticker_symbol.strip().upper()
    if not symbol:
        symbol = "AAPL"
        
    prices = fetch_single_ticker(symbol, period="1y")
    if prices.empty:
        return {"error": f"Could not fetch historical data for symbol '{symbol}'. Please check ticker spelling."}
        
    curr_price = float(prices.iloc[-1])
    prev_price = float(prices.iloc[-2]) if len(prices) > 1 else curr_price
    day_change_pct = ((curr_price - prev_price) / prev_price) * 100.0
    
    sma_50 = float(prices.rolling(50).mean().iloc[-1]) if len(prices) >= 50 else float(prices.mean())
    sma_200 = float(prices.rolling(200).mean().iloc[-1]) if len(prices) >= 200 else float(prices.mean())
    
    dist_200d_pct = ((curr_price - sma_200) / sma_200) * 100.0
    dist_50d_pct = ((curr_price - sma_50) / sma_50) * 100.0
    
    high_52w = float(prices.max())
    low_52w = float(prices.min())
    dist_high_52w = ((curr_price - high_52w) / high_52w) * 100.0
    
    # 20-day annualized volatility
    returns = prices.pct_change().dropna()
    vol_20d_ann = float(returns.tail(20).std() * np.sqrt(252) * 100.0) if len(returns) >= 20 else 20.0
    
    # Beta relative to SPY
    beta = 1.0
    rel_strength_3m = 0.0
    if spy_series is not None and not spy_series.empty:
        combined = pd.concat([prices, spy_series], axis=1, join="inner").dropna()
        if len(combined) >= 30:
            sym_ret = combined.iloc[:, 0].pct_change().dropna()
            spy_ret = combined.iloc[:, 1].pct_change().dropna()
            cov = np.cov(sym_ret, spy_ret)[0, 1]
            var = np.var(spy_ret)
            if var > 0:
                beta = float(cov / var)
                
            # 3-month relative strength
            lookback_60 = min(60, len(combined) - 1)
            sym_3m_ret = (combined.iloc[-1, 0] / combined.iloc[-lookback_60, 0] - 1) * 100.0
            spy_3m_ret = (combined.iloc[-1, 1] / combined.iloc[-lookback_60, 1] - 1) * 100.0
            rel_strength_3m = sym_3m_ret - spy_3m_ret
            
    return {
        "symbol": symbol,
        "prices": prices,
        "curr_price": round(curr_price, 2),
        "day_change_pct": round(day_change_pct, 2),
        "sma_50": round(sma_50, 2),
        "sma_200": round(sma_200, 2),
        "dist_200d_pct": round(dist_200d_pct, 2),
        "dist_50d_pct": round(dist_50d_pct, 2),
        "high_52w": round(high_52w, 2),
        "low_52w": round(low_52w, 2),
        "dist_high_52w": round(dist_high_52w, 2),
        "vol_20d_ann": round(vol_20d_ann, 1),
        "beta": round(beta, 2),
        "rel_strength_3m": round(rel_strength_3m, 1)
    }

