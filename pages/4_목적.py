import streamlit as st

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

st.set_page_config(
    page_title="목적",
    page_icon="🎯",
)

icon("🎯")
st.title("프로젝트 목적")

st.markdown(
    "<p style='color: #6b7280; font-size:16px;'>공공 Wi-Fi 정책의 효율적 재설계를 위한 데이터 기반 접근</p>",
    unsafe_allow_html=True
)

st.divider()

# -----------------------------
# 🖼 이미지 영역
# -----------------------------
left, right = st.columns([2.5, 1])

with left:
    st.image("./images/목적_이미지_1.jpg", use_container_width=True)

with right:
    st.image("./images/목적_이미지_2.jpg", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------
# 📌 내용 카드 영역
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div style="
            background-color:#f9fafb;
            padding:24px;
            border-radius:16px;
            box-shadow:0 4px 12px rgba(0,0,0,0.05);
        ">
        <h3>🚨 문제 제시</h3>
        <ul style="line-height:1.8; font-size:15px;">
            <li><b>공공 Wi-Fi 관련 예산이 지속적으로 축소</b></li>
            <li>기존 정책은 <b>자치구별 설치 수 확대</b>에 집중</li>
            <li>AP 밀집도·실제 사용량을 반영하지 못함</li>
            <li style="color:#b91c1c;"><b>과잉 설치 → 품질 저하</b></li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div style="
            background-color:#eef2ff;
            padding:24px;
            border-radius:16px;
            box-shadow:0 4px 12px rgba(0,0,0,0.05);
        ">
        <h3>🎯 프로젝트 목적</h3>
        <ul style="line-height:1.8; font-size:15px;">
            <li>공공 Wi-Fi <b>AP 데이터 종합 분석</b></li>
            <li>노후 장비 교체 대상 도출</li>
            <li>불필요한 신규 설치 최소화</li>
            <li style="color:#1d4ed8;"><b>제한된 예산 내 서비스 품질 극대화</b></li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
    )