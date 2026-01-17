import streamlit as st
from pages.subpages.tour_map import render as tour_map_render
from pages.subpages.wifi_speed import render as wifi_speed_render

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

st.set_page_config(
    page_title="서비스 확장 구조",
    page_icon="🚀",
)

icon("🚀")
st.title("서비스 확장 구조")

# 탭 설정
tab1, tab2 = st.tabs(["🚄 관광객 Wi-Fi 지도", "📶 Wi-Fi 예상 속도"], width=800)

with tab1:
    st.markdown("지도")

with tab2:
    wifi_speed_render()