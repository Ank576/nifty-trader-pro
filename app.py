import streamlit as st

st.set_page_config(
    page_title="NIFTY Trader Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📈 NIFTY Trader Pro")
st.caption("Zerodha Kite Connect + Perplexity AI Research + Option Strategy Builder")

st.markdown(
    """
Welcome to **NIFTY Trader Pro** — a Streamlit-based trading workspace for
market tracking, AI-assisted research, options strategy analysis, and portfolio monitoring.

### Available pages
Use the sidebar to open:
- Dashboard
- Research
- Options
- Algo Trading
- Portfolio

### Deployment notes
- This `app.py` file is the homepage.
- All additional pages should live directly inside the `pages/` folder.
- Do not use `st.navigation()` here if you want Streamlit to auto-show pages from `pages/`.
"""
)

with st.sidebar:
    st.success("App deployed successfully")
    st.info("Select a page from the sidebar")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Dashboard")
    st.write("Track NIFTY and market activity.")

with col2:
    st.subheader("Research")
    st.write("Run Perplexity-powered stock research.")

with col3:
    st.subheader("Options")
    st.write("Analyze strategies and payoff structures.")

st.divider()
st.write("Start from the sidebar pages to use the full application.")
