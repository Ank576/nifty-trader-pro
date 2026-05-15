import os
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

NIFTY_50_TOKEN = 256265

# ─── Kite Client ────────────────────────────────────────────────────────────
def get_kite_client():
    try:
        from kiteconnect import KiteConnect
        api_key = st.secrets.get("KITE_API_KEY", os.getenv("KITE_API_KEY"))
        access_token = st.secrets.get("KITE_ACCESS_TOKEN", os.getenv("KITE_ACCESS_TOKEN"))
        if not api_key or not access_token:
            return None
        kite = KiteConnect(api_key=api_key)
        kite.set_access_token(access_token)
        return kite
    except Exception:
        return None

@st.cache_data(ttl=5)
def fetch_nifty_quote_kite():
    kite = get_kite_client()
    if kite is None:
        return None
    try:
        quote = kite.quote(["NSE:NIFTY 50"])
        return quote.get("NSE:NIFTY 50")
    except Exception:
        return None

# ─── yfinance Fallback ───────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_nifty_history(period="6mo", interval="1d"):
    """Fetch NIFTY 50 historical data via yfinance (no auth needed)."""
    try:
        import yfinance as yf
        ticker = yf.Ticker("^NSEI")
        df = ticker.history(period=period, interval=interval)
        df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize(None)
        return df
    except Exception as e:
        st.warning(f"Could not fetch historical data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_nifty_quote_yf():
    """Get latest price from yfinance."""
    try:
        import yfinance as yf
        ticker = yf.Ticker("^NSEI")
        info = ticker.fast_info
        return {
            "last_price": info.last_price,
            "open": info.open,
            "high": info.day_high,
            "low": info.day_low,
            "prev_close": info.previous_close,
        }
    except Exception:
        return None

# ─── Projection (Simple Linear Regression on 20-day MA) ─────────────────────
def compute_projection(df, forecast_days=10):
    """Extrapolate 20-day MA trend for `forecast_days` ahead."""
    df = df.copy()
    df["MA20"] = df["Close"].rolling(20).mean()
    ma = df["MA20"].dropna()
    if len(ma) < 5:
        return pd.DataFrame()
    x = np.arange(len(ma))
    slope, intercept = np.polyfit(x, ma.values, 1)
    last_date = ma.index[-1]
    future_dates = pd.bdate_range(start=last_date + timedelta(days=1), periods=forecast_days)
    future_x = np.arange(len(ma), len(ma) + forecast_days)
    projected = slope * future_x + intercept
    proj_df = pd.DataFrame({"Date": future_dates, "Projected": projected})
    proj_df.set_index("Date", inplace=True)
    return proj_df

# ─── Page Header ─────────────────────────────────────────────────────────────
st.title("📊 NIFTY Dashboard")
st.caption("Real-time NIFTY 50 tracking · Historical chart · Price projection")

# ─── Sidebar Controls ────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    period_map = {"1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y", "2 Years": "2y"}
    selected_period = st.selectbox("Historical Period", list(period_map.keys()), index=2)
    chart_type = st.radio("Chart Type", ["Candlestick", "Line"], index=0)
    show_projection = st.toggle("Show 10-Day Projection", value=True)
    show_volume = st.toggle("Show Volume", value=True)
    st.divider()
    st.info("Live quote requires Zerodha Kite credentials. Historical data loads automatically via Yahoo Finance.")

period = period_map[selected_period]

# ─── Live Quote ──────────────────────────────────────────────────────────────
kite_quote = fetch_nifty_quote_kite()
yf_quote = fetch_nifty_quote_yf()

if kite_quote:
    last_price = kite_quote.get("last_price")
    ohlc = kite_quote.get("ohlc", {})
    open_p, high_p, low_p, prev_close = ohlc.get("open",0), ohlc.get("high",0), ohlc.get("low",0), ohlc.get("close",0)
    data_source = "🟢 Zerodha Kite (Live)"
elif yf_quote:
    last_price = yf_quote["last_price"]
    open_p, high_p, low_p, prev_close = yf_quote["open"], yf_quote["high"], yf_quote["low"], yf_quote["prev_close"]
    data_source = "🟡 Yahoo Finance (Delayed ~15 min)"
else:
    last_price = open_p = high_p = low_p = prev_close = None
    data_source = "🔴 No Data Source"

net_change = (last_price - prev_close) if last_price and prev_close else 0
pct_change = (net_change / prev_close * 100) if prev_close else 0
change_label = f"{net_change:+,.2f} ({pct_change:+.2f}%)"

st.caption(f"Data source: {data_source}")

col1, col2, col3, col4, col5 = st.columns(5)
if last_price:
    col1.metric("NIFTY 50", f"{last_price:,.2f}", change_label)
    col2.metric("Open", f"{open_p:,.2f}")
    col3.metric("High", f"{high_p:,.2f}")
    col4.metric("Low", f"{low_p:,.2f}")
    col5.metric("Prev Close", f"{prev_close:,.2f}")
    st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}")
