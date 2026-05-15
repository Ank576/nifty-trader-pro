import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Research", page_icon="🔎", layout="wide")

st.title("🔎 Benjamin Graham Research")
st.caption("Search a stock, estimate intrinsic value, and build an entry strategy with time horizon.")


def format_num(value, prefix="", suffix=""):
    if value is None or (isinstance(value, float) and (np.isnan(value) or np.isinf(value))):
        return "—"
    return f"{prefix}{value:,.2f}{suffix}"


def safe_get(d, key, default=None):
    try:
        return d.get(key, default)
    except Exception:
        return default


@st.cache_data(ttl=900)
def fetch_stock_data(symbol: str):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    price_hist = ticker.history(period="1y", interval="1d")
    financials = ticker.financials
    balance_sheet = ticker.balance_sheet
    return info, price_hist, financials, balance_sheet


def derive_metrics(info, financials, price_hist):
    current_price = safe_get(info, "currentPrice") or safe_get(info, "regularMarketPrice")
    eps = safe_get(info, "trailingEps")
    book_value = safe_get(info, "bookValue")
    pe = safe_get(info, "trailingPE")
    pb = safe_get(info, "priceToBook")
    roe = safe_get(info, "returnOnEquity")
    market_cap = safe_get(info, "marketCap")
    debt_to_equity = safe_get(info, "debtToEquity")
    sector = safe_get(info, "sector")
    long_name = safe_get(info, "longName") or safe_get(info, "shortName")

    growth = None
    if financials is not None and not financials.empty:
        try:
            if "Net Income" in financials.index:
                s = financials.loc["Net Income"].dropna()
                s = s.sort_index()
                if len(s) >= 2 and s.iloc[0] > 0 and s.iloc[-1] > 0:
                    growth = ((s.iloc[-1] / s.iloc[0]) ** (1 / (len(s) - 1)) - 1) * 100
        except Exception:
            growth = None

    if growth is None:
        growth = safe_get(info, "earningsGrowth")
        if growth is not None:
            growth = growth * 100

    last_close = None
    support_50dma = None
    support_200dma = None
    if price_hist is not None and not price_hist.empty:
        last_close = float(price_hist["Close"].iloc[-1])
        price_hist = price_hist.copy()
        price_hist["MA50"] = price_hist["Close"].rolling(50).mean()
        price_hist["MA200"] = price_hist["Close"].rolling(200).mean()
        if not pd.isna(price_hist["MA50"].iloc[-1]):
            support_50dma = float(price_hist["MA50"].iloc[-1])
        if not pd.isna(price_hist["MA200"].iloc[-1]):
            support_200dma = float(price_hist["MA200"].iloc[-1])

    return {
        "name": long_name,
        "sector": sector,
        "current_price": current_price or last_close,
        "eps": eps,
        "book_value": book_value,
        "pe": pe,
        "pb": pb,
        "roe": roe * 100 if roe is not None and abs(roe) < 1 else roe,
        "market_cap": market_cap,
        "debt_to_equity": debt_to_equity,
        "growth": growth,
        "support_50dma": support_50dma,
        "support_200dma": support_200dma,
    }


def graham_number(eps, bvps):
    if eps is None or bvps is None or eps <= 0 or bvps <= 0:
        return None
    return math.sqrt(22.5 * eps * bvps)


def eps_fair_value(eps, growth_pct, required_return_pct):
    if eps is None or eps <= 0:
        return None
    growth_pct = max(growth_pct or 0, 0)
    rr = required_return_pct / 100
    if rr <= 0:
        return None
    next_eps = eps * (1 + growth_pct / 100)
    return next_eps * (8.5 + 2 * growth_pct) / (rr * 100)


def valuation_bands(fair_value):
    if fair_value is None:
        return {}
    return {
        "Fair Value": fair_value,
        "MOS 15%": fair_value * 0.85,
        "MOS 25%": fair_value * 0.75,
        "MOS 40%": fair_value * 0.60,
    }


