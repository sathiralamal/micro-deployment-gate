import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime

from data_fetcher import fetch_all_macro_data, generate_synthetic_macro_data
from blend_engine import compute_all_signals, blend_deployment_score, calculate_historical_scores

# Required by deployment platforms that look for a top-level application object.
# Keep the Streamlit dashboard working as-is while exposing a conventional app export.
app = st
application = app


def main():
    return st

# Page Configuration
st.set_page_config(
    page_title="Macro Market Deployment Gating System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Dark CSS Custom Styling
st.markdown("""
<style>
    /* Dark Theme Custom Colors */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    .hero-card {
        background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #30363d;
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        margin-bottom: 24px;
    }
    
    .metric-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .metric-container:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }
    
    .signal-card {
        background-color: #161b22;
        border-radius: 10px;
        padding: 18px;
        border: 1px solid #30363d;
        margin-bottom: 16px;
    }
    
    .signal-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #f0f6fc;
        margin-bottom: 6px;
    }
    
    .score-badge {
        font-size: 1.3rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 6px;
        display: inline-block;
    }
    
    .badge-green { background-color: #064e3b; color: #34d399; border: 1px solid #059669; }
    .badge-lime { background-color: #1a4d2e; color: #a3e635; border: 1px solid #65a30d; }
    .badge-yellow { background-color: #713f12; color: #fde047; border: 1px solid #ca8a04; }
    .badge-orange { background-color: #7c2d12; color: #fb923c; border: 1px solid #ea580c; }
    .badge-red { background-color: #7f1d1d; color: #fca5a5; border: 1px solid #dc2626; }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        padding: 8px 16px;
        background-color: #161b22;
        border: 1px solid #30363d;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f6feb !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to assign badge style class
def get_badge_class(score):
    if score >= 80: return "badge-green"
    elif score >= 60: return "badge-lime"
    elif score >= 40: return "badge-yellow"
    elif score >= 20: return "badge-orange"
    else: return "badge-red"

# App Header
st.title("⚡ Macro Market Deployment Gating System")
st.caption("Quantitative Capital Allocation & Risk Management Framework")

# Sidebar Configuration & Controls
with st.sidebar:
    st.header("⚙️ System Controls")
    
    data_mode = st.radio(
        "Data Source Mode:",
        ["Live Yahoo Finance Data", "Simulated Market Stress Scenarios"],
        index=0
    )
    
    st.divider()
    
    st.subheader("🎛️ Signal Weights Customizer")
    st.caption("Adjust macro signal weights (Default: Equal 16.7%)")
    
    w_vix_level = st.slider("VIX Level Weight", 0.0, 5.0, 1.0, 0.1)
    w_vix_term = st.slider("VIX Term Structure Weight", 0.0, 5.0, 1.0, 0.1)
    w_breadth = st.slider("Market Breadth Weight", 0.0, 5.0, 1.0, 0.1)
    w_credit = st.slider("Credit Spreads Weight", 0.0, 5.0, 1.0, 0.1)
    w_sentiment = st.slider("Put/Call Sentiment Weight", 0.0, 5.0, 1.0, 0.1)
    w_trend = st.slider("SPY Trend & Momentum Weight", 0.0, 5.0, 1.0, 0.1)
    
    custom_weights = {
        "vix_level": w_vix_level,
        "vix_term_structure": w_vix_term,
        "breadth": w_breadth,
        "credit_spreads": w_credit,
        "put_call": w_sentiment,
        "spy_trend": w_trend
    }
    
    st.divider()
    
    if st.button("🔄 Refresh Market Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Data Retrieval
with st.spinner("Fetching macro signals & financial time series..."):
    if data_mode == "Live Yahoo Finance Data":
        macro_data = fetch_all_macro_data()
    else:
        macro_data = generate_synthetic_macro_data()

# Compute Signal Scores & Blend
signals = compute_all_signals(macro_data)
result = blend_deployment_score(signals, custom_weights)

final_score = result["final_score"]
gating_status = result["gating_status"]
answer_summary = result["answer_summary"]
recommended_capital_pct = result["recommended_capital_pct"]
action_plan = result["action_plan"]
badge_color = result["badge_color"]
breakdown_df = result["breakdown"]

# Top Banner: Direct Answer to User's Core Question
st.markdown(f"""
<div class="hero-card">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <span style="font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px; color: #8b949e; font-weight: 600;">
                CORE DEPLOYMENT DECISION
            </span>
            <h2 style="margin: 4px 0 12px 0; color: #f0f6fc; font-size: 1.9rem;">
                {answer_summary}
            </h2>
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <span class="score-badge {get_badge_class(final_score)}">
                    {gating_status}
                </span>
                <span style="font-size: 1.1rem; color: #c9d1d9; font-weight: 500;">
                    Target Capital Allocation: <strong style="color: {badge_color};">{recommended_capital_pct}</strong>
                </span>
            </div>
        </div>
        <div style="text-align: right; background: #0d1117; padding: 16px 28px; border-radius: 10px; border: 1px solid #30363d;">
            <div style="font-size: 0.85rem; color: #8b949e; font-weight: 600;">BLENDED DEPLOYMENT SCORE</div>
            <div style="font-size: 3.2rem; font-weight: 800; color: {badge_color}; line-height: 1.1;">
                {final_score:.1f}<span style="font-size: 1.5rem; color: #8b949e;">/100</span>
            </div>
            <div style="font-size: 0.8rem; color: #8b949e;">Updated: {macro_data.get('last_updated', 'N/A')}</div>
        </div>
    </div>
    <hr style="border-color: #30363d; margin: 16px 0;">
    <p style="margin: 0; font-size: 1.05rem; line-height: 1.5; color: #c9d1d9;">
        <strong>Strategic Guidance:</strong> {action_plan}
    </p>
</div>
""", unsafe_allow_html=True)

# Metric Summary Cards Row
cols = st.columns(6)

vix_raw = signals["vix_level"]["current_vix"]
vix_score = signals["vix_level"]["score"]

term_ratio = signals["vix_term_structure"]["ratio"]
term_score = signals["vix_term_structure"]["score"]

breadth_pct = signals["breadth"]["breadth_pct"]
breadth_score = signals["breadth"]["score"]

credit_z = signals["credit_spreads"]["z_score"]
credit_score = signals["credit_spreads"]["score"]

roc_20d = signals["put_call"]["roc_20d"]
sentiment_score = signals["put_call"]["score"]

spy_dist = signals["spy_trend"]["dist_200d_pct"]
trend_score = signals["spy_trend"]["score"]

with cols[0]:
    st.markdown(f"""
    <div class="metric-container">
        <div style="font-size: 0.8rem; color: #8b949e; font-weight: 600;">1. VIX LEVEL</div>
        <div style="font-size: 1.6rem; font-weight: 700; color: #f0f6fc;">{vix_raw:.2f}</div>
        <div style="font-size: 0.85rem; color: {badge_color};">Score: <strong>{vix_score}</strong>/100</div>
    </div>
    """, unsafe_allow_html=True)

with cols[1]:
    st.markdown(f"""
    <div class="metric-container">
        <div style="font-size: 0.8rem; color: #8b949e; font-weight: 600;">2. VIX TERM STRUCT</div>
        <div style="font-size: 1.6rem; font-weight: 700; color: #f0f6fc;">{term_ratio:.3f}</div>
        <div style="font-size: 0.85rem; color: {badge_color};">Score: <strong>{term_score}</strong>/100</div>
    </div>
    """, unsafe_allow_html=True)

with cols[2]:
    st.markdown(f"""
    <div class="metric-container">
        <div style="font-size: 0.8rem; color: #8b949e; font-weight: 600;">3. MARKET BREADTH</div>
        <div style="font-size: 1.6rem; font-weight: 700; color: #f0f6fc;">{breadth_pct:.1f}%</div>
        <div style="font-size: 0.85rem; color: {badge_color};">Score: <strong>{breadth_score}</strong>/100</div>
    </div>
    """, unsafe_allow_html=True)

with cols[3]:
    st.markdown(f"""
    <div class="metric-container">
        <div style="font-size: 0.8rem; color: #8b949e; font-weight: 600;">4. CREDIT SPREADS</div>
        <div style="font-size: 1.6rem; font-weight: 700; color: #f0f6fc;">{credit_z:+.2f} Z</div>
        <div style="font-size: 0.85rem; color: {badge_color};">Score: <strong>{credit_score}</strong>/100</div>
    </div>
    """, unsafe_allow_html=True)

with cols[4]:
    st.markdown(f"""
    <div class="metric-container">
        <div style="font-size: 0.8rem; color: #8b949e; font-weight: 600;">5. PUT/CALL (VIX ROC)</div>
        <div style="font-size: 1.6rem; font-weight: 700; color: #f0f6fc;">{roc_20d:+.1f}%</div>
        <div style="font-size: 0.85rem; color: {badge_color};">Score: <strong>{sentiment_score}</strong>/100</div>
    </div>
    """, unsafe_allow_html=True)

with cols[5]:
    st.markdown(f"""
    <div class="metric-container">
        <div style="font-size: 0.8rem; color: #8b949e; font-weight: 600;">6. SPY TREND (200D)</div>
        <div style="font-size: 1.6rem; font-weight: 700; color: #f0f6fc;">{spy_dist:+.1f}%</div>
        <div style="font-size: 0.85rem; color: {badge_color};">Score: <strong>{trend_score}</strong>/100</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

from data_fetcher import fetch_all_macro_data, generate_synthetic_macro_data, fetch_symbol_scan_data

# Main Content Tabs
tab1, tab_symbol, tab2, tab3, tab4 = st.tabs([
    "📊 Signal Dashboard & Radar",
    "🔎 Single Symbol Scanner",
    "📈 Trailing Score Trends",
    "🎛️ Scenario Stress Simulator",
    "📘 Signal Specs & Math Formulas"
])

# TAB 1: Dashboard & Radar
with tab1:
    col_gauge, col_radar = st.columns([1, 1])
    
    with col_gauge:
        st.subheader("🎯 Deployment Score Gauge")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=final_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Master Deployment Score", 'font': {'size': 20, 'color': '#f0f6fc'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#8b949e"},
                'bar': {'color': badge_color},
                'bgcolor': "#161b22",
                'borderwidth': 2,
                'bordercolor': "#30363d",
                'steps': [
                    {'range': [0, 20], 'color': '#7f1d1d'},
                    {'range': [20, 40], 'color': '#7c2d12'},
                    {'range': [40, 60], 'color': '#713f12'},
                    {'range': [60, 80], 'color': '#1a4d2e'},
                    {'range': [80, 100], 'color': '#064e3b'}
                ],
                'threshold': {
                    'line': {'color': "#ffffff", 'width': 4},
                    'thickness': 0.75,
                    'value': final_score
                }
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor="#0d1117",
            plot_bgcolor="#0d1117",
            font={'color': "#c9d1d9"},
            height=340,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        
    with col_radar:
        st.subheader("🕸️ Macro Signals Radar Profile")
        categories = breakdown_df["signal_name"].tolist()
        scores = breakdown_df["score"].tolist()
        categories.append(categories[0])
        scores.append(scores[0])
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=scores,
            theta=categories,
            fill='toself',
            name='Current Macro State',
            line_color=badge_color,
            fillcolor=f"rgba(16, 185, 129, 0.25)" if final_score >= 60 else "rgba(239, 68, 68, 0.25)"
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color="#8b949e", gridcolor="#30363d"),
                angularaxis=dict(color="#f0f6fc", gridcolor="#30363d"),
                bgcolor="#161b22"
            ),
            paper_bgcolor="#0d1117",
            font=dict(color="#c9d1d9"),
            height=340,
            margin=dict(l=40, r=40, t=30, b=30),
            showlegend=False
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
    st.subheader("📋 Detailed Signal Decomposition & Weighting")
    
    # Styled breakdown table
    st.dataframe(
        breakdown_df[["signal_name", "category", "score", "weight", "contribution", "regime", "explanation"]],
        column_config={
            "signal_name": "Signal Name",
            "category": "Category",
            "score": st.column_config.ProgressColumn("Score (0-100)", format="%.1f", min_value=0, max_value=100),
            "weight": st.column_config.NumberColumn("Weight (%)", format="%.1f%%"),
            "contribution": st.column_config.NumberColumn("Contrib to Score", format="%.1f pts"),
            "regime": "Market Regime",
            "explanation": "Signal Findings & Commentary"
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🔍 Breakdown of All 6 Macro Signals")
    
    sig_cols = st.columns(2)
    
    with sig_cols[0]:
        # Signal 1 Card
        v1 = signals["vix_level"]
        st.markdown(f"""
        <div class="signal-card">
            <div class="signal-title">1. VIX Level (signals/vix_level.py)</div>
            <div style="font-size: 0.9rem; color: #8b949e; margin-bottom: 8px;">Percentile-rank current VIX against trailing 1Y. Low VIX = high score.</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #f0f6fc;">
                Current VIX: {v1['current_vix']} ({v1['percentile']}th percentile)
            </div>
            <div style="color: {badge_color}; font-weight: 600; margin-top: 4px;">Score: {v1['score']} / 100</div>
            <div style="font-size: 0.85rem; color: #8b949e; margin-top: 6px;">{v1['explanation']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Signal 3 Card
        v3 = signals["breadth"]
        st.markdown(f"""
        <div class="signal-card">
            <div class="signal-title">3. Market Breadth (signals/breadth.py)</div>
            <div style="font-size: 0.9rem; color: #8b949e; margin-bottom: 8px;">% of S&P 500 stocks above 200-day SMA. Catches narrow rallies.</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #f0f6fc;">
                Breadth: {v3['breadth_pct']}% ({v3['stocks_above_200d']}/{v3['total_stocks_analyzed']} stocks > 200D SMA)
            </div>
            <div style="color: {badge_color}; font-weight: 600; margin-top: 4px;">Score: {v3['score']} / 100</div>
            <div style="font-size: 0.85rem; color: #8b949e; margin-top: 6px;">{v3['explanation']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Signal 5 Card
        v5 = signals["put_call"]
        st.markdown(f"""
        <div class="signal-card">
            <div class="signal-title">5. Put/Call Sentiment (signals/put_call.py)</div>
            <div style="font-size: 0.9rem; color: #8b949e; margin-bottom: 8px;">VIX 20-day rate of change as sentiment proxy. Rapidly rising VIX = panic.</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #f0f6fc;">
                20D ROC: {v5['roc_20d']:+.1f}% (VIX: {v5['current_vix']} vs {v5['vix_20d_ago']} 20D ago)
            </div>
            <div style="color: {badge_color}; font-weight: 600; margin-top: 4px;">Score: {v5['score']} / 100</div>
            <div style="font-size: 0.85rem; color: #8b949e; margin-top: 6px;">{v5['explanation']}</div>
        </div>
        """, unsafe_allow_html=True)

    with sig_cols[1]:
        # Signal 2 Card
        v2 = signals["vix_term_structure"]
        st.markdown(f"""
        <div class="signal-card">
            <div class="signal-title">2. VIX Term Structure (signals/vix_term_structure.py)</div>
            <div style="font-size: 0.9rem; color: #8b949e; margin-bottom: 8px;">Ratio = front VIX / VIX3M. Contango (&lt;1.0) = calm. Backwardation (&gt;1.0) = stress.</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #f0f6fc;">
                VIX / VIX3M Ratio: {v2['ratio']:.3f} (Spot: {v2['vix_spot']}, 3M: {v2['vix_3m']})
            </div>
            <div style="color: {badge_color}; font-weight: 600; margin-top: 4px;">Score: {v2['score']} / 100</div>
            <div style="font-size: 0.85rem; color: #8b949e; margin-top: 6px;">{v2['explanation']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Signal 4 Card
        v4 = signals["credit_spreads"]
        st.markdown(f"""
        <div class="signal-card">
            <div class="signal-title">4. Credit Spreads (signals/credit_spreads.py)</div>
            <div style="font-size: 0.9rem; color: #8b949e; margin-bottom: 8px;">HYG vs TLT spread proxy z-score against 1Y history. Tight = 100, Wide = 0.</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #f0f6fc;">
                Credit Spread Z-Score: {v4['z_score']:+.2f} (TLT/HYG: {v4['current_ratio']:.3f})
            </div>
            <div style="color: {badge_color}; font-weight: 600; margin-top: 4px;">Score: {v4['score']} / 100</div>
            <div style="font-size: 0.85rem; color: #8b949e; margin-top: 6px;">{v4['explanation']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Signal 6 Card
        v6 = signals["spy_trend"]
        st.markdown(f"""
        <div class="signal-card">
            <div class="signal-title">6. S&P 500 Trend & Momentum (signals/spy_trend.py)</div>
            <div style="font-size: 0.9rem; color: #8b949e; margin-bottom: 8px;">SPY relative to 200-day SMA (+10% -> 100, -10% -> 0) + Golden Cross status.</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #f0f6fc;">
                SPY: ${v6['spy_price']} ({v6['dist_200d_pct']:+.1f}% vs 200D SMA ${v6['sma_200']})
            </div>
            <div style="color: {badge_color}; font-weight: 600; margin-top: 4px;">Score: {v6['score']} / 100</div>
            <div style="font-size: 0.85rem; color: #8b949e; margin-top: 6px;">{v6['explanation']}</div>
        </div>
        """, unsafe_allow_html=True)

# TAB: Single Symbol Scanner
with tab_symbol:
    st.subheader("🔎 Single Symbol / Asset Deployment Scanner")
    st.caption("Scan any specific stock, ETF, or asset symbol against the macro deployment gate and technical alignment.")
    
    col_input, col_presets = st.columns([1.5, 2])
    with col_input:
        target_symbol = st.text_input("Enter Ticker Symbol (e.g. AAPL, NVDA, QQQ, TSLA, BTC-USD):", value="AAPL").strip().upper()
    with col_presets:
        st.markdown("<div style='font-size:0.85rem; color:#8b949e; margin-bottom:4px;'>Quick Ticker Presets:</div>", unsafe_allow_html=True)
        preset_cols = st.columns(6)
        presets = ["AAPL", "NVDA", "QQQ", "TSLA", "MSFT", "BTC-USD"]
        for idx, p in enumerate(presets):
            if preset_cols[idx].button(p, use_container_width=True):
                target_symbol = p

    sym_data = fetch_symbol_scan_data(target_symbol, spy_series=macro_data.get("spy"))
    
    if "error" in sym_data:
        st.error(sym_data["error"])
    else:
        # Determine Gating Decision for this specific symbol
        s_price = sym_data["curr_price"]
        s_sma200 = sym_data["sma_200"]
        s_sma50 = sym_data["sma_50"]
        dist_200 = sym_data["dist_200d_pct"]
        dist_50 = sym_data["dist_50d_pct"]
        
        # Symbol Decision Matrix
        if final_score >= 60.0 and dist_200 >= 0.0:
            sym_status = "CLEAR TO DEPLOY / BUY"
            sym_badge = "badge-green"
            sym_guidance = f"Macro Gate is OPEN ({final_score:.1f}/100) and {target_symbol} is in a healthy uptrend ({dist_200:+.1f}% above 200D SMA ${s_sma200}). Position size: 100% of standard tranche."
        elif final_score >= 60.0 and dist_200 < 0.0:
            sym_status = "MACRO CLEAR — SYMBOL IN PULLBACK"
            sym_badge = "badge-yellow"
            sym_guidance = f"Macro Gate is OPEN ({final_score:.1f}/100), but {target_symbol} is trading {dist_200:+.1f}% below its 200D SMA (${s_sma200}). Opportunistic DCA entry only or wait for 50D SMA reclamation."
        elif final_score >= 40.0:
            sym_status = "CAUTIOUS / HALF TRANCHE"
            sym_badge = "badge-orange"
            sym_guidance = f"Macro Gate is Neutral/Cautious ({final_score:.1f}/100). Deploy max 50% tranche size into {target_symbol} with tight stops."
        else:
            sym_status = "GATE CLOSED FOR THIS SYMBOL"
            sym_badge = "badge-red"
            sym_guidance = f"Macro Gate is DEFENSIVE/CLOSED ({final_score:.1f}/100). Do not deploy fresh capital into {target_symbol} until macro volatility stabilizes."

        st.markdown(f"""
        <div style="background: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin: 16px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span style="font-size: 0.85rem; color: #8b949e; font-weight: 600;">SYMBOL SCAN RESULT FOR {target_symbol}</span>
                    <h3 style="margin: 4px 0; color: #f0f6fc;">${s_price} <span style="font-size: 1rem; color: {'#34d399' if sym_data['day_change_pct'] >= 0 else '#fca5a5'};">({sym_data['day_change_pct']:+.2f}%)</span></h3>
                    <div style="margin-top: 8px;">
                        <span class="score-badge {sym_badge}">{sym_status}</span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.85rem; color: #8b949e;">200-Day SMA: <strong>${s_sma200}</strong> ({dist_200:+.1f}%)</div>
                    <div style="font-size: 0.85rem; color: #8b949e;">50-Day SMA: <strong>${s_sma50}</strong> ({dist_50:+.1f}%)</div>
                    <div style="font-size: 0.85rem; color: #8b949e;">Beta vs SPY: <strong>{sym_data['beta']}</strong> | Vol 20D: <strong>{sym_data['vol_20d_ann']}%</strong></div>
                </div>
            </div>
            <hr style="border-color: #30363d; margin: 12px 0;">
            <p style="margin: 0; color: #c9d1d9; font-size: 0.95rem;">
                <strong>Symbol Deployment Rules:</strong> {sym_guidance}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Price & Moving Average Chart for Symbol
        fig_sym = go.Figure()
        fig_sym.add_trace(go.Scatter(x=sym_data["prices"].index, y=sym_data["prices"].values, mode='lines', name=f'{target_symbol} Price', line=dict(color='#58a6ff', width=2.5)))
        
        sma50_series = sym_data["prices"].rolling(50).mean()
        sma200_series = sym_data["prices"].rolling(200).mean()
        
        fig_sym.add_trace(go.Scatter(x=sma50_series.index, y=sma50_series.values, mode='lines', name='50-Day SMA', line=dict(color='#f59e0b', width=1.5, dash='dash')))
        fig_sym.add_trace(go.Scatter(x=sma200_series.index, y=sma200_series.values, mode='lines', name='200-Day SMA', line=dict(color='#ef4444', width=2)))
        
        fig_sym.update_layout(
            title=f"{target_symbol} Price Action & Moving Averages (1Y)",
            paper_bgcolor="#0d1117",
            plot_bgcolor="#161b22",
            font=dict(color="#c9d1d9"),
            height=400,
            xaxis=dict(gridcolor="#30363d"),
            yaxis=dict(gridcolor="#30363d"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_sym, use_container_width=True)

# TAB 2: Trailing Score Trends
with tab2:
    st.subheader("📈 Trailing 90-Day Deployment Score History")
    st.caption("Track how the market deployment gating decision evolved over time alongside S&P 500 price action.")
    
    df_hist = calculate_historical_scores(macro_data, custom_weights, lookback_days=90)
    
    if not df_hist.empty and "spy" in macro_data and not macro_data["spy"].empty:
        spy_sub = macro_data["spy"].loc[df_hist.index] if df_hist.index.isin(macro_data["spy"].index).all() else macro_data["spy"].tail(len(df_hist))
        
        fig_trend = go.Figure()
        
        # Blended Score Line
        fig_trend.add_trace(go.Scatter(
            x=df_hist.index,
            y=df_hist["Deployment_Score"],
            mode='lines',
            name='Deployment Score (0-100)',
            line=dict(color='#10b981', width=3),
            yaxis='y'
        ))
        
        # Threshold Bands
        fig_trend.add_hrect(y0=80, y1=100, fillcolor="#064e3b", opacity=0.15, line_width=0, annotation_text="Green Gate (Aggressive)")
        fig_trend.add_hrect(y0=60, y1=80, fillcolor="#1a4d2e", opacity=0.15, line_width=0, annotation_text="Lime Gate (Moderate)")
        fig_trend.add_hrect(y0=40, y1=60, fillcolor="#713f12", opacity=0.15, line_width=0, annotation_text="Yellow Gate (Cautious)")
        fig_trend.add_hrect(y0=20, y1=40, fillcolor="#7c2d12", opacity=0.15, line_width=0, annotation_text="Orange Gate (Defensive)")
        fig_trend.add_hrect(y0=0, y1=20, fillcolor="#7f1d1d", opacity=0.15, line_width=0, annotation_text="Red Gate (Halt)")
        
        # SPY Price Line on secondary axis
        if len(spy_sub) == len(df_hist):
            fig_trend.add_trace(go.Scatter(
                x=df_hist.index,
                y=spy_sub.values,
                mode='lines',
                name='S&P 500 (SPY)',
                line=dict(color='#58a6ff', width=2, dash='dot'),
                yaxis='y2'
            ))
            
        fig_trend.update_layout(
            paper_bgcolor="#0d1117",
            plot_bgcolor="#161b22",
            font=dict(color="#c9d1d9"),
            height=450,
            xaxis=dict(title="Date", gridcolor="#30363d"),
            yaxis=dict(title="Deployment Score", range=[0, 105], gridcolor="#30363d"),
            yaxis2=dict(title="SPY Index Price ($)", overlaying='y', side='right', showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        st.subheader("📊 Individual Signal Sub-Component Trailing History")
        fig_subs = px.line(
            df_hist[["VIX_Level", "VIX_Term", "Breadth", "Credit", "Sentiment", "SPY_Trend"]],
            title="Individual Signal Scores (0-100)",
            labels={"value": "Score", "variable": "Macro Signal"}
        )
        fig_subs.update_layout(
            paper_bgcolor="#0d1117",
            plot_bgcolor="#161b22",
            font=dict(color="#c9d1d9"),
            height=380,
            xaxis=dict(gridcolor="#30363d"),
            yaxis=dict(range=[0, 105], gridcolor="#30363d")
        )
        st.plotly_chart(fig_subs, use_container_width=True)
    else:
        st.info("Insufficient historical time series data to render 90-day trend chart.")

# TAB 3: Scenario Stress Simulator
with tab3:
    st.subheader("🎛️ Interactive Macro Shock Simulator")
    st.caption("Stress test the gating system by injecting hypothetical macro shocks (e.g. VIX spike, credit spread freeze, market breadth crash).")
    
    sim_col1, sim_col2 = st.columns(2)
    
    with sim_col1:
        sim_vix = st.slider("Simulated VIX Level:", 10.0, 60.0, float(vix_raw), 0.5)
        sim_vix_ratio = st.slider("Simulated VIX / VIX3M Ratio:", 0.70, 1.40, float(term_ratio), 0.01)
        sim_breadth = st.slider("Simulated Market Breadth (% > 200D):", 10.0, 95.0, float(breadth_pct), 1.0)

    with sim_col2:
        sim_credit_z = st.slider("Simulated Credit Spread Z-Score:", -3.0, +3.5, float(credit_z), 0.1)
        sim_roc = st.slider("Simulated VIX 20D Rate of Change (%):", -50.0, +100.0, float(roc_20d), 5.0)
        sim_spy_dist = st.slider("Simulated SPY Distance to 200D SMA (%):", -25.0, +25.0, float(spy_dist), 1.0)
        
    # Recalculate scores under simulated inputs
    from signals.vix_level import calculate_vix_level_score
    from signals.vix_term_structure import calculate_vix_term_structure_score
    from signals.breadth import calculate_breadth_score_from_pct
    from signals.credit_spreads import calculate_credit_spreads_score
    from signals.put_call import calculate_put_call_score
    from signals.spy_trend import calculate_spy_trend_score

    # Mock series for simulators
    sim_vix_series = pd.Series([20.0]*200 + [sim_vix])
    sim_vix3m_series = pd.Series([20.0]*200 + [sim_vix / sim_vix_ratio if sim_vix_ratio > 0 else 20.0])
    
    sim_s1 = calculate_vix_level_score(sim_vix_series)
    sim_s2 = calculate_vix_term_structure_score(sim_vix_series, sim_vix3m_series)
    sim_s3 = calculate_breadth_score_from_pct(sim_breadth)
    
    # Sim credit
    sim_s4 = {
        "score": float(np.clip(50.0 - 25.0 * sim_credit_z, 0.0, 100.0)),
        "z_score": sim_credit_z,
        "regime": "Simulated Credit State"
    }
    
    # Sim sentiment
    sim_s5_raw = 100.0 - ((sim_roc - (-30.0)) / (50.0 - (-30.0))) * 100.0
    sim_s5 = {
        "score": float(np.clip(sim_s5_raw, 0.0, 100.0)),
        "roc_20d": sim_roc,
        "regime": "Simulated Sentiment State"
    }
    
    # Sim trend
    sim_s6_raw = ((sim_spy_dist - (-10.0)) / (10.0 - (-10.0))) * 100.0
    sim_s6 = {
        "score": float(np.clip(sim_s6_raw, 0.0, 100.0)),
        "dist_200d_pct": sim_spy_dist,
        "regime": "Simulated SPY Trend State"
    }
    
    sim_signals = {
        "vix_level": sim_s1,
        "vix_term_structure": sim_s2,
        "breadth": sim_s3,
        "credit_spreads": sim_s4,
        "put_call": sim_s5,
        "spy_trend": sim_s6
    }
    
    sim_result = blend_deployment_score(sim_signals, custom_weights)
    
    st.divider()
    st.subheader("⚡ Simulated Stress Test Outcome")
    
    sim_col_res1, sim_col_res2 = st.columns([1, 2])
    with sim_col_res1:
        st.markdown(f"""
        <div style="background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; text-align: center;">
            <div style="font-size: 0.9rem; color: #8b949e; font-weight: 600;">SIMULATED DEPLOYMENT SCORE</div>
            <div style="font-size: 3.5rem; font-weight: 800; color: {sim_result['badge_color']}; margin: 8px 0;">
                {sim_result['final_score']:.1f}
            </div>
            <div class="score-badge {get_badge_class(sim_result['final_score'])}">
                {sim_result['gating_status']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with sim_col_res2:
        st.markdown(f"""
        <div style="background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d;">
            <h4 style="margin: 0 0 8px 0; color: #f0f6fc;">{sim_result['answer_summary']}</h4>
            <p style="color: #c9d1d9; font-size: 1rem; margin-bottom: 12px;">
                <strong>Recommended Allocation:</strong> {sim_result['recommended_capital_pct']}
            </p>
            <p style="color: #8b949e; font-size: 0.95rem; margin: 0;">
                {sim_result['action_plan']}
            </p>
        </div>
        """, unsafe_allow_html=True)

# TAB 4: Methodological Formulas & Specs
with tab4:
    st.subheader("📘 System Architecture & Quantitative Formulas")
    
    st.markdown("""
    ### 1. VIX Level (`signals/vix_level.py`)
    - **Logic**: Evaluates absolute market volatility relative to 1-year trailing history (252 trading days).
    - **Formula**:
      $$\\text{Percentile} = \\frac{\\text{Days with } \\text{VIX} \\le \\text{VIX}_{\\text{current}}}{252} \\times 100$$
      $$\\text{Base Score} = 100 - \\text{Percentile}$$
      $$\\text{Bonus} = +5 \\text{ if VIX} < 15, \\quad \\text{Penalty} = -10 \\text{ if VIX} > 30$$
      $$\\text{Score} = \\text{Clamp}(\\text{Base Score} + \\text{Bonus} + \\text{Penalty}, 0, 100)$$

    ### 2. VIX Term Structure (`signals/vix_term_structure.py`)
    - **Logic**: Detects curve shape of volatility index futures/spot.
    - **Formula**:
      $$\\text{Ratio} = \\frac{\\text{Front VIX Spot (}^\\text{VIX)}}{\\text{VIX 3-Month (}^\\text{VIX3M)}}$$
      $$\\text{Contango (Ratio} < 1.0) \\implies \\text{Calm}, \\quad \\text{Backwardation (Ratio} \\ge 1.0) \\implies \\text{Stress}$$
      $$\\text{Linear Mapping}: \\quad 0.85 \\to 100, \\quad 1.15 \\to 0$$
      $$\\text{Score} = \\text{Clamp}\\left(100 - \\frac{\\text{Ratio} - 0.85}{1.15 - 0.85} \\times 100, 0, 100\\right)$$

    ### 3. Market Breadth (`signals/breadth.py`)
    - **Logic**: Measures participation breadth across S&P 500 stocks to identify narrow mega-cap-only rallies.
    - **Formula**:
      $$\\text{Breadth \\%} = \\frac{\\text{Number of S\\&P 500 stocks } > \\text{200-Day SMA}}{\\text{Total Stocks Analyzed}} \\times 100$$
      $$\\text{Linear Mapping}: \\quad 80\\% \\to 100, \\quad 30\\% \\to 0$$
      $$\\text{Score} = \\text{Clamp}\\left(\\frac{\\text{Breadth \\%} - 30}{80 - 30} \\times 100, 0, 100\\right)$$

    ### 4. Credit Spreads (`signals/credit_spreads.py`)
    - **Logic**: Assesses high-yield corporate credit risk appetite relative to safe-haven 20Y Treasuries via HYG/TLT proxy ratio.
    - **Formula**:
      $$\\text{Spread Ratio} = \\frac{\\text{TLT Price}}{\\text{HYG Price}}$$
      $$Z = \\frac{\\text{Spread Ratio}_{\\text{current}} - \\mu_{1\\text{Y}}}{\\sigma_{1\\text{Y}}}$$
      $$\\text{Tight Spreads } (Z = -2.0) \\to 100, \\quad \\text{Wide Spreads } (Z = +2.0) \\to 0$$
      $$\\text{Score} = \\text{Clamp}(50 - 25 \\times Z, 0, 100)$$

    ### 5. Put/Call Sentiment Proxy (`signals/put_call.py`)
    - **Logic**: Monitors 20-day rate of change (ROC) of VIX as sentiment and panic hedging proxy.
    - **Formula**:
      $$\\text{ROC}_{20\\text{D}} = \\frac{\\text{VIX}_{\\text{current}} - \\text{VIX}_{20\\text{D ago}}}{\\text{VIX}_{20\\text{D ago}}} \\times 100\\%$$
      $$\\text{Mapping}: \\quad \\text{ROC } -30\\% \\to 100, \\quad \\text{ROC } +50\\% \\to 0$$
      $$\\text{Score} = \\text{Clamp}\\left(100 - \\frac{\\text{ROC}_{20\\text{D}} - (-30)}{50 - (-30)} \\times 100, 0, 100\\right)$$

    ### 6. S&P 500 Trend & Momentum (`signals/spy_trend.py`)
    - **Logic**: Evaluates equity index price location relative to structural moving averages.
    - **Formula**:
      $$\\text{Distance}_{200\\text{D}} = \\frac{\\text{SPY} - \\text{SMA}_{200\\text{D}}}{\\text{SMA}_{200\\text{D}}} \\times 100\\%$$
      $$\\text{Mapping}: \\quad +10\\% \\to 100, \\quad -10\\% \\to 0$$
      $$\\text{Bonus} = +5 \\text{ if } \\text{SMA}_{50\\text{D}} > \\text{SMA}_{200\\text{D}} \\text{ (Golden Cross)}$$
    """)

# Footer
st.markdown("<br><hr style='border-color: #30363d;'>", unsafe_allow_html=True)
st.caption("Market Deployment Gating System • Powered by Python, Streamlit, yfinance & Plotly")
