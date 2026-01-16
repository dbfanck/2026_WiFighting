import os
import streamlit as st
import pandas as pd
import numpy as np
import json
import folium
from branca.colormap import linear
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import matplotlib as mpl

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

mpl.rc('font', family='Malgun Gothic')  # Windows 한글 폰트
mpl.rcParams['axes.unicode_minus'] = False

MAP_WIDTH = 600   # ▶ 그래프/지도 왼쪽 컬럼 가로폭에 맞춰 줄 값

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

st.set_page_config(
    page_title="AP 현황 대시보드",
    page_icon="📡",
)

icon("📡")
st.title("AP 현황 대시보드")

# 1) CSV 불러오기
data_path = os.path.join(BASE_DIR, "data", "공공와이파이_최종데이터.csv")
df = pd.read_csv(data_path)

# ===============================
# K-means cluster_k3 의미 재정렬
# ===============================

# 클러스터별 평균 계산
cluster_mean = (
    df.groupby("cluster_k3")[["age_norm", "usage_norm", "density_norm"]]
      .mean()
)

# 종합 위험도 점수 (클수록 상태 나쁨)
cluster_mean["risk_score"] = (
    cluster_mean["age_norm"]
    + cluster_mean["usage_norm"]
    + cluster_mean["density_norm"]
)

# 위험도 낮은 순서로 정렬
cluster_order = cluster_mean["risk_score"].sort_values().index.tolist()

# 의미 매핑: 0=양호, 1=보통, 2=개선 필요
cluster_rank_map = {
    cluster_order[0]: 0,  # 양호
    cluster_order[1]: 1,  # 보통
    cluster_order[2]: 2,  # 개선 필요
}

# 의미 기반 클러스터 컬럼 생성
df["cluster_k3_rank"] = df["cluster_k3"].map(cluster_rank_map)


# 2) 구별 평균값
gu_mean = (
    df.groupby('gu')[['age_norm', 'usage_norm', 'density_norm']]
      .mean()
      .reset_index()
)

# ===============================
# 구별 대표 클러스터 계산
# ===============================

gu_cluster = (
    df.groupby("gu")["cluster_k3_rank"]
      .mean()
      .round()
      .astype(int)
      .reset_index()
)


# 3) 서울 구 경계 geojson
geojson_path = os.path.join(BASE_DIR, "data", "seoul_gu.geojson")
with open(geojson_path, encoding='utf-8') as f:
    seoul_geo = json.load(f)

# 4) 지도 함수
def make_choropleth(var_name, caption, log_scale=False):
    m = folium.Map(location=[37.5665, 126.9780],
                   zoom_start=11,
                   tiles='cartodbpositron')

    raw_values = gu_mean.set_index('gu')[var_name]

    if log_scale:
        values = np.log1p(raw_values)
        caption = caption + " (log scale)"
    else:
        values = raw_values

    colormap = linear.YlGnBu_09.scale(values.min(), values.max())
    colormap.caption = caption
    colormap.add_to(m)

    def style_function(feature):
        gu_name = feature['properties']['SIG_KOR_NM']
        v = raw_values.get(gu_name, None)

        if v is None or pd.isna(v):
            fill_color = '#ffffff'
        else:
            color_value = np.log1p(v) if log_scale else v
            fill_color = colormap(color_value)

        return {
            'fillColor': fill_color,
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7,
        }

    tooltip = folium.GeoJsonTooltip(
        fields=['SIG_KOR_NM'],
        aliases=['구 이름:'],
        localize=True
    )

    folium.GeoJson(
        seoul_geo,
        style_function=style_function,
        tooltip=tooltip,
    ).add_to(m)

    return m

# ===============================
# 클러스터 전용 지도 함수
# ===============================

def make_cluster_map():
    m = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=11,
        tiles='cartodbpositron'
    )

    cluster_dict = gu_cluster.set_index("gu")["cluster_k3_rank"]

    color_map = {
        0: "#2ECC71",  # 초록: 양호
        1: "#F1C40F",  # 노랑: 보통
        2: "#E74C3C",  # 빨강: 개선 필요
    }

    def style_function(feature):
        gu_name = feature["properties"]["SIG_KOR_NM"]
        v = cluster_dict.get(gu_name, None)

        return {
            "fillColor": color_map.get(v, "#ffffff"),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7,
        }

    folium.GeoJson(
        seoul_geo,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["SIG_KOR_NM"],
            aliases=["구 이름:"],
        ),
    ).add_to(m)

    return m



