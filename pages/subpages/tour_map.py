import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from branca.element import Element

# ===============================
# 1. 데이터 로드
# ===============================
@st.cache_data
def load_data():
    return pd.read_csv("data/AP_all_data.csv")

df = load_data()

def render():
    st.title("🚄 관광객 Wi-Fi 지도")
    
    # ===============================
    # 2. 사이드바 세팅
    # ===============================

    # 라디오버튼 목록 세팅 : install_type_code 목록 추출 (중복 제거 + 정렬)
    available_types = sorted(
        df['install_type'].dropna().unique()
    )

    # 한글로 라벨링
    labels = ["전체"] + available_types

    with st.sidebar:
        # 라디오버튼
        add_radio = st.radio("장소", labels, key="place")

    # ===============================
    # 3. 데이터 필터링
    # ===============================

    # 실제로 화면에 보여줄 df 설정 : filtered_df
    filtered_df = df.copy()

    # 장소별 필터링
    if st.session_state.place != "전체":
        filtered_df = filtered_df[
            filtered_df['install_type'] == st.session_state.place
        ]

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

    for _, row in filtered_df.iterrows():
        html = f"""
        <h4>AP 상세 정보</h4>
        <table style="width: 280px;">
        <tr><th align="left">AP ID</th><td>{row['ap_id']}</td></tr>
        <tr><th align="left">구</th><td>{row['gu']}</td></tr>
        <tr><th align="left">설치 연도</th><td>{row['install_year']}</td></tr>
        <tr><th align="left">설치유형 코드</th><td>{row['install_type_code']}</td></tr>
        <tr><th align="left">설치유형</th><td>{row['install_type']}</td></tr>
        <tr><th align="left">실내/실외</th><td>{row['indoor_outdoor']}</td></tr>
        <tr><th align="left">위도(lat)</th><td>{row['lat']:.6f}</td></tr>
        <tr><th align="left">경도(lon)</th><td>{row['lon']:.6f}</td></tr>
        <tr><th align="left">이용량(GB)</th><td>{row['usage_gb']}</td></tr>
        </table>
        """
        popup = folium.Popup(html, max_width=350)
        
        # 점(원) 하나 추가 – 색/크기는 필요하면 나중에 조건 걸어서 바꿀 수 있음
        if st.session_state.place == "전체":
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=4,
                popup=popup,
                color='blue',
                fill=True,
                fill_opacity=0.7
            ).add_to(marker_cluster)
        else:
            folium.Marker(
                popup=popup,
                location=[row['lat'], row['lon']],
                icon=folium.Icon(
                    icon=icon_name,
                    color=icon_color,
                    prefix='fa'
                )
            ).add_to(marker_cluster)

    # 지도 표시
    st_folium(m, width=1500, height=700, returned_objects=[])