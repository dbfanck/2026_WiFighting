import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

st.set_page_config(
    page_title="지도",
    page_icon="🗺️",
)

st.title("🗺️ 지도")

# ===============================
# 1. 데이터 로드
# ===============================
@st.cache_data
def load_data():
    # CSV가 app.py와 같은 위치에 있으면 그대로 사용
    # 만약 data/ 폴더 안에 있으면 "data/공공와이파이_최종데이터.csv" 로 수정
    return pd.read_csv("data/공공와이파이_최종데이터.csv")

df = load_data()

# st.write(df.head())

# ===============================
# 2. 지도 세팅
# ===============================

# 지도 중심을 데이터 평균 위치로
center_lat = df['lat'].mean()
center_lon = df['lon'].mean()

m = folium.Map(location=[center_lat, center_lon],
               zoom_start=11,
               tiles='cartodbpositron')

# 많은 점일 때 성능 좋게 MarkerCluster 사용
marker_cluster = MarkerCluster().add_to(m)

for _, row in df.iterrows():
    # 점(원) 하나 추가 – 색/크기는 필요하면 나중에 조건 걸어서 바꿀 수 있음
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=4,
        color='blue',
        fill=True,
        fill_opacity=0.7
    ).add_to(marker_cluster)

# ===============================
# 3. 지도 표시
# ===============================
st_folium(m, width=1500, height=700, returned_objects=[])