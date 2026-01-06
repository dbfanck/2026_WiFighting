import streamlit as st

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

st.set_page_config(
    page_title="정책 의사 결정",
    page_icon="📊",
)

icon("📊")
st.title("정책 의사 결정")