import streamlit as st

# 페이지 세팅
st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide",
)

# 버튼 높이 늘리기
st.markdown(
    """
    <style>
    /* 버튼 */
    div.stButton > button {
        height: 250px;
        border-radius: 20px;
        background: #ffffff;
        transition: all 0.2s ease-in-out;
        line-height: 1.4;
        white-space: pre-line;
        color: white;
    }

    /* 글자 크기 */
    div.stButton button div[data-testid="stMarkdownContainer"] p {
        margin: 0;
        text-align: center;
        color: black;
        font-weight: 600;
        font-size: 26px;
        line-height: 1.4;
        white-space: pre-line;
    }

    /* 아이콘 */
    div.stButton button div[data-testid="stMarkdownContainer"] p::first-line {
        font-size: 48px;
        line-height: 1.2;
    }

    /* hover 효과 */
    div.stButton > button:hover {
        background: #f9fafb;
        transform: translateY(-6px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
    }

    /* 클릭 시 */
    div.stButton > button:active {
        transform: scale(0.98);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🏠 메인 대시보드")

st.markdown("---")

# 레이아웃 설정
col1, col2, col3 = st.columns([1, 1, 1])

# 각 버튼 클릭 시, 해당 페이지로 이동
with col1:
    if st.button("📡\nAP 현황 대시보드", key="card1", width="stretch"):
        st.switch_page("pages/2_AP_현황_대시보드.py")

with col2:
    if st.button("🗺️\n지도 보기", key="card2", width="stretch"):
        st.switch_page("pages/3_AP_상세_지도.py")

with col3:
    if st.button("📊\n정책 의사 결정", key="card4", width="stretch"):
        st.switch_page("pages/4_목적.py")