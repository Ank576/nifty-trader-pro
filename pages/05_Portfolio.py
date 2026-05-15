import os
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Portfolio", page_icon="💼", layout="wide")

# ---------- Helpers ----------
def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


@st.cache_resource(show_spinner=False)
def get_kite_client(api_key: str, access_token: str):
    from kiteconnect import KiteConnect

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    return kite


def get_login_url(api_key: str) -> str:
    return f"https://kite.trade/connect/login?api_key={api_key}&v=3"


def instrument_exchange_symbol(row):
    exchange = row.get("exchange", "")
    tradingsymbol = row.get("tradingsymbol", "")
    if exchange and tradingsymbol:
        return f"{exchange}:{tradingsymbol}"
    return tradingsymbol or "-"


def color_pnl(value):
    if value > 0:
        return "🟢"
    if value < 0:
        return "🔴"
    return "⚪"


# ---------- Sidebar ----------
st.title("💼 Portfolio Tracker")
st.caption("Track Zerodha holdings, positions, orders, and funds after Kite authentication.")

with st.sidebar:
    st.header("Zerodha Kite Login")

    default_api_key = st.secrets.get("ZERODHA_API_KEY", "") if hasattr(st, "secrets") else ""
    default_api_secret = st.secrets.get("ZERODHA_API_SECRET", "") if hasattr(st, "secrets") else ""

    api_key = st.text_input(
        "Kite API Key",
        value=os.getenv("ZERODHA_API_KEY", default_api_key),
        help="Enter your Zerodha Kite Connect API key.",
    )

    api_secret = st.text_input(
        "Kite API Secret",
        value=os.getenv("ZERODHA_API_SECRET", default_api_secret),
        type="password",
        help="Required only once to generate access token from request token.",
    )

    if api_key:
        st.markdown(f"[🔐 Login to Zerodha Kite]({get_login_url(api_key)})")

    request_token = st.text_input(
        "Request Token",
        value=st.session_state.get("request_token", ""),
        help="After login, copy the request_token from the redirected URL and paste it here.",
    )

    manual_access_token = st.text_input(
        "Access Token (optional)",
        value=st.session_state.get("access_token", ""),
        type="password",
        help="If you already generated an access token, paste it here directly.",
    )

    generate_clicked = st.button("Generate / Use Session", use_container_width=True, type="primary")
    logout_clicked = st.button("Clear Session", use_container_width=True)

    if logout_clicked:
        for key in ["access_token", "request_token", "profile_name"]:
            st.session_state.pop(key, None)
        st.success("Session cleared. Login again to reconnect.")

    if generate_clicked:
        try:
            if manual_access_token:
                st.session_state["access_token"] = manual_access_token.strip()
                st.success("Access token stored in session.")
            elif api_key and api_secret and request_token:
                from kiteconnect import KiteConnect

                kite = KiteConnect(api_key=api_key)
                session_data = kite.generate_session(
                    request_token.strip(),
                    api_secret=api_secret.strip(),
                )
                st.session_state["access_token"] = session_data["access_token"]
                st.session_state["request_token"] = request_token.strip()
                st.success("Kite session created successfully.")
            else:
                st.warning("Provide either an access token, or API key + API secret + request token.")
        except Exception as e:
            st.error(f"Authentication failed: {e}")

access_token = st.session_state.get("access_token")

# ---------- Main ----------
if not api_key:
    st.info("Add your Zerodha Kite API key in the sidebar to begin.")
    st.stop()

if not access_token:
    st.warning("Authenticate from the sidebar to load portfolio data.")
    st.markdown(
        """
**Steps**
1. Click **Login to Zerodha Kite**.
2. Complete login on Zerodha.
3. Copy `request_token` from the redirect URL.
4. Paste it in the sidebar and click **Generate / Use Session**.
"""
    )
    st.stop()

try:
    kite = get_kite_client(api_key, access_token)
    profile = kite.profile()
    st.session_state["profile_name"] = profile.get("user_name", "User")
except Exception as e:
    st.error(f"Unable to initialize Kite session: {e}")
    st.stop()

user_name = st.session_state.get("profile_name", "User")
st.success(f"Connected to Zerodha as {user_name}")

tab1, tab2, tab3, tab4 = st.tabs(["Holdings", "Positions", "Orders", "Funds"])

