# ⚡ Market Deployment Gating System

A quantitative macro market gating system in Python with a Streamlit dashboard that answers the fundamental investor question: 
> **"Should I be deploying capital right now, and how aggressively?"**

The system pulls **6 macro market signals**, normalizes each signal to a **0–100 scale**, and blends them into a master **Macro Deployment Score** with actionable capital allocation rules.

---

## 🏛️ System Architecture & Signal Modules

The project is structured with modular signal drivers inside the `signals/` directory:

```
micro-deployment-gate/
├── signals/
│   ├── __init__.py
│   ├── vix_level.py             # 1. VIX Level Percentile Rank
│   ├── vix_term_structure.py    # 2. VIX / VIX3M Term Structure Ratio
│   ├── breadth.py               # 3. % S&P 500 Stocks > 200-Day SMA
│   ├── credit_spreads.py        # 4. HYG vs TLT Credit Spread Z-Score
│   ├── put_call.py              # 5. VIX 20-Day ROC (Sentiment Proxy)
│   └── spy_trend.py             # 6. S&P 500 Trend & Golden Cross
├── data_fetcher.py              # Live yfinance data fetching & caching
├── blend_engine.py              # Signal blending engine & risk matrix
├── app.py                       # Streamlit Dashboard UI
├── requirements.txt             # Dependency specification
└── README.md                    # System Documentation
```

---

## 📐 Signal Mathematical Specifications

### 1. VIX Level (`signals/vix_level.py`)
- **Metric**: Percentile rank of current VIX close against trailing 1 year (252 trading days).
- **Formula**:
  $$\text{Base Score} = 100 - \text{Percentile}$$
  - Bonus $+5$ if current $\text{VIX} < 15.0$.
  - Penalty $-10$ if current $\text{VIX} > 30.0$.
  - Clamped to $[0, 100]$.

### 2. VIX Term Structure (`signals/vix_term_structure.py`)
- **Metric**: Ratio of front-month VIX spot (`^VIX`) to VIX 3-Month (`^VIX3M`).
- **Formula**:
  $$\text{Ratio} = \frac{\text{VIX}}{\text{VIX3M}}$$
  - $\text{Ratio} < 1.0 \implies \text{Contango (Calm Market, High Score)}$.
  - $\text{Ratio} \ge 1.0 \implies \text{Backwardation (Vol Stress, Low Score)}$.
  - Mapping: $0.85 \to 100$, $1.15 \to 0$.

### 3. Market Breadth (`signals/breadth.py`)
- **Metric**: Percentage of S&P 500 stocks above their 200-day Simple Moving Average (SMA).
- **Formula**:
  $$\text{Score} = \text{Clamp}\left(\frac{\text{Breadth } \% - 30}{80 - 30} \times 100, 0, 100\right)$$
  - Prevents buying into narrow rallies driven by a few mega-caps while the rest of the market declines.

### 4. Credit Spreads (`signals/credit_spreads.py`)
- **Metric**: High Yield (`HYG`) vs Treasuries (`TLT`) spread ratio z-score over trailing 1-year history.
- **Formula**:
  $$Z = \frac{\text{Ratio}_{\text{current}} - \mu_{1\text{Y}}}{\sigma_{1\text{Y}}}$$
  - Tight Spreads ($Z = -2.0$) $\to 100$.
  - Wide Spreads ($Z = +2.0$) $\to 0$.
  - $\text{Score} = \text{Clamp}(50 - 25 \times Z, 0, 100)$.

### 5. Put/Call Sentiment Proxy (`signals/put_call.py`)
- **Metric**: VIX 20-day Rate of Change (ROC) as a sentiment/panic hedging proxy.
- **Formula**:
  $$\text{ROC}_{20\text{D}} = \frac{\text{VIX}_{\text{current}} - \text{VIX}_{20\text{D ago}}}{\text{VIX}_{20\text{D ago}}} \times 100\%$$
  - Mapping: $\text{ROC } -30\% \to 100$, $\text{ROC } +50\% \to 0$.

### 6. S&P 500 Trend & Momentum (`signals/spy_trend.py`)
- **Metric**: Distance of SPY relative to its 200-day SMA ($+10\% \to 100, -10\% \to 0$) plus Golden Cross status ($50\text{D} > 200\text{D}$).

---

## 🛑 Deployment Gating Threshold Matrix

| Blended Score | Gate Status | Core Answer | Recommended Allocation | Guidance |
| :--- | :--- | :--- | :--- | :--- |
| **80 – 100** | **GREEN GATE** | YES — Deploy Aggressively | 90% – 100% | Full risk-on capital acceleration; buy pullbacks. |
| **60 – 79** | **LIME GATE** | YES — Deploy Moderately | 70% – 85% | Systematic DCA into core equities & market leaders. |
| **40 – 59** | **YELLOW GATE**| Cautious / Selective | 40% – 60% | Hold cash reserves; select high quality only. |
| **20 – 39** | **ORANGE GATE**| Defensive / Slow Down | 20% – 35% | Pause aggressive buying; tighten stop-losses. |
| **0 – 19** | **RED GATE** | NO — Halt Capital Deployment | 0% – 15% | Gate closed; preserve capital & hold cash. |

---

## 🚀 Getting Started

### 1. Installation
Activate environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Launch Dashboard
Run the Streamlit application:
```bash
streamlit run app.py
```
Open browser at `http://localhost:8501`.
