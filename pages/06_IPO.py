import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="IPO",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 IPO Tracker")
st.caption("Live IPO dashboard embedded from Trendlyne.")

ipo_widget_html = """
<div style="width:100%; margin:0; padding:0;">
    <blockquote
        class="trendlyne-widgets"
        data-get-url="https://trendlyne.com/web-widget/ipo-widget/Poppins/?activeCol=006AFF&linksCol=006CFF&primary=202020&secondary=666666&positive=00a25b&negative=ff4e54"
        data-theme="light">
    </blockquote>
    <script
        async
        src="https://cdn-static.trendlyne.com/static/js/webwidgets/tl-widgets.js"
        charset="utf-8">
    </script>
</div>
"""

components.html(
    ipo_widget_html,
    height=2200,
    scrolling=True
)
