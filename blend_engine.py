import pandas as pd
import numpy as np

from signals.vix_level import calculate_vix_level_score
from signals.vix_term_structure import calculate_vix_term_structure_score
from signals.breadth import calculate_breadth_score_from_prices, calculate_breadth_score_from_pct
from signals.credit_spreads import calculate_credit_spreads_score
from signals.put_call import calculate_put_call_score
from signals.spy_trend import calculate_spy_trend_score

DEFAULT_WEIGHTS = {
    "vix_level": 1.0 / 6.0,
    "vix_term_structure": 1.0 / 6.0,
    "breadth": 1.0 / 6.0,
    "credit_spreads": 1.0 / 6.0,
    "put_call": 1.0 / 6.0,
    "spy_trend": 1.0 / 6.0
}

def compute_all_signals(data: dict) -> dict:
    """Compute individual signal dicts from fetched macro data."""
    vix_spot = data.get("vix_spot")
    vix_3m = data.get("vix_3m")
    hyg = data.get("hyg")
    tlt = data.get("tlt")
    spy = data.get("spy")
    breadth_prices = data.get("breadth_prices")
    
    # 1. VIX Level
    sig_vix_level = calculate_vix_level_score(vix_spot)
    
    # 2. VIX Term Structure
    sig_vix_term = calculate_vix_term_structure_score(vix_spot, vix_3m)
    
    # 3. Market Breadth
    if isinstance(breadth_prices, pd.DataFrame) and not breadth_prices.empty:
        sig_breadth = calculate_breadth_score_from_prices(breadth_prices)
    else:
        sig_breadth = calculate_breadth_score_from_pct(58.0)
        
    # 4. Credit Spreads
    sig_credit = calculate_credit_spreads_score(hyg, tlt)
    
    # 5. Put/Call Sentiment (VIX 20D ROC)
    sig_put_call = calculate_put_call_score(vix_spot)
    
    # 6. SPY Trend & Momentum
    sig_spy_trend = calculate_spy_trend_score(spy)
    
    return {
        "vix_level": sig_vix_level,
        "vix_term_structure": sig_vix_term,
        "breadth": sig_breadth,
        "credit_spreads": sig_credit,
        "put_call": sig_put_call,
        "spy_trend": sig_spy_trend
    }

def blend_deployment_score(signals: dict, custom_weights: dict = None) -> dict:
    """
    Blends the 6 signal scores using specified weights into a master Deployment Score (0-100).
    Returns deployment gating decision and capital allocation metrics.
    """
    if custom_weights is None:
        weights = DEFAULT_WEIGHTS.copy()
    else:
        weights = custom_weights.copy()
        
    # Normalize weights so they sum to 1.0
    total_w = sum(weights.values())
    if total_w > 0:
        norm_weights = {k: v / total_w for k, v in weights.items()}
    else:
        norm_weights = DEFAULT_WEIGHTS.copy()
        
    score_breakdown = []
    blended_score = 0.0
    
    signal_names = {
        "vix_level": ("VIX Level", "Volatility"),
        "vix_term_structure": ("VIX Term Structure", "Volatility"),
        "breadth": ("Market Breadth (% > 200d)", "Participation"),
        "credit_spreads": ("Credit Spreads (HYG/TLT)", "Credit Risk"),
        "put_call": ("Put/Call Sentiment (VIX 20D ROC)", "Sentiment"),
        "spy_trend": ("S&P 500 Trend (SPY 200D)", "Trend")
    }
    
    for key, (name, category) in signal_names.items():
        sig_data = signals.get(key, {})
        s_score = float(sig_data.get("score", 50.0))
        weight = float(norm_weights.get(key, 1.0 / 6.0))
        contrib = s_score * weight
        blended_score += contrib
        
        score_breakdown.append({
            "key": key,
            "signal_name": name,
            "category": category,
            "score": round(s_score, 1),
            "weight": round(weight * 100.0, 1),
            "contribution": round(contrib, 1),
            "regime": sig_data.get("regime", "N/A"),
            "explanation": sig_data.get("explanation", "")
        })
        
    final_score = round(float(np.clip(blended_score, 0.0, 100.0)), 1)
    
    # Deployment Gating Matrix & Recommendation
    if final_score >= 80.0:
        gating_status = "GREEN GATE (Risk-On)"
        answer_summary = "YES — DEPLOY CAPITAL AGGRESSIVELY"
        recommended_capital_pct = "90% - 100%"
        action_plan = "Full Capital Deployment Mode. Macro backdrop is clear with low volatility, contango term structure, tight credit spreads, and strong market breadth. Accelerate DCA and deploy tactical reserves into market pullbacks."
        badge_color = "#10b981"  # Emerald Green
    elif final_score >= 60.0:
        gating_status = "LIME GATE (Moderate Risk-On)"
        answer_summary = "YES — DEPLOY CAPITAL MODERATELY"
        recommended_capital_pct = "70% - 85%"
        action_plan = "Standard Deployment Mode. Macro conditions are favorable. Continue steady dollar-cost averaging and opportunistic additions to core equity positions."
        badge_color = "#84cc16"  # Lime Green
    elif final_score >= 40.0:
        gating_status = "YELLOW GATE (Cautious Neutral)"
        answer_summary = "CAUTIOUS / SELECTIVE DEPLOYMENT ONLY"
        recommended_capital_pct = "40% - 60%"
        action_plan = "Cautious Stance. Mixed macro signals detected. Limit deployment to high-conviction quality assets. Maintain cash buffer and avoid aggressive leverage or speculative entries."
        badge_color = "#eab308"  # Amber Yellow
    elif final_score >= 20.0:
        gating_status = "ORANGE GATE (Defensive / Risk-Off)"
        answer_summary = "DEFENSIVE — SLOW DOWN DEPLOYMENT"
        recommended_capital_pct = "20% - 35%"
        action_plan = "Defensive Stance. Elevated market volatility, expanding credit spreads, or deteriorating breadth. Pause aggressive new buys, tighten stop-losses, and park capital in short-duration yield."
        badge_color = "#f97316"  # Orange
    else:
        gating_status = "RED GATE (Gated / Capital Preservation)"
        answer_summary = "NO — HALT CAPITAL DEPLOYMENT"
        recommended_capital_pct = "0% - 15%"
        action_plan = "Gate Closed. High macro stress, volatility panic, or backwardation detected. Capital preservation is priority #1. Gate stays closed until signals stabilize."
        badge_color = "#ef4444"  # Red
        
    df_breakdown = pd.DataFrame(score_breakdown)
    
    return {
        "final_score": final_score,
        "gating_status": gating_status,
        "answer_summary": answer_summary,
        "recommended_capital_pct": recommended_capital_pct,
        "action_plan": action_plan,
        "badge_color": badge_color,
        "breakdown": df_breakdown,
        "raw_signals": signals
    }

