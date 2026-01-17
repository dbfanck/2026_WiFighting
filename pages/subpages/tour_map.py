import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

@st.cache_data
def load_data():
    return pd.read_csv("data/AP_data.csv")

df = load_data()

icon_map = {
    '주요거리': ('road', 'blue'),
    '전통시장': ('shopping-cart', 'green'),
    '공원(하천)': ('tree', 'darkgreen'),
    '문화관광': ('camera', 'purple'),
    '버스정류소': ('bus', 'red'),
    '복지시설': ('heart', 'pink'),
    '공공시설': ('building', 'gray'),
    '기타': ('info-sign', 'orange')
}

def render():
    st.subheader("🚄 관광객 Wi-Fi 지도")

    available_types = sorted(df["install_type"].dropna().unique())
    if not available_types:
        st.warning("install_type 데이터가 없습니다.")
        return

    # ✅ 초기값 보장 (처음 실행 대비)
    if "place" not in st.session_state:
        st.session_state.place = available_types[0]

    left, right = st.columns([1, 2])

    # ---- 왼쪽: 필터 UI ----
    with left:
        place = st.radio("장소", available_types, key="place")
        # place는 st.session_state.place와 동일

    # ---- 데이터 필터링(라디오 이후) ----
    filtered_df = df.loc[df["install_type"] == place, ["lat", "lon", "address"]].dropna(subset=["lat", "lon"])

    with left:
        st.write(f"📍 표시중 : {len(filtered_df):,}개")

    # ---- 지도 생성 ----
    icon_name, icon_color = icon_map.get(place, ("info-sign", "blue"))

    if len(filtered_df) > 0:
        center_lat = float(filtered_df["lat"].mean())
        center_lon = float(filtered_df["lon"].mean())
    else:
        center_lat = float(df["lat"].mean())
        center_lon = float(df["lon"].mean())

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles="cartodbpositron",
    )

    marker_cluster = MarkerCluster().add_to(m)

    for r in filtered_df.itertuples(index=False):
        popup = folium.Popup(f"주소: {r.address}", max_width=350)
        folium.Marker(
            location=[float(r.lat), float(r.lon)],
            popup=popup,
            icon=folium.Icon(icon=icon_name, color=icon_color, prefix="fa"),
        ).add_to(marker_cluster)

    with right:
        st_folium(m, width=1500, height=700, returned_objects=[])
