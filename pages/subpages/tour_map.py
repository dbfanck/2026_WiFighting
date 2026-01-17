import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# ===============================
# 1. 데이터 로드
# ===============================
@st.cache_data
def load_data():
    return pd.read_csv("data/AP_data.csv")

df = load_data()

def render():
    st.subheader("🚄 관광객 Wi-Fi 지도")

    # ===============================
    # 2. 사이드바 세팅
    # ===============================

    # 라디오버튼 목록 세팅 : install_type_code 목록 추출 (중복 제거 + 정렬)
    available_types = sorted(
        df['install_type'].dropna().unique()
    )

    # 한글로 라벨링
    labels = available_types

    with st.sidebar:
        # 라디오버튼
        add_radio = st.radio("장소", labels, key="place")

    # ===============================
    # 3. 데이터 필터링
    # ===============================

    # 장소별 필터링
    filtered_df = df.loc[df["install_type"] == st.session_state.place, ["lat","lon","address"]]
    filtered_df = filtered_df.dropna(subset=["lat","lon"])

    st.sidebar.markdown("---")
    st.sidebar.write(f"📍 표시중 : {len(filtered_df):,}개")

    # ===============================
    # 4. 지도 세팅
    # ===============================

    # 장소별 아이콘 세팅
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

    icon_name, icon_color = icon_map.get(
        st.session_state.place,
        ('info-sign', 'blue')
    )

    # 지도 중심을 데이터 평균 위치로
    if len(filtered_df) > 0:
        center_lat = filtered_df['lat'].mean()
        center_lon = filtered_df['lon'].mean()
    else:
        center_lat = df['lat'].mean()
        center_lon = df['lon'].mean()

    m = folium.Map(location=[center_lat, center_lon],
                zoom_start=11,
                tiles='cartodbpositron')

    # 많은 점일 때 성능 좋게 MarkerCluster 사용
    marker_cluster = MarkerCluster().add_to(m)

    for r in filtered_df.itertuples(index=False):
        addr = r.address
        lat, lon = float(r.lat), float(r.lon)

        popup = folium.Popup(f"주소: {addr}", max_width=350)
        
        # 점(원) 하나 추가 – 색/크기는 필요하면 나중에 조건 걸어서 바꿀 수 있음
        folium.Marker(
            popup=popup,
            location=[lat, lon],
            icon=folium.Icon(
                icon=icon_name,
                color=icon_color,
                prefix='fa'
            )
        ).add_to(marker_cluster)

    # 지도 표시
    st_folium(m, width=1500, height=700, returned_objects=[])