import streamlit as st

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

st.set_page_config(
    page_title="기대효과",
    page_icon="✨",
)

icon("✨")
st.title("기대효과")

st.markdown(
    "<p style='color:#6b7280; font-size:16px;'>데이터 기반 공공 Wi-Fi 정책 전환을 통한 실질적 효과</p>",
    unsafe_allow_html=True
)

st.divider()

# -----------------------------
# 🌟 기대효과 카드
# -----------------------------
st.markdown(
    """
    <div style="
        background-color:#f8fafc;
        padding:28px;
        border-radius:18px;
        box-shadow:0 6px 16px rgba(0,0,0,0.06);
        margin-bottom:32px;
    ">
    <h2>🌟 기대효과</h2>

    <h4>① 제한적 예산 환경에서의 정책 고도화</h4>
    <p style="line-height:1.8; font-size:15px;">
    기존의 <b>설치 수 중심 공공 Wi-Fi 정책</b>에서 벗어나,
    실제 <b>이용량과 공간 밀집도</b>를 반영한 분석을 통해
    <span style="color:#2563eb;"><b>한정된 예산 내에서도 효율적인 정책 설계</b></span>가 가능하다.
    </p>

    <h4>② 다양한 이용자 군집을 위한 웹 플랫폼 제공</h4>
    <p style="line-height:1.8; font-size:15px;">
    정책 담당자뿐 아니라 <b>일반 시민 및 외국인 관광객</b>에게도
    공공 Wi-Fi 현황을 직관적으로 제공하여
    <span style="color:#059669;"><b>공공 데이터의 활용성과 정책 투명성</b></span>을 제고할 수 있다.
    </p>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 🚧 한계점 & 확장 가능성
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div style="
            background-color:#fff7ed;
            padding:24px;
            border-radius:16px;
            box-shadow:0 4px 12px rgba(0,0,0,0.05);
        ">
        <h3>🚧 한계점</h3>
        <ul style="line-height:1.8; font-size:15px;">
            <li>공공 데이터 기반 분석으로 <b>체감 속도·하드웨어 성능 반영 한계</b></li>
            <li>유동 인구, 시간대별 트래픽 등 데이터 확보 제약</li>
            <li>AP 모델별 성능 차이에 대한 정보 부족</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div style="
            background-color:#ecfeff;
            padding:24px;
            border-radius:16px;
            box-shadow:0 4px 12px rgba(0,0,0,0.05);
        ">
        <h3>🚀 확장 가능성</h3>
        <ul style="line-height:1.8; font-size:15px;">
            <li>유동 인구 · 실측 속도 · AP 모델 데이터 결합</li>
            <li><b>정교한 서비스 품질 지표</b> 산출 가능</li>
            <li>클러스터 다양화 및 <b>시계열 분석</b> 적용</li>
            <li>외국인·시민 대상 <b>Wi-Fi 탐색 및 속도 예측 서비스</b> 확장</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
    )