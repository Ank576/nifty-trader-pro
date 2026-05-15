import time
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Options", page_icon="🎯", layout="wide")

INDEX_SYMBOLS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "NIFTYNXT50"]

POPULAR_SYMBOLS = [
    "NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY",
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "SBIN", "LT", "AXISBANK", "BHARTIARTL", "ITC"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.nseindia.com/option-chain",
    "Connection": "keep-alive",
}


def get_nse_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


@st.cache_data(ttl=60, show_spinner=False)
def fetch_option_chain(symbol: str):
    symbol = symbol.upper().strip()
    session = get_nse_session()

    warmup_urls = [
        "https://www.nseindia.com/",
        "https://www.nseindia.com/option-chain"
    ]

    for warmup_url in warmup_urls:
        try:
            session.get(warmup_url, timeout=20)
        except Exception:
            pass

    if symbol in INDEX_SYMBOLS:
        api_url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    else:
        api_url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"

    last_error = None
    for _ in range(3):
        try:
            response = session.get(api_url, timeout=20)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            last_error = e
            time.sleep(1.5)

    raise last_error


def parse_option_chain(data, selected_expiry=None):
    records = data.get("records", {})
    underlying_value = records.get("underlyingValue")
    timestamp = records.get("timestamp")
    expiry_dates = records.get("expiryDates", [])
    raw_data = records.get("data", [])

    if not expiry_dates:
        return pd.DataFrame(), underlying_value, timestamp, []

    if selected_expiry is None:
        selected_expiry = expiry_dates[0]

    rows = []
    for item in raw_data:
        if item.get("expiryDate") != selected_expiry:
            continue

        strike = item.get("strikePrice")
        ce = item.get("CE", {}) or {}
        pe = item.get("PE", {}) or {}

        rows.append({
            "strikePrice": strike,

            "CE_OI": ce.get("openInterest"),
            "CE_Chg_OI": ce.get("changeinOpenInterest"),
            "CE_Volume": ce.get("totalTradedVolume"),
            "CE_IV": ce.get("impliedVolatility"),
            "CE_LTP": ce.get("lastPrice"),
            "CE_BidQty": ce.get("bidQty"),
            "CE_BidPrice": ce.get("bidprice"),
            "CE_AskPrice": ce.get("askPrice"),
            "CE_AskQty": ce.get("askQty"),

            "PE_BidQty": pe.get("bidQty"),
            "PE_BidPrice": pe.get("bidprice"),
            "PE_AskPrice": pe.get("askPrice"),
            "PE_AskQty": pe.get("askQty"),
            "PE_LTP": pe.get("lastPrice"),
            "PE_IV": pe.get("impliedVolatility"),
            "PE_Volume": pe.get("totalTradedVolume"),
            "PE_Chg_OI": pe.get("changeinOpenInterest"),
            "PE_OI": pe.get("openInterest"),
        })

    df = pd.DataFrame(rows)

    if df.empty:
        return df, underlying_value, timestamp, expiry_dates

    df = df.sort_values("strikePrice").reset_index(drop=True)
    return df, underlying_value, timestamp, expiry_dates


def option_intrinsic(option_type, spot, strike):
    if option_type == "CE":
        return max(spot - strike, 0)
    return max(strike - spot, 0)


def compute_payoff(legs_df, spot_reference, lot_size=1):
    if legs_df.empty:
        return pd.DataFrame()

    price_min = max(1, spot_reference * 0.8)
    price_max = spot_reference * 1.2
    prices = np.linspace(price_min, price_max, 120)

    pnl_list = []
    for s in prices:
        total_pnl = 0
        for _, leg in legs_df.iterrows():
            intrinsic = option_intrinsic(leg["Type"], s, leg["Strike"])
            side_mult = 1 if leg["Side"] == "Buy" else -1
            premium = leg["Premium"]
            qty = leg["Qty"]
            pnl = (intrinsic - premium) * side_mult * qty * lot_size
            total_pnl += pnl
        pnl_list.append(total_pnl)

    return pd.DataFrame({"UnderlyingPrice": prices, "PnL": pnl_list})


st.title("🎯 Options Strategy Builder")
st.caption("Search a stock or index, view NSE option chain, and build payoff charts.")

with st.sidebar:
    st.subheader("Underlying")
    selected_symbol = st.selectbox("Quick Select", POPULAR_SYMBOLS, index=0)
    custom_symbol = st.text_input("Or type symbol", value=selected_symbol)
    symbol = custom_symbol.upper().strip() if custom_symbol else selected_symbol

