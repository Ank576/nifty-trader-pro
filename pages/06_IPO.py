import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="IPO",
    page_icon="🧾",
    layout="wide"
)

st.markdown("""
<style>
    .block-container {
        max-width: 100% !important;
        padding-top: 0.75rem !important;
        padding-right: 0.75rem !important;
        padding-left: 0.75rem !important;
        padding-bottom: 0rem !important;
    }

    .stApp {
        max-width: 100vw;
    }

    iframe {
        width: 100% !important;
    }

    [data-testid="stHeader"] {
        background: rgba(0, 0, 0, 0);
    }
</style>
""", unsafe_allow_html=True)

st.title("🧾 IPO Tracker")
st.caption("Live IPO dashboard embedded from Trendlyne.")

ipo_widget_html = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            min-width: 100%;
            background: #ffffff;
            overflow-x: auto;
            font-family: Arial, sans-serif;
        }

        .widget-wrap {
            width: 100%;
            min-width: 100%;
            margin: 0;
            padding: 0;
        }

        blockquote.trendlyne-widgets {
            width: 100% !important;
            min-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
    </style>
</head>
<body>
    <div class="widget-wrap">
        <blockquote
            class="trendlyne-widgets"
            data-get-url="https://trendlyne.com/web-widget/ipo-widget/Poppins/?activeCol=006AFF&linksCol=006CFF&primary=202020&secondary=666666&positive=00a25b&negative=ff4e54"
            data-theme="light">
        </blockquote>
    </div>

    <script async src="https://cdn-static.trendlyne.com/static/js/webwidgets/tl-widgets.js" charset="utf-8"></script>
</body>
</html>
"""

components.html(
    ipo_widget_html,
    height=2200,
    scrolling=True
)
