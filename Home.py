import streamlit as st

# CSS
st.markdown("""
<style>
.dashboard-card {
    background-color: #ffffff;
    border-radius: 16px;
    padding: 24px;
    height: 220px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    transition: all 0.25s ease-in-out;

    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.dashboard-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 10px 24px rgba(0,0,0,0.15);
}

.card-title {
    font-size: 18px;
    font-weight: 600;
    color: #555;
}

.card-value {
    font-size: 42px;
    font-weight: 700;
    margin-top: 12px;
}

.card-icon {
    font-size: 36px;
    opacity: 0.85;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

# 페이지 세팅
st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 메인 대시보드")

# 카드 생성
def dashboard_card(title, value, icon, page, key):
    with st.container():
        # 카드 내용
        st.markdown(f"""
        <div class="dashboard-card">
            <div>
                <div class="card-icon">{icon}</div>
                <div class="card-title">{title}</div>
                <div class="card-value">{value}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 이동 버튼
        st.markdown("<div class=dashboard-button>", unsafe_allow_html=True)
        if st.button("자세히 보기 →", key=key):
            st.switch_page(page)
        st.markdown("</div>", unsafe_allow_html=True)

# 레이아웃 설정
col1, col2 = st.columns([2, 1])
col3, col4 = st.columns([1, 1])

with col1:
    dashboard_card("전체 AP 수", "1,000대", "📡", "pages/1_전체_AP_수.py", "card1")

with col2:
    dashboard_card("지도 보기", "", "🗺️", "pages/2_지도.py", "card2")

with col3:
    dashboard_card("Wi-Fi 예상 속도", "", "⚡", "pages/3_위치별_Wi-Fi_예상_속도.py", "card3")

with col4:
    dashboard_card("정책 의사 결정", "", "📊", "pages/4_정책_의사_결정.py", "card4")