import os
from datetime import datetime
import streamlit as st
import pandas as pd
from kiteconnect import KiteConnect

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

NIFTY_50_TOKEN = 256265

def get_kite_client():
    api_key = st.secrets.get("KITE_API_KEY", os.getenv("KITE_API_KEY"))
    access_token = st.secrets.get("KITE_ACCESS_TOKEN", os.getenv("KITE_ACCESS_TOKEN"))

    if not api_key or not access_token:
        return None

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    return kite

@st.cache_data(ttl=5)
def fetch_nifty_quote():
    kite = get_kite_client()
    if kite is None:
        return None

    quote = kite.quote([f"NSE:NIFTY 50"])
    return quote.get("NSE:NIFTY 50")

st.title("📊 NIFTY Dashboard")
st.caption("Real-time NIFTY 50 tracking with Zerodha Kite Connect")

refresh_seconds = st.sidebar.selectbox("Auto-refresh", [5, 10, 15, 30], index=1)
st.sidebar.info("Refresh the page manually or use Streamlit app reruns for updates.")

quote = fetch_nifty_quote()

if quote is None:
    st.error("Kite credentials not found. Add KITE_API_KEY and KITE_ACCESS_TOKEN in Streamlit secrets.")
    st.stop()

last_price = quote.get("last_price")
ohlc = quote.get("ohlc", {})
net_change = last_price - ohlc.get("close", 0) if last_price and ohlc.get("close") else 0
pct_change = (net_change / ohlc.get("close") * 100) if ohlc.get("close") else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("NIFTY 50", f"{last_price:,.2f}" if last_price else "—", f"{net_change:,.2f} ({pct_change:.2f}%)")
c2.metric("Open", f"{ohlc.get('open', 0):,.2f}")
c3.metric("High", f"{ohlc.get('high', 0):,.2f}")
c4.metric("Low", f"{ohlc.get('low', 0):,.2f}")

st.write(f"Last updated: {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}")

st.subheader("Raw Quote")
st.json(quote)

st.subheader("Quick View")
df = pd.DataFrame(
    [{
        "Instrument": "NIFTY 50",
        "Last Price": last_price,
        "Open": ohlc.get("open"),
        "High": ohlc.get("high"),
        "Low": ohlc.get("low"),
        "Previous Close": ohlc.get("close"),
        "% Change": round(pct_change, 2),
    }]
)
st.dataframe(df, use_container_width=True)