else:
    st.warning("Could not fetch live quote. Historical chart will still load below.")

st.divider()

# ─── Historical Chart ─────────────────────────────────────────────────────────
st.subheader(f"📈 NIFTY 50 — {selected_period} History")

df = fetch_nifty_history(period=period)

if df.empty:
    st.error("Historical data unavailable. Check your internet connection.")
    st.stop()

df["MA20"] = df["Close"].rolling(20).mean()
df["MA50"] = df["Close"].rolling(50).mean()

rows = 2 if show_volume else 1
row_heights = [0.75, 0.25] if show_volume else [1.0]
fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=row_heights, vertical_spacing=0.04)

if chart_type == "Candlestick":
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name="NIFTY 50",
        increasing_line_color="#00b386", decreasing_line_color="#e84040",
        increasing_fillcolor="#00b386", decreasing_fillcolor="#e84040"
    ), row=1, col=1)
else:
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"], mode="lines", name="NIFTY 50",
        line=dict(color="#4f98a3", width=2)
    ), row=1, col=1)

fig.add_trace(go.Scatter(
    x=df.index, y=df["MA20"], mode="lines", name="MA 20",
    line=dict(color="#e8af34", width=1.5, dash="dot")
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=df.index, y=df["MA50"], mode="lines", name="MA 50",
    line=dict(color="#a86fdf", width=1.5, dash="dash")
), row=1, col=1)

# Projection
if show_projection:
    proj_df = compute_projection(df, forecast_days=10)
    if not proj_df.empty:
        # Connect from last MA20 point
        last_ma_date = df["MA20"].dropna().index[-1]
        last_ma_val = df["MA20"].dropna().iloc[-1]
        proj_x = [last_ma_date] + list(proj_df.index)
        proj_y = [last_ma_val] + list(proj_df["Projected"])
        fig.add_trace(go.Scatter(
            x=proj_x, y=proj_y, mode="lines", name="Projection (MA Trend)",
            line=dict(color="#fd8c04", width=2, dash="longdash"),
            fill="tozeroy", fillcolor="rgba(253,140,4,0.04)"
        ), row=1, col=1)
        # Shaded projection area
        fig.add_vrect(
            x0=str(last_ma_date.date()), x1=str(proj_df.index[-1].date()),
            fillcolor="rgba(253,140,4,0.06)", layer="below", line_width=0,
            annotation_text="Projection", annotation_position="top left",
            annotation_font_color="#fd8c04"
        )

if show_volume and "Volume" in df.columns:
    colors = ["#00b386" if c >= o else "#e84040" for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"], name="Volume",
        marker_color=colors, opacity=0.6
    ), row=2, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1, tickfont=dict(size=11))

fig.update_layout(
    height=600 if show_volume else 500,
    paper_bgcolor="#0e1117",
    plot_bgcolor="#0e1117",
    font=dict(color="#cdccca", family="sans-serif"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis_rangeslider_visible=False,
    margin=dict(l=10, r=10, t=20, b=10),
    hovermode="x unified",
)
fig.update_xaxes(gridcolor="#262523", showgrid=True)
fig.update_yaxes(gridcolor="#262523", showgrid=True, row=1, col=1, tickformat=",.0f", title_text="Price (₹)")

st.plotly_chart(fig, use_container_width=True)

# ─── Stats Table ─────────────────────────────────────────────────────────────
st.subheader("📋 Period Stats")
period_high = df["High"].max()
period_low = df["Low"].min()
last_close = df["Close"].iloc[-1]
first_close = df["Close"].iloc[0]
period_return = ((last_close - first_close) / first_close) * 100
avg_volume = df["Volume"].mean() if "Volume" in df.columns else 0
volatility = df["Close"].pct_change().std() * np.sqrt(252) * 100

s1, s2, s3, s4, s5 = st.columns(5)
s1.metric(f"{selected_period} High", f"₹{period_high:,.2f}")
s2.metric(f"{selected_period} Low", f"₹{period_low:,.2f}")
s3.metric(f"{selected_period} Return", f"{period_return:+.2f}%")
s4.metric("Annualised Volatility", f"{volatility:.1f}%")
if avg_volume:
    s5.metric("Avg Daily Volume", f"{avg_volume/1e6:.1f}M")

if kite_quote:
    with st.expander("🔍 Raw Kite Quote"):
        st.json(kite_quote)
