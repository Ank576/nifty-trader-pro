import streamlit as st

st.set_page_config(
    page_title="NIFTY Trader Pro",
    page_icon="📈",
    layout="wide",
)

st.title("📈 NIFTY Trader Pro")
st.caption("Zerodha Kite Connect + Perplexity AI Research + Option Strategy Builder")

st.write(
    """
Welcome to **NIFTY Trader Pro** — a Streamlit-based trading workspace for market tracking, 
AI-assisted research, options strategy analysis, and portfolio monitoring.
"""
)

st.markdown("### Available pages")
st.write("Use the sidebar to open:")
st.markdown(
    """
- Dashboard  
- Research  
- Options  
- Algo Trading  
- Portfolio  
- IPO  
"""
)

st.markdown("### Dashboard")
st.write("Track NIFTY and market activity.")

st.markdown("### Research")
st.write("Run Perplexity-powered stock research.")

st.markdown("### Options")
st.write("Analyze strategies and payoff structures.")

st.write("Start from the sidebar pages to use the full application.")

st.divider()

st.info(
    "This application is intended for educational and research purposes only. "
    "Some market data, option-chain values, and external content may be delayed, "
    "incomplete, or subject to third-party source availability."
)

st.markdown("#### About the creator")
st.write(
    """
**Name:** Ankit Saxena  
**Email:** ankit.saxena76@nmims.edu.in  
**GitHub:** [Ank576](https://github.com/Ank576)
"""
)