def investment_view(current_price, fair_value, mos25, mos40):
    if current_price is None or fair_value is None:
        return ("Insufficient data", "Could not determine a reliable intrinsic value.")
    if current_price <= mos40:
        return ("Deep Value Buy", "Price is below the 40% margin-of-safety band. Suitable for staggered accumulation.")
    if current_price <= mos25:
        return ("Accumulate", "Price is below the 25% margin-of-safety band. Attractive for long-term value investing.")
    if current_price <= fair_value:
        return ("Watch / SIP Entry", "Price is below fair value but not deeply discounted. Use staggered entries.")
    return ("Wait", "Price is above estimated fair value. Add only on correction or earnings improvement.")


def build_strategy(current_price, fair_value, support_50dma, support_200dma):
    if current_price is None or fair_value is None:
        return None
    ideal_low = min(fair_value * 0.60, support_200dma if support_200dma else fair_value * 0.60)
    ideal_high = min(fair_value * 0.75, support_50dma if support_50dma else fair_value * 0.75)
    buy_below = fair_value * 0.90
    stagger_1 = min(current_price, ideal_high)
    stagger_2 = fair_value * 0.75
    stagger_3 = fair_value * 0.60

    if current_price < fair_value * 0.75:
        horizon = "3-5 years"
        review_window = "Accumulate over 2-6 weeks"
    elif current_price < fair_value:
        horizon = "2-4 years"
        review_window = "Accumulate over 4-8 weeks"
    else:
        horizon = "Wait for better valuation comfort before long-term entry"
        review_window = "Review weekly for 1-8 weeks"

    return {
        "ideal_low": ideal_low,
        "ideal_high": ideal_high,
        "buy_below": buy_below,
        "stagger_1": stagger_1,
        "stagger_2": stagger_2,
        "stagger_3": stagger_3,
        "horizon": horizon,
        "review_window": review_window,
    }

with st.sidebar:
    st.header("Inputs")
    ticker_input = st.text_input(
        "Ticker",
        value="RELIANCE.NS",
        help="Use Yahoo Finance ticker format, e.g. TCS.NS, INFY.NS, HDFCBANK.NS"
    )
    required_return = st.slider("Required Return (%)", 8, 20, 12)
    growth_override = st.slider("Growth Assumption (%)", 0, 20, 8)
    use_auto_growth = st.toggle("Use detected earnings growth when available", value=True)
    st.caption("Best suited for profitable, mature, fundamentally stable businesses.")

# Normalize ticker: auto-append .NS for Indian stocks
raw_symbol = ticker_input.strip()
if "." not in raw_symbol and not raw_symbol.startswith("^"):
    symbol = f"{raw_symbol.upper()}.NS"
else:
    symbol = raw_symbol.upper()

try:
    info, price_hist, financials, balance_sheet = fetch_stock_data(symbol)
    metrics = derive_metrics(info, financials, price_hist)
except Exception as e:
    st.error(f"Could not load stock data for {symbol}: {e}")
    st.stop()

name = metrics["name"] or symbol
current_price = metrics["current_price"]
auto_growth = metrics["growth"]
used_growth = auto_growth if (use_auto_growth and auto_growth is not None and auto_growth > 0) else growth_override

fair_graham = graham_number(metrics["eps"], metrics["book_value"])
fair_eps = eps_fair_value(metrics["eps"], used_growth, required_return)
fair_values = [v for v in [fair_graham, fair_eps] if v is not None and v > 0]
blended_fair = float(np.mean(fair_values)) if fair_values else None
bands = valuation_bands(blended_fair)
view_title, view_text = investment_view(current_price, blended_fair, bands.get("MOS 25%"), bands.get("MOS 40%"))
strategy = build_strategy(current_price, blended_fair, metrics["support_50dma"], metrics["support_200dma"])

st.subheader(f"{name} ({symbol})")
st.caption(f"Sector: {metrics['sector'] or '—'}")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Current Price", format_num(current_price, prefix="Rs. "))
m2.metric("EPS", format_num(metrics["eps"], prefix="Rs. "))
m3.metric("Book Value / Share", format_num(metrics["book_value"], prefix="Rs. "))
m4.metric("Growth Used", format_num(used_growth, suffix="%"))

m5, m6, m7, m8 = st.columns(4)
m5.metric("P/E", format_num(metrics["pe"]))
m6.metric("P/B", format_num(metrics["pb"]))
m7.metric("ROE", format_num(metrics["roe"], suffix="%"))
m8.metric("Debt / Equity", format_num(metrics["debt_to_equity"]))

st.divider()

left, right = st.columns([1.2, 0.8])