# -----------------------------
# 📍 설치 수 TOP10 + Top3
# -----------------------------
wifi_recent = (df.groupby('gu').size()
               .sort_values(ascending=False)
               .head(10))

st.subheader("📍 자치구별 공공 Wi-Fi 설치 수 TOP10")

col_left, col_right = st.columns([2, 1])

with col_left:
    fig, ax = plt.subplots(figsize=(8, 4))  # 왼쪽 컬럼 폭에 맞게
    wifi_recent.plot(kind='bar', ax=ax)
    ax.set_xticklabels(wifi_recent.index, rotation=45, ha='right')
    ax.set_xlabel("자치구")
    ax.set_ylabel("설치된 AP 수")
    st.pyplot(fig)

with col_right:
    st.markdown("### ⬆️ 설치 수 Top3")
    top3_install = wifi_recent.head(3)
    for gu, count in top3_install.items():
        st.markdown(f"**{gu}** — {count}개")

# -----------------------------
# 📍 밀집도 + Top3
# -----------------------------
st.subheader("📍 자치구 공공 Wi-Fi 밀집도")

col_left, col_right = st.columns([2, 1])

with col_left:
    m_density = make_choropleth('density_norm',
                                '와이파이 밀집도 (density_norm)')
    st_folium(m_density, width=MAP_WIDTH, height=450)

with col_right:
    st.markdown("### ⬆️ 밀집도 Top3")
    density_top3 = (
        gu_mean[['gu', 'density_norm']]
        .sort_values('density_norm', ascending=False)
        .head(3)
    )
    for _, row in density_top3.iterrows():
        st.markdown(f"**{row['gu']}** — {row['density_norm']:.3f}")

# -----------------------------
# 📍 노후도 + Top3
# -----------------------------
st.subheader("📍 자치구 공공 Wi-Fi 노후도")

col_left, col_right = st.columns([2, 1])

with col_left:
    m_age = make_choropleth('age_norm', '설치연도 노후도 (age_norm)')
    st_folium(m_age, width=MAP_WIDTH, height=450)

with col_right:
    st.markdown("### ⬆️ 노후도 Top3")
    age_top3 = (
        gu_mean[['gu', 'age_norm']]
        .sort_values('age_norm', ascending=False)
        .head(3)
    )
    for _, row in age_top3.iterrows():
        st.markdown(f"**{row['gu']}** — {row['age_norm']:.3f}")



# -----------------------------
# 📍 AP 이용량 + Top3
# -----------------------------
st.subheader("📍 자치구 AP 이용량")

col_left, col_right = st.columns([2, 1])

with col_left:
    m_usage = make_choropleth('usage_norm',
                              'AP 이용량 (usage_norm)',
                              log_scale=True)
    st_folium(m_usage, width=MAP_WIDTH, height=450)

with col_right:
    st.markdown("### ⬆️ AP 이용량 Top3")
    usage_top3 = (
        gu_mean[['gu', 'usage_norm']]
        .sort_values('usage_norm', ascending=False)
        .head(3)
    )
    for _, row in usage_top3.iterrows():
        st.markdown(f"**{row['gu']}** — {row['usage_norm']:.3f}")


# -----------------------------
# 📍 K-means 기반 종합 상태
# -----------------------------
st.subheader("📍 자치구 공공 Wi-Fi 종합 상태 (K-means k=3)")

col_left, col_right = st.columns([2, 1])

with col_left:
    m_cluster = make_cluster_map()
    st_folium(m_cluster, width=MAP_WIDTH, height=450)

with col_right:
    st.markdown("""
### 📊 상태 구분 기준

🟢 **양호**  
- 노후도·이용량·밀집도 모두 낮음  

🟡 **보통**  
- 일부 지표에서 관리 필요  

🔴 **개선 필요**  
- 교체 또는 증설 우선 검토 대상  
""")