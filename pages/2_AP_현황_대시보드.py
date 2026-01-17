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

mpl.rc('font', family='Malgun Gothic')
mpl.rcParams['axes.unicode_minus'] = False

MAP_WIDTH = 600

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

# (1) 기본 데이터 – 설치 수, 위치 등
@st.cache_data
def load_base_data():
    data_path = os.path.join(BASE_DIR, "data", "공공와이파이_최종데이터.csv")
    return pd.read_csv(data_path)

df = load_base_data()

# (2) 🔥 클러스터링 전용 데이터 – score, cluster 결과
@st.cache_data
def load_cluster_data():
    cluster_path = os.path.join(BASE_DIR, "data", "클러스터링전용.csv")
    return pd.read_csv(cluster_path)

df_cluster = load_cluster_data()

# (3) 서울 구 경계 geojson 데이터
@st.cache_resource
def load_geojson():
    geojson_path = os.path.join(BASE_DIR, "data", "seoul_gu.geojson")
    with open(geojson_path, encoding="utf-8") as f:
        return json.load(f)

seoul_geo = load_geojson()

# ===============================
# Choropleth 지도 함수 (df를 인자로 받음)
# ===============================

def make_choropleth(df_src, var_name, caption, log_scale=False):
    m = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=11,
        tiles="cartodbpositron"
    )

    gu_mean = (
        df_src.groupby("gu")[var_name]
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

        return {
            "fillColor": colormap(np.log1p(v) if log_scale else v) if v is not None else "#ffffff",
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
# 📍 개별 AP 교체·유지관리 지도 (클러스터링 전용)
# ===============================

def make_ap_cluster_map():
    m = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=11,
        tiles="cartodbpositron"
    )

    COLOR_MAP = {
        1: "#F0AD4E",  # 🟡 유지관리
        2: "#D9534F",  # 🔴 교체권장
    }

    LABEL_MAP = {
        1: "유지관리 대상",
        2: "교체 권장 대상",
    }

    df_target = (
        df_cluster[df_cluster["cluster_k3_rank"].isin([1, 2])]
        .sort_values("cluster_k3_rank")
    )

    for _, row in df_target.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=4 if row["cluster_k3_rank"] == 1 else 6,  # 점 작게
            fill=True,
            fill_color=COLOR_MAP[row["cluster_k3_rank"]],
            fill_opacity=0.8,
            color=None,
            weight=0,
            tooltip=f"""
            <b>상태</b>: {LABEL_MAP[row['cluster_k3_rank']]}<br>
            <b>자치구</b>: {row['gu']}<br>
            <b>설치유형</b>: {row['설치유형']}<br>
            <b>노후도 점수</b>: {row['age_score']:.2f}<br>
            <b>이용량 점수</b>: {row['usage_score']:.2f}<br>
            <b>밀집도 점수</b>: {row['density_score']:.2f}
            """
        ).add_to(m)

    return m

# ===============================
# 📊 자치구별 설치 수 TOP10 (기본 df 사용)
# ===============================

# 탭 설정
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📡 설치 현황", "📍 밀집도", "🕰 노후도", "📶 이용량", "📉 저이용 AP", "📊 종합 상태"], width=800)

wifi_recent = (
    df.groupby("gu")
      .size()
      .sort_values(ascending=False)
      .head(10)
)

# -----------------------------
# 📍 자치구별 공공 Wi-Fi 설치 수 TOP10
# -----------------------------
with tab1:
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
# 📍 지표별 Choropleth 지도 (클러스터링 전용 df 사용)
# ===============================

with tab2:
    st.subheader("📍 자치구 공공 Wi-Fi 밀집도")
    st_folium(
        make_choropleth(df_cluster, "density_score", "와이파이 밀집도"),
        width=MAP_WIDTH,
        height=450
    )

with tab3:
    st.subheader("📍 자치구 공공 Wi-Fi 노후도")
    st_folium(
        make_choropleth(df_cluster, "age_score", "설치연도 노후도"),
        width=MAP_WIDTH,
        height=450
    )

with tab4:
    st.subheader("📍 자치구 AP 이용량")
    st_folium(
        make_choropleth(df_cluster, "usage_score", "AP 이용량"),
        width=MAP_WIDTH,
        height=450
    )

with tab5:
    st.subheader("📉 저이용 AP 집중 지역")
    
    # 이용량 하위 20%
    q20 = df["usage_norm"].quantile(0.2)
    low20 = df[df["usage_norm"] <= q20]

    # 구별 개수 집계
    low20_counts = (low20.groupby("gu").size().sort_values(ascending=False))

    # 이용량 하위 20% -> 구별 개수 표기 그래프
    fig, ax = plt.subplots(figsize=(10, 4))
    low20_counts.plot(kind="bar", ax=ax)
    ax.set_xlabel("자치구")
    ax.set_ylabel("하위 20% AP 개수")
    ax.set_title("자치구별 이용량 하위 20% AP 개수")
    ax.set_xticklabels(low20_counts.index, rotation=45, ha="right")
    st.pyplot(fig)

# ===============================
# 📍 개별 AP 지도
# ===============================

with tab6:
    st.subheader("📍 교체·유지관리 대상 공공 Wi-Fi AP 분포 (개별 AP 기준)")

    st_folium(make_ap_cluster_map(), width=MAP_WIDTH, height=500)

    st.markdown("""
    ### 📊 표시 기준

    🟡 **유지관리 대상**  
    - 일부 지표에서 관리 필요  

    🔴 **교체 권장 대상**  
    - 노후·과부하·비효율적 밀집 등으로 우선 조치 필요  

    ※ 양호 AP는 시각화에서 제외
    """)