with left:
    st.subheader("Intrinsic Value")

    # Safe dataframe rendering - pre-format values instead of using Styler
    def fmt(x):
        if pd.notnull(x) and isinstance(x, (int, float, np.floating, np.integer)):
            return f"Rs. {x:,.2f}"
        return "—"

    display_val_df = pd.DataFrame([
        ["Graham Number", fair_graham],
        ["EPS-based Fair Value", fair_eps],
        ["Blended Fair Value", blended_fair],
        ["MOS 15%", bands.get("MOS 15%")],
        ["MOS 25%", bands.get("MOS 25%")],
        ["MOS 40%", bands.get("MOS 40%")],
    ], columns=["Method", "Value"])
    display_val_df["Value"] = display_val_df["Value"].apply(fmt)
    st.dataframe(display_val_df, use_container_width=True)

    if price_hist is not None and not price_hist.empty:
        hist = price_hist.copy().reset_index()
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=hist["Date"],
                y=hist["Close"],
                mode="lines",
                name="Price",
                line=dict(color="#4f98a3", width=2),
            )
        )
        if blended_fair is not None:
            fig.add_hline(y=blended_fair, line_dash="solid", line_color="#e8af34", annotation_text="Fair Value")
            fig.add_hline(y=bands.get("MOS 25%"), line_dash="dash", line_color="#6daa45", annotation_text="MOS 25%")
            fig.add_hline(y=bands.get("MOS 40%"), line_dash="dot", line_color="#227f8b", annotation_text="MOS 40%")
        fig.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis_title="",
            yaxis_title="Price (Rs.)",
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Investment View")
    if blended_fair is None:
        st.warning("Intrinsic value could not be estimated reliably. EPS or book value may be missing or negative.")
    else:
        st.success(f"{view_title}: {view_text}")

    if strategy:
        st.markdown("### Entry Strategy")
        st.markdown(f"- Ideal buy zone: **Rs. {strategy['ideal_low']:,.2f} - Rs. {strategy['ideal_high']:,.2f}**")
        st.markdown(f"- Buy below: **Rs. {strategy['buy_below']:,.2f}**")
        st.markdown(f"- Staggered allocation: **30%** near Rs. {strategy['stagger_1']:,.2f}, **30%** near Rs. {strategy['stagger_2']:,.2f}, **40%** near Rs. {strategy['stagger_3']:,.2f}")
        st.markdown(f"- Suggested holding horizon: **{strategy['horizon']}**")
        st.markdown(f"- Time window: **{strategy['review_window']}**")

    st.markdown("### Suitability Checks")
    checks = []
    if metrics["eps"] is None or metrics["eps"] <= 0:
        checks.append("Negative or missing EPS reduces Graham-model reliability.")
    if metrics["book_value"] is None or metrics["book_value"] <= 0:
        checks.append("Missing or negative book value makes Graham Number unusable.")
    if metrics["debt_to_equity"] is not None and metrics["debt_to_equity"] > 150:
        checks.append("High leverage may weaken a pure value thesis.")
    if auto_growth is not None and auto_growth > 20:
        checks.append("Very high growth assumptions can overstate fair value for Graham investing.")
    if not checks:
        checks.append("Suitable for first-pass Graham-style screening; verify annual reports before investing.")
    for item in checks:
        st.write(f"- {item}")

st.divider()

st.subheader("Research Notes")
upside = ((blended_fair / current_price) - 1) * 100 if current_price and blended_fair else None

# Safe notes dataframe rendering
notes_data = [
    ["Current Price", format_num(current_price, prefix="Rs. ")],
    ["Blended Fair Value", format_num(blended_fair, prefix="Rs. ")],
    ["Upside / Downside to Fair Value (%)", f"{upside:,.2f}%" if upside is not None else "—"],
    ["50 DMA", format_num(metrics["support_50dma"], prefix="Rs. ")],
    ["200 DMA", format_num(metrics["support_200dma"], prefix="Rs. ")],
    ["Market Cap", format_num(metrics["market_cap"], prefix="Rs. ")],
]
notes_df = pd.DataFrame(notes_data, columns=["Metric", "Value"])
st.dataframe(notes_df, use_container_width=True)

st.info("This page is a screening and planning tool, not investment advice. Confirm numbers against company filings before acting.")
