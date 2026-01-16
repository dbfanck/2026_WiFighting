import streamlit as st

# 로고 설정
LOGO = "images/logo.png"
st.logo(LOGO, size="large")

# Define the pages
main_page = st.Page("pages/1_메인_대시보드.py", title="Main Page", icon="🏠")
ap_num_page = st.Page("pages/2_전체_AP에_대한_분석.py", title="전체 AP에 대한 분석", icon="📡")
map_page = st.Page("pages/3_지도.py", title="지도", icon="🗺️")
speed_page = st.Page("pages/4_위치별_Wi-Fi_예상_속도.py", title="위치별 Wi-Fi 예상 속도", icon="⚡")
policy_page = st.Page("pages/5_정책_의사_결정.py", title="정책 의사 결정", icon="📊")

# Set up navigation
pg = st.navigation([main_page, ap_num_page, map_page, speed_page, policy_page])

# Run the selected page
pg.run()