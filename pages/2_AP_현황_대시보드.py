import os
import streamlit as st
import pandas as pd
import numpy as np
import json
import folium
from branca.colormap import linear
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as fm

# ===============================
# 기본 설정
# ===============================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# 한글 폰트 설정
FONT_PATH = os.path.join(BASE_DIR, "fonts", "NanumGothic-Regular.ttf")
font_prop = fm.FontProperties(fname=FONT_PATH)
mpl.rcParams["axes.unicode_minus"] = False

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
# 데이터 로드 ( 단일 CSV)
# ===============================

data_path = os.path.join(BASE_DIR, "data", "AP_data.csv")
df = pd.read_csv(data_path)

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

    return m.get_root().render(), gu_mean

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
        df[df["cluster_k3_rank"].isin([1, 2])]
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
            <b>설치유형</b>: {row['install_type']}<br>
            <b>노후도 점수</b>: {row['age_norm']:.2f}<br>
            <b>이용량 점수</b>: {row['usage_norm']:.2f}<br>
            <b>밀집도 점수</b>: {row['density_norm']:.2f}
            """
        ).add_to(m)

    return m.get_root().render()

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
        ax.set_xticklabels(wifi_recent.index, rotation=45, ha="right", fontproperties=font_prop)
        ax.set_xlabel("자치구", fontproperties=font_prop)
        ax.set_ylabel("설치된 AP 수", fontproperties=font_prop)
        st.pyplot(fig)

    with col_right:
        st.markdown("### ⬆️ 설치 수 Top5")
        for gu, count in wifi_recent.head(5).items():
            st.markdown(f"**{gu}** — {count}개")

# ===============================
# 📍 지표별 Choropleth 지도 (클러스터링 전용 df 사용)
# ===============================

with tab2:
    st.subheader("📍 자치구 공공 Wi-Fi AP 설치 과밀도 위험도")
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        m_density, mean_value = make_choropleth(df, "density_norm", "와이파이 밀집도")
        components.html(m_density, height=450, width=MAP_WIDTH)

    with col_right:
        st.markdown("### ⬆️ AP 설치 과밀도 위험도 Top 5")
        density_top5 = (mean_value.sort_values('density_norm', ascending=False).head(5))
        for _, row in density_top5.iterrows():
            st.markdown(f"**{row['gu']}** — {row['density_norm']:.3f}")

with tab3:
    st.subheader("📍 자치구 공공 Wi-Fi 노후도")
    col_left, col_right = st.columns([2, 1])

    with col_left:
        m_age, mean_value = make_choropleth(df, "age_norm", "설치연도 노후도")
        components.html(m_age, height=450, width=MAP_WIDTH)

    with col_right:
        st.markdown("### ⬆️ 노후도 Top5")
        age_top5 = (mean_value.sort_values('age_norm', ascending=False).head(5))
        for _, row in age_top5.iterrows():
            st.markdown(f"**{row['gu']}** — {row['age_norm']:.3f}")

with tab4:
    st.subheader("📍 자치구 AP 이용량")
    col_left, col_right = st.columns([2, 1])

    with col_left:
        m_usage, mean_value = make_choropleth(df, "usage_norm", "AP 이용량")
        components.html(m_usage, height=450, width=MAP_WIDTH)

    with col_right:
        st.markdown("### ⬆️ AP 이용량 Top5")
        usage_top5 = (mean_value.sort_values('usage_norm', ascending=False).head(5))
        for _, row in usage_top5.iterrows():
            st.markdown(f"**{row['gu']}** — {row['usage_norm']:.3f}")

with tab5:
    st.subheader("📉 저이용 AP 집중 지역")
    col_left, col_right = st.columns([2, 1])
    
    # 이용량 하위 20%
    q20 = df["usage_norm"].quantile(0.2)
    low20 = df[df["usage_norm"] <= q20]

    # 구별 개수 집계
    low20_counts = (low20.groupby("gu").size().sort_values(ascending=False))

    with col_left:
        # 이용량 하위 20% -> 구별 개수 표기 그래프
        fig, ax = plt.subplots(figsize=(10, 4))
        low20_counts.plot(kind="bar", ax=ax)
        ax.set_xlabel("자치구", fontproperties=font_prop)
        ax.set_ylabel("하위 20% AP 개수", fontproperties=font_prop)
        ax.set_title("자치구별 이용량 하위 20% AP 개수", fontproperties=font_prop)
        ax.set_xticklabels(low20_counts.index, rotation=45, ha="right", fontproperties=font_prop)
        st.pyplot(fig)
    
    with col_right:
        st.markdown("### ⬆️ AP 저이용 Top5")
        for gu, count in low20_counts.head(5).items():
            st.markdown(f"**{gu}** — {count}개")

# ===============================
# 📍 개별 AP 지도
# ===============================

with tab6:
    st.subheader("📍 교체·유지관리 대상 공공 Wi-Fi AP 분포 (개별 AP 기준)")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        m_cluster = make_ap_cluster_map()
        components.html(m_cluster, height=450, width=MAP_WIDTH)

    with col_right:
        st.markdown("""
        ### 📊 표시 기준

        🟡 **유지관리 대상**  
        - 일부 지표에서 관리 필요  

        🔴 **교체 권장 대상**  
        - 노후·과부하·비효율적 밀집 등으로 우선 조치 필요  

        ※ 양호 AP는 시각화에서 제외
        """)