def _strip_tz(obj):
    if obj is not None and hasattr(obj, 'index') and hasattr(obj.index, 'tz') and obj.index.tz is not None:
        obj.index = obj.index.tz_localize(None)
    return obj

def calculate_historical_scores(data: dict, weights: dict = None, lookback_days: int = 90) -> pd.DataFrame:
    """Calculate trailing history of blended deployment score over lookback_days."""
    vix_spot = _strip_tz(data.get("vix_spot"))
    vix_3m = _strip_tz(data.get("vix_3m"))
    hyg = _strip_tz(data.get("hyg"))
    tlt = _strip_tz(data.get("tlt"))
    spy = _strip_tz(data.get("spy"))
    breadth_prices = _strip_tz(data.get("breadth_prices"))
    
    if vix_spot is None or spy is None or vix_spot.empty or spy.empty:
        return pd.DataFrame()
        
    dates = vix_spot.tail(lookback_days).index
    records = []
    
    if weights is None:
        weights = DEFAULT_WEIGHTS
    total_w = sum(weights.values())
    w = {k: v / total_w for k, v in weights.items()} if total_w > 0 else DEFAULT_WEIGHTS
    
    for i in range(len(dates)):
        curr_date = dates[i]
        
        # Slices up to curr_date
        sub_vix = vix_spot.loc[:curr_date]
        sub_vix3m = vix_3m.loc[:curr_date] if vix_3m is not None else None
        sub_hyg = hyg.loc[:curr_date] if hyg is not None else None
        sub_tlt = tlt.loc[:curr_date] if tlt is not None else None
        sub_spy = spy.loc[:curr_date] if spy is not None else None
        
        if len(sub_vix) < 10:
            continue
            
        s1 = calculate_vix_level_score(sub_vix)["score"]
        s2 = calculate_vix_term_structure_score(sub_vix, sub_vix3m)["score"]
        
        if isinstance(breadth_prices, pd.DataFrame) and not breadth_prices.empty:
            sub_bp = breadth_prices.loc[:curr_date]
            s3 = calculate_breadth_score_from_prices(sub_bp)["score"]
        else:
            s3 = 58.0
            
        s4 = calculate_credit_spreads_score(sub_hyg, sub_tlt)["score"]
        s5 = calculate_put_call_score(sub_vix)["score"]
        s6 = calculate_spy_trend_score(sub_spy)["score"]
        
        blended = (
            s1 * w["vix_level"] +
            s2 * w["vix_term_structure"] +
            s3 * w["breadth"] +
            s4 * w["credit_spreads"] +
            s5 * w["put_call"] +
            s6 * w["spy_trend"]
        )
        
        records.append({
            "Date": curr_date,
            "Deployment_Score": round(blended, 1),
            "VIX_Level": s1,
            "VIX_Term": s2,
            "Breadth": s3,
            "Credit": s4,
            "Sentiment": s5,
            "SPY_Trend": s6
        })
        
    df_hist = pd.DataFrame(records)
    if not df_hist.empty:
        df_hist.set_index("Date", inplace=True)
    return df_hist
