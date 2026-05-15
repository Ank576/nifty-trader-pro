import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="IPO", page_icon="🧾", layout="wide")

# ---------- Page Header ----------
st.title("🧾 IPO Tracker")
st.caption("Track ongoing IPO activity, issue details, and market sentiment in one place.")

st.divider()

# ---------- Top Summary ----------
c1, c2, c3 = st.columns(3)
c1.metric("Section", "IPO Market")
c2.metric("Source", "Trendlyne Widget")
c3.metric("Coverage", "Live / Embedded")

st.divider()

# ---------- Intro / Notes ----------
left, right = st.columns([1.15, 0.85])

with left:
    st.subheader("IPO Dashboard")
    st.write(
        "Use this page to monitor IPO listings and issue-level details from Trendlyne "
        "inside the app, without leaving your workflow."
    )

    st.markdown("### What this page shows")
    st.markdown("- Active IPO information")
    st.markdown("- Linked issue details and updates")
    st.markdown("- Embedded market view in a single panel")

with right:
    st.subheader("Usage Notes")
    st.info(
        "This is a live embedded widget. If the source updates, the page reflects the latest "
        "available IPO data automatically."
    )

    st.markdown("### Best use")
    st.markdown("- Check upcoming and active IPOs")
    st.markdown("- Use alongside your Research and Portfolio pages")
    st.markdown("- Validate final decisions from official filings before applying")

st.divider()

# ---------- Styled Widget Container ----------
st.subheader("Live IPO Feed")

st.markdown(
    """
    <style>
    .ipo-widget-shell {
        background: linear-gradient(180deg, rgba(20,24,35,0.98) 0%, rgba(14,17,23,0.98) 100%);
        border: 1px solid rgba(120, 130, 150, 0.22);
        border-radius: 16px;
        padding: 14px 14px 6px 14px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.18);
        margin-top: 8px;
        margin-bottom: 8px;
    }
    .ipo-widget-caption {
        color: #b8c0cc;
        font-size: 0.92rem;
        margin-bottom: 10px;
        padding-left: 4px;
    }
    </style>
    <div class="ipo-widget-shell">
        <div class="ipo-widget-caption">
            Embedded Trendlyne IPO monitor
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

ipo_widget_html = """
<div style="background: transparent; padding: 0; margin: 0;">
    <blockquote
        class="trendlyne-widgets"
        data-get-url="https://trendlyne.com/web-widget/ipo-widget/Poppins/?activeCol=006AFF&linksCol=006CFF&primary=202020&secondary=666666&positive=00a25b&negative=ff4e54"
        data-theme="light">
    </blockquote>
    <script async src="https://cdn-static.trendlyne.com/static/js/webwidgets/tl-widgets.js" charset="utf-8"></script>
</div>
"""

components.html(ipo_widget_html, height=1500, scrolling=True)

st.divider()

# ---------- Footer Note ----------
st.subheader("Notes")
st.dataframe(
    {
        "Item": [
            "Data source",
            "Refresh behavior",
            "Recommended check",
        ],
        "Details": [
            "Trendlyne embedded IPO widget",
            "Updates as the source widget refreshes",
            "Cross-check price bands, dates, and documents with official exchange filings",
        ],
    },
    use_container_width=True,
)

st.info("This page is for tracking and research support, not investment advice.")
