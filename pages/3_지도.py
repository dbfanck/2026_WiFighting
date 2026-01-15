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

# ===============================
# 2. 사이드바 세팅
# ===============================

# 체크박스 버튼이 바뀔 시, 장소별 보기는 설정 해제
def on_check_change():
    if st.session_state.low20:
        st.session_state.place = "전체"

# 라디오 버튼이 바뀔 시, 하위 20% 보기는 설정 해제
def on_radio_change():
    if st.session_state.place != "전체":
        st.session_state.low20 = False

# 라디오버튼 목록 세팅 : install_type_code 목록 추출 (중복 제거 + 정렬)
available_codes = sorted(df['install_type_code'].dropna().unique().astype(int))

# 코드 - 한글
codes_to_labels = {
    1: '주요거리', 2: '전통시장', 3: '공원(하천)', 4: '문화관광',
    5: '버스정류소', 6: '복지시설', 7: '공공시설', 9: '기타'
}

# 한글로 라벨링
labels = ["전체"] + [codes_to_labels.get(code, f"미정({code})") for code in available_codes]

with st.sidebar:
    # 체크박스
    st.write("사용량")
    add_checkbox = st.checkbox('하위 20% 보기', key="low20", on_change=on_check_change)

    # 라디오버튼
    add_radio = st.radio("장소", labels, key="place", on_change=on_radio_change)

# ===============================
# 3. 데이터 필터링
# ===============================

# 실제로 화면에 보여줄 df 설정 : filtered_df
filtered_df = df.copy()

# 사용량 하위 20%만 선택
if st.session_state.low20:
    threshold_20 = df['usage_norm'].quantile(0.2)
    filtered_df = filtered_df[filtered_df['usage_norm'] <= threshold_20]

# 장소별 필터링
if st.session_state.place != "전체":
    code = [k for k, v in codes_to_labels.items() if v == st.session_state.place][0]
    filtered_df = filtered_df[filtered_df['install_type_code'] == code]

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
    # 점(원) 하나 추가 – 색/크기는 필요하면 나중에 조건 걸어서 바꿀 수 있음
    if st.session_state.place == "전체":
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=4,
            color='blue',
            fill=True,
            fill_opacity=0.7
        ).add_to(marker_cluster)
    else:
        folium.Marker(
            location=[row['lat'], row['lon']],
            icon=folium.Icon(
                icon=icon_name,
                color=icon_color,
                prefix='fa'
            )
        ).add_to(marker_cluster)

# 지도 표시
st_folium(m, width=1500, height=700, returned_objects=[])