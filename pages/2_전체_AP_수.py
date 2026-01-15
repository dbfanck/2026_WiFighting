import os
import streamlit as st
import pandas as pd
import numpy as np 
import folium
import json
from branca.colormap import linear
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib as mpl

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

mpl.rc('font', family='Malgun Gothic')  # Windows 한글 폰트
mpl.rcParams['axes.unicode_minus'] = False


def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="전체 AP 수",
    page_icon="📡",
)

icon("📡")
st.title("전체 AP 수")

# 1) CSV 불러오기
data_path = os.path.join(BASE_DIR, "data", "공공와이파이_최종데이터.csv")
df = pd.read_csv(data_path)

# 2) 구별 평균값 만들기 (AP가 여러 개라서)
gu_mean = (
    df.groupby('gu')[['age_norm', 'usage_norm', 'density_norm']]
      .mean()
      .reset_index()
)

# 3) 서울 구 경계 geojson 불러오기
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
geojson_path = os.path.join(BASE_DIR, "data", "seoul_gu.geojson")

with open(geojson_path, encoding='utf-8') as f:
    seoul_geo = json.load(f)

# 4) 지도 만드는 함수
def make_choropleth(var_name, caption, log_scale=False):
    """
    var_name : 'age_norm', 'usage_norm', 'density_norm' 중 하나
    caption  : 색범례 제목으로 쓸 문자열
    """
    # 서울 중심으로 기본 지도 생성
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11,
                   tiles='cartodbpositron')


    # 구 이름 -> 값 매핑
    raw_values = gu_mean.set_index('gu')[var_name]

    # 로그 스케일 여부에 따라 사용할 값 결정
    if log_scale:
        values = np.log1p(raw_values)          # log(1+x)
        caption = caption + " (log scale)"
    else:
        values = raw_values

    # 값 범위에 맞는 컬러맵
    colormap = linear.YlGnBu_09.scale(values.min(), values.max())
    colormap.caption = caption
    colormap.add_to(m)

    # geojson 스타일 함수
    def style_function(feature):
        gu_name = feature['properties']['SIG_KOR_NM']
        v = raw_values.get(gu_name, None)


        if v is None or pd.isna(v):
            fill_color = '#ffffff'   # 데이터 없으면 흰색
        else:
            color_value = np.log1p(v) if log_scale else v
            fill_color = colormap(color_value)

        return {
            'fillColor': fill_color,
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7,
        }

    # 툴팁(마우스 올렸을 때)
    tooltip = folium.GeoJsonTooltip(
        fields=['SIG_KOR_NM'],             # geojson에 있는 필드 이름
        aliases=['구 이름:'],              # 표시될 라벨
        localize=True
    )

    folium.GeoJson(
        seoul_geo,
        style_function=style_function,
        tooltip=tooltip,
    ).add_to(m)

    return m

wifi_recent = (df.groupby('gu').size().sort_values(ascending=False).head(10))

st.subheader("📍 자치구별 공공 Wi-Fi 설치 수 TOP10")
plt.figure(figsize=(14, 6))
wifi_recent.plot(kind='bar')
plt.xticks(rotation=45)
plt.xlabel("자치구")
plt.ylabel("설치된 AP 수")

st.pyplot(plt)

st.markdown("### 🔝 설치 수 Top3")

top3_install = wifi_recent.head(3)
for gu, count in top3_install.items():
    st.write(f"**{gu}** — {count}개")


st.subheader("📍 자치구 공공 Wi-Fi 밀집도")
m_density = make_choropleth('density_norm', '와이파이 밀집도 (density_norm)')
st_folium(m_density, width=900, height=600) ### 🔹

density_top3 = (
    gu_mean[['gu', 'density_norm']]
    .sort_values('density_norm', ascending=False)
    .head(3)
)

st.markdown("### 🔝 밀집도 Top3")
for idx, row in density_top3.iterrows():
    st.write(f"**{row['gu']}** — {row['density_norm']:.3f}")


st.subheader("📍 자치구 공공 Wi-Fi 노후도")
m_age = make_choropleth('age_norm', '설치연도 노후도 (age_norm)')
st_folium(m_age, width=900, height=600)   ### 🔹 이걸로 지도 렌더링

age_top3 = (
    gu_mean[['gu', 'age_norm']]
    .sort_values('age_norm', ascending=False)
    .head(3)
)

st.markdown("### 🔝 노후도 Top3")
for idx, row in age_top3.iterrows():
    st.write(f"**{row['gu']}** — {row['age_norm']:.3f}")


st.subheader("📍 자치구 AP 이용량")
m_usage = make_choropleth('usage_norm', 'AP 이용량 (usage_norm)', log_scale=True)
st_folium(m_usage, width=900, height=600) ### 🔹

usage_top3 = (
    gu_mean[['gu', 'usage_norm']]
    .sort_values('usage_norm', ascending=False)
    .head(3)
)

st.markdown("### 🔝 AP 이용량 Top3")
for idx, row in usage_top3.iterrows():
    st.write(f"**{row['gu']}** — {row['usage_norm']:.3f}")
