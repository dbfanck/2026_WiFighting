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

st.subheader("서초구 정책")

st.markdown("**1) 서초구 외에 타 자치구들의 과밀도 위험도 ↔ WIFI 이용량 불균형 순위**")

left, right = st.columns([1.5, 1])

with left:
    st.image("./images/시나리오_이미지_1.png")

with right:
    st.image("./images/시나리오_이미지_2.png")

st.markdown("""
            → **서초구부터 ~ 구로구**까지 **재배치해야 할 가능성이 보이는 자치구들**을 표로 시각화함

            → 만약 과밀도 위험도가 높은 반면, 이용량이 낮은 AP들이 다수인 자치구에선

            “수요 기반이 아닌 설치 중심 정책의 결과” 라고 해석 가능
            """)

# 과밀도 위험도
st.markdown("**2) 과밀도 위험도가 TOP1인 ‘서초구’ AP 분석**")
st.image("./images/시나리오_이미지_3.png")

st.markdown("""
            - 특징
                1. 서초구 AP 이용량 분포는 **강한 우측 꼬리(long-tail) 형태**
                2. 대부분의 AP가 매우 낮은 이용량 구간(0~수백 GB)에 집중
                3. 소수의 AP만 **수천 GB 이상의 매우 높은 이용량**

                → 소수의 AP가 트래픽을 대부분 담당하고, 다수의 AP는 거의 활용되지 않음

            - 결과

                서초구는 **AP 설치 밀집도 위험도가 매우 높은 지역**임에도 불구하고,
                실제 이용 패턴은 **균등 분산이 아닌 극단적인 편중 구조를 보임**

            - 정책 의사결정 시사점
                1. 신규 설치보다 “재배치·통합” 우선

                → 저이용 AP 다수가 존재하기에, **신규 AP 증설의 필요성 낮음**

                → 고이용 AP 주변의 중복 AP는 **통합 또는 재배치 대상**

                1. ‘개수 기준’ 정책의 한계 드러남

                → 단순 AP 수 확대는 **서비스 품질 개선으로 직결되지 않음**

                → **거리 기반 과밀도 지표 + 이용량 지표**를 함께 고려해야 함

                3. 유지보수·교체 우선순위 설정 가능

                → **저이용 + 고밀집 AP** → 철거/이전 후보

                → **고이용 AP** → 성능 강화(장비 교체, 대역폭 확장)
            """)