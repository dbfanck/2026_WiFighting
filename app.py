import streamlit as st

# 로고 설정
LOGO = "images/logo.png"
st.logo(LOGO, size="large")

# Define the pages
main_page = st.Page("pages/1_메인_대시보드.py", title="Home", icon="🏠")
ap_num_page = st.Page("pages/2_AP_현황_대시보드.py", title="AP 현황 대시보드", icon="📡")
map_page = st.Page("pages/3_AP_상세_지도.py", title="AP별 상세 지도", icon="🗺️")
policy_purpose_page = st.Page("pages/4_목적.py", title="목적", icon="🎯")
policy_expect_page = st.Page("pages/5_기대효과.py", title="기대효과", icon="✨")
policy_scenario_page = st.Page("pages/6_구별_정책_의사결정_시나리오.py", title="구별 정책 의사 결정", icon="🧭")
policy_extension_page = st.Page("pages/7_서비스_확장_구조.py", title="서비스 확장 구조", icon="🚀")

pages = {
    "Home": [
        main_page,
    ],
    "AP 현황 대시보드": [
        ap_num_page,
    ],
    "지도": [
        map_page,
    ],
    "정책의사결정": [
        policy_purpose_page,
        policy_expect_page,
        policy_scenario_page,
        policy_extension_page
    ]
}

# Set up navigation
pg = st.navigation(pages)

# Run the selected page
pg.run()