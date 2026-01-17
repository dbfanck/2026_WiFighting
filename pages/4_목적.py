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
st.title("목적")

left, right = st.columns([2.5, 1])

with left:
    st.image("./images/목적_이미지_1.jpg")

with right:
    st.image("./images/목적_이미지_2.jpg")

st.markdown("""
공공 Wi-Fi 이용량 증가와 통신비 절감 효과라는 장점에도, 최근 관련 예산이 지속적으로 축소되면서 보다 효율적인 정책 전환이 요구되고 있다.[1]
현재 자치구별 설치 수 확대 방식은 AP 밀집도와 사용량을 반영하지 못해, 일부 지역의 과잉 설치와 서비스 품질 저하를 초래할 가능성이 있다.
본 프로젝트는 AP 데이터를 종합 분석하여 노후 장비 교체와 불필요한 설치 최소화하며, 제한된 예산 내에서도 공공 Wi-Fi 서비스 품질을 효과적으로 배치하는 정책 방향을 데이터로 제시하고자 한다.[2]
""")