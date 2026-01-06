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
        background: linear-gradient(135deg, #1f2933, #374151);
        transition: all 0.2s ease-in-out;
        line-height: 1.4;
        white-space: pre-line;
        color: white;
    }

    /* 글자 크기 */
    div.stButton button div[data-testid="stMarkdownContainer"] p {
        margin: 0;
        text-align: center;
        color: #f1f5f9;
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
        background: linear-gradient(
            135deg,
            #374151,
            #4b5563
        );
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

# 레이아웃 설정
col1, col2 = st.columns([2, 1])
col3, col4 = st.columns([1, 1])

# 각 버튼 클릭 시, 해당 페이지로 이동
with col1:
    if st.button("📡\n전체 AP 수", key="card1", width="stretch"):
        st.switch_page("pages/1_전체_AP_수.py")

with col2:
    if st.button("🗺️\n지도 보기", key="card2", width="stretch"):
        st.switch_page("pages/2_지도.py")

with col3:
    if st.button("⚡\nWi-Fi 예상 속도", key="card3", width="stretch"):
        st.switch_page("pages/3_위치별_Wi-Fi_예상_속도.py")

with col4:
    if st.button("📊\n정책 의사 결정", key="card4", width="stretch"):
        st.switch_page("pages/4_정책_의사_결정.py")