with st.spinner(f"Fetching option chain for {symbol}..."):
    try:
        option_chain_json = fetch_option_chain(symbol)
        temp_df, spot_price, chain_timestamp, expiry_dates = parse_option_chain(option_chain_json)

        if not expiry_dates:
            st.error(f"No expiry dates found for {symbol}.")
            st.stop()

        selected_expiry = st.sidebar.selectbox("Expiry", expiry_dates, index=0)
        chain_df, spot_price, chain_timestamp, expiry_dates = parse_option_chain(option_chain_json, selected_expiry)

    except Exception as e:
        st.error(f"NSE option-chain fetch failed for {symbol}. This is usually a temporary NSE timeout or session issue.")
        st.caption(str(e))
        st.info("Try again in a few seconds. If it keeps failing, switch symbol once and return to NIFTY.")
        st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Underlying", symbol)
c2.metric("Spot", f"{spot_price:,.2f}" if spot_price else "N/A")
c3.metric("Timestamp", chain_timestamp if chain_timestamp else "N/A")

st.subheader(f"Option Chain — {symbol} — {selected_expiry}")

if chain_df.empty:
    st.warning("No option chain rows available for the selected expiry.")
    st.stop()

st.dataframe(chain_df, use_container_width=True, height=520)

atm_idx = (chain_df["strikePrice"] - spot_price).abs().idxmin() if spot_price else 0
atm_strike = chain_df.loc[atm_idx, "strikePrice"]

st.markdown("### ATM Snapshot")
a1, a2, a3, a4 = st.columns(4)
a1.metric("ATM Strike", f"{atm_strike:,.2f}")
a2.metric("ATM CE LTP", f"{chain_df.loc[atm_idx, 'CE_LTP']}")
a3.metric("ATM PE LTP", f"{chain_df.loc[atm_idx, 'PE_LTP']}")
a4.metric(
    "ATM Total OI",
    f"{(chain_df.loc[atm_idx, 'CE_OI'] or 0) + (chain_df.loc[atm_idx, 'PE_OI'] or 0):,}"
)

st.divider()
st.subheader("Build Strategy")

if "option_legs" not in st.session_state:
    st.session_state["option_legs"] = []

available_strikes = chain_df["strikePrice"].dropna().tolist()

with st.form("add_leg_form"):
    f1, f2, f3, f4, f5 = st.columns(5)

    with f1:
        leg_type = st.selectbox("Option Type", ["CE", "PE"])
    with f2:
        leg_side = st.selectbox("Side", ["Buy", "Sell"])
    with f3:
        default_strike_index = available_strikes.index(atm_strike) if atm_strike in available_strikes else 0
        leg_strike = st.selectbox("Strike", available_strikes, index=default_strike_index)
    with f4:
        leg_qty = st.number_input("Qty", min_value=1, value=1, step=1)
    with f5:
        premium_col = "CE_LTP" if leg_type == "CE" else "PE_LTP"
        premium_series = chain_df.loc[chain_df["strikePrice"] == leg_strike, premium_col]
        default_premium = float(premium_series.iloc[0]) if not premium_series.empty and pd.notna(premium_series.iloc[0]) else 0.0
        leg_premium = st.number_input("Premium", min_value=0.0, value=default_premium, step=0.05)

    add_leg = st.form_submit_button("Add Leg")

if add_leg:
    st.session_state["option_legs"].append({
        "Type": leg_type,
        "Side": leg_side,
        "Strike": float(leg_strike),
        "Qty": int(leg_qty),
        "Premium": float(leg_premium),
        "Expiry": selected_expiry,
        "Underlying": symbol
    })

legs_df = pd.DataFrame(st.session_state["option_legs"])

left, right = st.columns([1, 2])

with left:
    st.markdown("### Strategy Legs")
    if legs_df.empty:
        st.info("No option legs added yet.")
    else:
        st.dataframe(legs_df, use_container_width=True)
        if st.button("Clear Strategy"):
            st.session_state["option_legs"] = []
            st.rerun()

with right:
    st.markdown("### Payoff Chart")
    if legs_df.empty:
        st.info("Add one or more legs to generate payoff.")
    else:
        payoff_df = compute_payoff(legs_df, spot_reference=float(spot_price), lot_size=1)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=payoff_df["UnderlyingPrice"],
            y=payoff_df["PnL"],
            mode="lines",
            name="Payoff",
            line=dict(width=3)
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.add_vline(x=float(spot_price), line_dash="dot", line_color="orange")
        fig.update_layout(
            title=f"Expiry Payoff — {symbol}",
            xaxis_title="Underlying Price at Expiry",
            yaxis_title="Profit / Loss",
            height=520
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown("### OI by Strike")

oi_chart_df = chain_df[["strikePrice", "CE_OI", "PE_OI"]].copy()

fig_oi = go.Figure()
fig_oi.add_trace(go.Bar(x=oi_chart_df["strikePrice"], y=oi_chart_df["CE_OI"], name="Call OI"))
fig_oi.add_trace(go.Bar(x=oi_chart_df["strikePrice"], y=oi_chart_df["PE_OI"], name="Put OI"))
fig_oi.update_layout(
    barmode="group",
    height=500,
    xaxis_title="Strike",
    yaxis_title="Open Interest",
    title=f"Open Interest Distribution — {symbol}"
)
st.plotly_chart(fig_oi, use_container_width=True)
