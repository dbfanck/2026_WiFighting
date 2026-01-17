import streamlit as st

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

st.set_page_config(
    page_title="정책 의사 결정",
    page_icon="🧭",
)

icon("🧭")
st.title("구별 정책 의사결정 시나리오")

st.markdown(
    "<p style='color:#6b7280; font-size:16px;'>데이터 기반 공공 Wi-Fi 재배치 정책 시뮬레이션</p>",
    unsafe_allow_html=True
)

st.divider()

# -----------------------------
# 🏙 서초구 정책 개요
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
    <h2>🏙 서초구 정책 시나리오</h2>
    <p style="font-size:15px; line-height:1.8;">
    과밀도 위험도와 실제 Wi-Fi 이용량 간의 불균형을 기준으로
    <b>재배치 필요성이 높은 자치구</b>를 도출한다.
    </p>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 📊 자치구 비교
# -----------------------------
st.markdown("### ① 자치구별 과밀도 위험도 ↔ 이용량 불균형 분석")

left, right = st.columns([1.4, 1])

with left:
    st.image("./images/시나리오_이미지_1.png", use_container_width=True)

with right:
    st.image("./images/시나리오_이미지_2.png", use_container_width=True)

st.markdown(
    """
    <div style="
        background-color:#eef2ff;
        padding:20px;
        border-radius:14px;
        margin-top:16px;
    ">
    <p style="font-size:15px; line-height:1.8;">
    👉 <b>서초구부터 ~ 구로구</b>까지
    <span style="color:#1d4ed8;"><b>재배치 필요 가능성이 높은 자치구</b></span>를
    순위 형태로 시각화하였다.
    </p>
    <p style="font-size:15px; line-height:1.8;">
    과밀도 위험도는 높지만 이용량이 낮은 자치구는
    <b>수요 기반이 아닌 설치 중심 정책의 결과</b>로 해석할 수 있다.
    </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------
# 🔍 서초구 심층 분석
# -----------------------------
st.markdown("### ② 과밀도 위험도 TOP1 : 서초구 AP 이용량 분석")
st.image("./images/시나리오_이미지_3.png", use_container_width=True)

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
        <h3>📌 이용 패턴 특징</h3>
        <ul style="line-height:1.8; font-size:15px;">
            <li>AP 이용량 분포는 <b>강한 우측 꼬리(long-tail)</b> 형태</li>
            <li>대부분의 AP는 <b>매우 낮은 이용량</b> 구간에 집중</li>
            <li>소수의 AP만 <b>수천 GB 이상의 트래픽</b> 담당</li>
        </ul>
        <p style="font-size:14px; color:#92400e;">
        → 다수의 AP는 활용도가 낮고, 소수의 AP에 트래픽 집중
        </p>
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
        <h3>🧭 정책 의사결정 시사점</h3>
        <ul style="line-height:1.8; font-size:15px;">
            <li><b>신규 설치보다 재배치·통합 우선</b></li>
            <li>저이용 + 고밀집 AP → <b>이전·철거 후보</b></li>
            <li>고이용 AP → <b>성능 강화(장비 교체, 대역폭 확장)</b></li>
            <li>단순 개수 기준 정책의 한계 명확</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