# ---------- Holdings ----------
with tab1:
    try:
        holdings = kite.holdings()
        holdings_df = pd.DataFrame(holdings)

        if holdings_df.empty:
            st.info("No holdings found.")
        else:
            holdings_df["last_price"] = holdings_df["last_price"].apply(safe_float)
            holdings_df["average_price"] = holdings_df["average_price"].apply(safe_float)
            holdings_df["quantity"] = holdings_df["quantity"].apply(safe_float)
            holdings_df["t1_quantity"] = holdings_df.get("t1_quantity", 0)
            holdings_df["pnl"] = holdings_df["pnl"].apply(safe_float)

            holdings_df["invested_value"] = holdings_df["quantity"] * holdings_df["average_price"]
            holdings_df["current_value"] = holdings_df["quantity"] * holdings_df["last_price"]
            holdings_df["day_change_pct"] = holdings_df.get("day_change_percentage", 0)

            total_invested = holdings_df["invested_value"].sum()
            total_current = holdings_df["current_value"].sum()
            total_pnl = holdings_df["pnl"].sum()
            total_pnl_pct = (total_pnl / total_invested * 100) if total_invested else 0

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Invested Value", f"₹{total_invested:,.2f}")
            c2.metric("Current Value", f"₹{total_current:,.2f}")
            c3.metric("Total P&L", f"₹{total_pnl:,.2f}", f"{total_pnl_pct:.2f}%")
            c4.metric("Holdings Count", int(len(holdings_df)))

            view_df = holdings_df.copy()
            view_df["symbol"] = view_df.apply(instrument_exchange_symbol, axis=1)
            view_df["weight_pct"] = (view_df["current_value"] / total_current * 100) if total_current else 0

            display_cols = [
                "symbol",
                "quantity",
                "average_price",
                "last_price",
                "invested_value",
                "current_value",
                "pnl",
                "weight_pct",
                "day_change_pct",
            ]

            renamed = view_df[display_cols].rename(
                columns={
                    "symbol": "Symbol",
                    "quantity": "Qty",
                    "average_price": "Avg Price",
                    "last_price": "LTP",
                    "invested_value": "Invested",
                    "current_value": "Current Value",
                    "pnl": "P&L",
                    "weight_pct": "Weight %",
                    "day_change_pct": "Day Change %",
                }
            )

            st.dataframe(renamed, use_container_width=True)

            top_gainers = view_df.sort_values("pnl", ascending=False).head(5)[["symbol", "pnl", "current_value"]]
            top_losers = view_df.sort_values("pnl", ascending=True).head(5)[["symbol", "pnl", "current_value"]]

            gc1, gc2 = st.columns(2)
            with gc1:
                st.subheader("Top Gainers")
                st.dataframe(top_gainers.rename(columns={"symbol": "Symbol", "pnl": "P&L", "current_value": "Value"}), use_container_width=True)
            with gc2:
                st.subheader("Top Losers")
                st.dataframe(top_losers.rename(columns={"symbol": "Symbol", "pnl": "P&L", "current_value": "Value"}), use_container_width=True)

    except Exception as e:
        st.error(f"Failed to fetch holdings: {e}")

# ---------- Positions ----------
with tab2:
    try:
        positions = kite.positions()
        net_positions = pd.DataFrame(positions.get("net", []))
        day_positions = pd.DataFrame(positions.get("day", []))

        c1, c2, c3 = st.columns(3)
        net_pnl = net_positions["pnl"].apply(safe_float).sum() if not net_positions.empty and "pnl" in net_positions.columns else 0
        day_pnl = day_positions["pnl"].apply(safe_float).sum() if not day_positions.empty and "pnl" in day_positions.columns else 0

        c1.metric("Net Positions", int(len(net_positions)))
        c2.metric("Net P&L", f"₹{net_pnl:,.2f}")
        c3.metric("Day P&L", f"₹{day_pnl:,.2f}")

        st.subheader("Net Positions")
        if net_positions.empty:
            st.info("No open or net positions.")
        else:
            net_positions["symbol"] = net_positions.apply(instrument_exchange_symbol, axis=1)
            cols = [c for c in ["symbol", "product", "quantity", "average_price", "last_price", "pnl", "buy_quantity", "sell_quantity"] if c in net_positions.columns]
            st.dataframe(net_positions[cols].rename(columns={"symbol": "Symbol"}), use_container_width=True)

        st.subheader("Day Positions")
        if day_positions.empty:
            st.info("No intraday day positions.")
        else:
            day_positions["symbol"] = day_positions.apply(instrument_exchange_symbol, axis=1)
            cols = [c for c in ["symbol", "product", "quantity", "average_price", "last_price", "pnl", "buy_quantity", "sell_quantity"] if c in day_positions.columns]
            st.dataframe(day_positions[cols].rename(columns={"symbol": "Symbol"}), use_container_width=True)

    except Exception as e:
        st.error(f"Failed to fetch positions: {e}")

# ---------- Orders ----------
with tab3:
    try:
        orders = kite.orders()
        orders_df = pd.DataFrame(orders)

        if orders_df.empty:
            st.info("No orders found.")
        else:
            if "order_timestamp" in orders_df.columns:
                orders_df["order_timestamp"] = pd.to_datetime(orders_df["order_timestamp"], errors="coerce")
                orders_df = orders_df.sort_values("order_timestamp", ascending=False)

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Orders", int(len(orders_df)))
            c2.metric("Complete", int((orders_df.get("status", "") == "COMPLETE").sum()) if "status" in orders_df.columns else 0)
            c3.metric("Open / Pending", int(orders_df["status"].isin(["OPEN", "TRIGGER PENDING", "AMO REQ RECEIVED", "VALIDATION PENDING", "PUT ORDER REQ RECEIVED"]).sum()) if "status" in orders_df.columns else 0)

            cols = [
                c for c in [
                    "order_timestamp",
                    "tradingsymbol",
                    "exchange",
                    "transaction_type",
                    "product",
                    "order_type",
                    "quantity",
                    "price",
                    "average_price",
                    "status",
                    "status_message",
                ] if c in orders_df.columns
            ]
            st.dataframe(orders_df[cols], use_container_width=True)

    except Exception as e:
        st.error(f"Failed to fetch orders: {e}")

# ---------- Funds ----------
with tab4:
    try:
        margins = kite.margins()
        equity = margins.get("equity", {})

        available = equity.get("available", {})
        utilised = equity.get("utilised", {})

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Available Cash", f"₹{safe_float(available.get('cash')):,.2f}")
        c2.metric("Opening Balance", f"₹{safe_float(available.get('opening_balance')):,.2f}")
        c3.metric("Utilised Debits", f"₹{safe_float(utilised.get('debits')):,.2f}")
        c4.metric("SPAN / Exposure", f"₹{safe_float(utilised.get('span')) + safe_float(utilised.get('exposure')):,.2f}")

        st.subheader("Available Funds")
        st.json(available)

        st.subheader("Utilised Funds")
        st.json(utilised)

    except Exception as e:
        st.error(f"Failed to fetch funds: {e}")

st.divider()
st.caption(f"Last refreshed: {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}")
