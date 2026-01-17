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

st.markdown("""
1. 시각화 분석을 통한 제한적 예산 환경에서의 공공 Wi-Fi 정책 고도화
설치 수 중심 접근 방식인 기존의 공공 와이파이 정책에서 벗어나, 실제 이용량과 공간 밀집도를 반영하여 한정적인 예산 내에서 효율적인 정책을 제시할 수 있다. 특히 노후도와 밀집도가 동시에 높은 지역은 우선 교체 대상으로, 저이용·저밀집 지역은 신규 설치 재검토 대상으로 분류하여 정책 효율을 극대화할 수 있다.

2. 다양한 이용자 군집을 위한 웹 플랫폼 배포
웹 플랫폼은 정책 담당자뿐만 아니라 일반 시민과 외국인 관광객에게도 공공 Wi-Fi 서비스 현황을 직관적으로 제공함으로써, 공공 데이터의 실질적 활용성과 투명성을 높이는 효과를 기대할 수 있다.
""")