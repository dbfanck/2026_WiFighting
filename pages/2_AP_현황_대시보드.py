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

# ===============================
# 기본 설정
# ===============================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

mpl.rc('font', family='Malgun Gothic')  # Windows 한글 폰트
mpl.rcParams['axes.unicode_minus'] = False

MAP_WIDTH = 600   # 지도/그래프 가로폭

def icon(emoji: str):
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

# ===============================
# 데이터 로드
# ===============================

data_path = os.path.join(BASE_DIR, "data", "공공와이파이_최종데이터.csv")
df = pd.read_csv(data_path)

# ===============================
# K-means cluster_k3 의미 재정렬
# ===============================

cluster_mean = (
    df.groupby("cluster_k3")[["age_norm", "usage_norm", "density_norm"]]
      .mean()
)

cluster_mean["risk_score"] = (
    cluster_mean["age_norm"]
    + cluster_mean["usage_norm"]
    + cluster_mean["density_norm"]
)

cluster_order = cluster_mean["risk_score"].sort_values().index.tolist()

cluster_rank_map = {
    cluster_order[0]: 0,  # 양호
    cluster_order[1]: 1,  # 보통
    cluster_order[2]: 2,  # 개선 필요
}

df["cluster_k3_rank"] = df["cluster_k3"].map(cluster_rank_map)

# ===============================
# 서울 구 경계 geojson
# ===============================

geojson_path = os.path.join(BASE_DIR, "data", "seoul_gu.geojson")
with open(geojson_path, encoding="utf-8") as f:
    seoul_geo = json.load(f)

# ===============================
# Choropleth 지도 함수 (기존 유지)
# ===============================

def make_choropleth(var_name, caption, log_scale=False):
    m = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=11,
        tiles="cartodbpositron"
    )

    gu_mean = (
        df.groupby("gu")[var_name]
          .mean()
          .reset_index()
    )

    raw_values = gu_mean.set_index("gu")[var_name]

    values = np.log1p(raw_values) if log_scale else raw_values

    colormap = linear.YlGnBu_09.scale(values.min(), values.max())
    colormap.caption = caption
    colormap.add_to(m)

    def style_function(feature):
        gu_name = feature["properties"]["SIG_KOR_NM"]
        v = raw_values.get(gu_name, None)

        if v is None or pd.isna(v):
            fill_color = "#ffffff"
        else:
            fill_color = colormap(np.log1p(v) if log_scale else v)

        return {
            "fillColor": fill_color,
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

# ===============================
# 📍 개별 AP 클러스터 지도 (핵심)
# ===============================

def make_ap_cluster_map():
    m = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=11,
        tiles="cartodbpositron"
    )

    COLOR_MAP = {
        1: "#F0AD4E",  # 🟡 유지관리 필요 (amber)
        2: "#D9534F",  # 🔴 교체 위험 (muted red)
    }

    # 양호(0) AP 제외
    df_target = df[df["cluster_k3_rank"] >= 1]

    for _, row in df_target.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=6 if row["cluster_k3_rank"] == 1 else 8,
            fill=True,
            fill_color=COLOR_MAP[row["cluster_k3_rank"]],
            fill_opacity=0.75,
            color=None,     # ✅ 테두리 제거
            weight=0,
            tooltip=f"""
            상태: {"보통" if row["cluster_k3_rank"] == 1 else "개선 필요"}<br>
            자치구: {row['gu']}
            """
        ).add_to(m)

    return m

# ===============================
# 📊 설치 수 TOP10
# ===============================

wifi_recent = (
    df.groupby("gu")
      .size()
      .sort_values(ascending=False)
      .head(10)
)

st.subheader("📍 자치구별 공공 Wi-Fi 설치 수 TOP10")

col_left, col_right = st.columns([2, 1])

with col_left:
    fig, ax = plt.subplots(figsize=(8, 4))
    wifi_recent.plot(kind="bar", ax=ax)
    ax.set_xticklabels(wifi_recent.index, rotation=45, ha="right")
    ax.set_xlabel("자치구")
    ax.set_ylabel("설치된 AP 수")
    st.pyplot(fig)

with col_right:
    st.markdown("### ⬆️ 설치 수 Top3")
    for gu, count in wifi_recent.head(3).items():
        st.markdown(f"**{gu}** — {count}개")

# ===============================
# 📍 노후도 / 밀집도 / 이용량 (기존 유지)
# ===============================

st.subheader("📍 자치구 공공 Wi-Fi 밀집도")
st_folium(make_choropleth("density_norm", "와이파이 밀집도"), width=MAP_WIDTH, height=450)

st.subheader("📍 자치구 공공 Wi-Fi 노후도")
st_folium(make_choropleth("age_norm", "설치연도 노후도"), width=MAP_WIDTH, height=450)

st.subheader("📍 자치구 AP 이용량")
st_folium(make_choropleth("usage_norm", "AP 이용량", log_scale=True), width=MAP_WIDTH, height=450)

# ===============================
# 📍 개별 AP 교체·유지관리 대상 지도
# ===============================

st.subheader("📍 교체·유지관리 대상 공공 Wi-Fi AP 분포 (개별 AP 기준)")

m_ap_cluster = make_ap_cluster_map()
st_folium(m_ap_cluster, width=MAP_WIDTH, height=500)

st.markdown("""
### 📊 표시 기준

🟡 **유지관리 필요**  
- 일부 지표에서 관리 필요  

🔴 **교체 위험**  
- 교체 또는 증설 우선 검토 대상  

※ 양호 AP는 시각화에서 제외
""")
