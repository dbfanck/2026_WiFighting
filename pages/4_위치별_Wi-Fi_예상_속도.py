import streamlit as st
import pandas as pd
import numpy as np
import folium
from geopy.distance import geodesic
from streamlit_folium import st_folium
from streamlit_javascript import st_javascript


# ===============================
# 페이지 설정
# ===============================
st.set_page_config(
    page_title="위치별 Wi-Fi 예상 속도",
    page_icon="📶",
    layout="wide"
)

st.title("📶 위치별 Wi-Fi 예상 속도 분석")

# ===============================
# 세션 상태 초기화
# ===============================
if "user_lat" not in st.session_state:
    st.session_state.user_lat = 37.5665
if "user_lon" not in st.session_state:
    st.session_state.user_lon = 126.9780
if "use_browser_location" not in st.session_state:
    st.session_state.use_browser_location = False

# ===============================
# 데이터 로드
# ===============================
@st.cache_data
def load_data():
    return pd.read_csv("data/공공와이파이_최종데이터.csv")

df = load_data()

# ===============================
# 자치구 선택
# ===============================
st.subheader("📍 자치구 선택")
gu_list = sorted(df["gu"].unique())
selected_gu = st.selectbox("서울시 자치구", gu_list)
df_gu = df[df["gu"] == selected_gu].copy()

# ===============================
# 레이아웃: 좌(입력) / 우(지도)
# ===============================
left, right = st.columns([1, 2])

with left:
    st.subheader("📌 내 위치 입력")

    # 1️⃣ 버튼은 상태만 바꿈
    if st.button("📍 브라우저 위치 자동입력"):
        st.session_state.request_browser_location = True

    # 2️⃣ JS는 상태가 켜져 있으면 항상 실행
    if st.session_state.get("request_browser_location", False):
        location = st_javascript("""
            new Promise((resolve) => {
                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        resolve({
                            lat: pos.coords.latitude,
                            lon: pos.coords.longitude
                        });
                    },
                    (err) => {
                        resolve(null);
                    }
                );
            })
        """)

        if location:
            st.session_state.user_lat = location["lat"]
            st.session_state.user_lon = location["lon"]
            st.session_state.request_browser_location = False
            st.rerun()

    # 3️⃣ 수동 입력
    st.session_state.user_lat = st.number_input(
        "위도",
        value=st.session_state.user_lat,
        format="%.6f"
    )
    st.session_state.user_lon = st.number_input(
        "경도",
        value=st.session_state.user_lon,
        format="%.6f"
    )

    st.caption("👉 지도 클릭 · AP 마커 클릭 · 브라우저 위치 자동입력 지원")





# ===============================
# 지도 생성
# ===============================
m = folium.Map(
    location=[st.session_state.user_lat, st.session_state.user_lon],
    zoom_start=13,
    tiles="cartodbpositron"
)

# 사용자 위치 마커
folium.Marker(
    location=[st.session_state.user_lat, st.session_state.user_lon],
    tooltip="내 위치",
    icon=folium.Icon(color="red", icon="user")
).add_to(m)

# AP 마커 표시
for _, row in df_gu.iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=5,
        fill=True,
        fill_opacity=0.7,
        popup=f"""
        <b>AP ID:</b> {row['ap_id']}<br>
        <b>lat:</b> {row['lat']}<br>
        <b>lon:</b> {row['lon']}
        """,
        color="blue"
    ).add_to(m)

# ===============================
# 지도 렌더링 + 클릭 이벤트
# ===============================
with right:
    map_data = st_folium(
        m,
        height=520,
        returned_objects=["last_clicked"]
    )

# 지도 클릭 → 위경도 자동 입력
clicked = map_data.get("last_clicked") if map_data else None
if clicked:
    if (
        clicked["lat"] != st.session_state.user_lat
        or clicked["lng"] != st.session_state.user_lon
    ):
        st.session_state.user_lat = clicked["lat"]
        st.session_state.user_lon = clicked["lng"]
        st.rerun()

# ===============================
# 거리 계산
# ===============================
def calc_distance(row):
    return geodesic(
        (st.session_state.user_lat, st.session_state.user_lon),
        (row["lat"], row["lon"])
    ).meters

df_gu["distance_m"] = df_gu.apply(calc_distance, axis=1)

# ===============================
# Wi-Fi 속도 점수
# ===============================
df_gu["speed_score"] = 1 - df_gu["usage_norm"]

# ===============================
# 정렬 기준
# ===============================
st.subheader("🔽 정렬 기준 선택")
sort_type = st.radio(
    "정렬 방식",
    ["가까운 순", "Wi-Fi 빠른 순", "가까움 + 빠름 혼합"],
    horizontal=True
)

if sort_type == "가까운 순":
    df_sorted = df_gu.sort_values("distance_m")

elif sort_type == "Wi-Fi 빠른 순":
    df_sorted = df_gu.sort_values("speed_score", ascending=False)

else:
    df_gu["distance_score"] = 1 / (df_gu["distance_m"] + 1)
    df_gu["final_score"] = (
        0.5 * df_gu["distance_score"] +
        0.5 * df_gu["speed_score"]
    )
    df_sorted = df_gu.sort_values("final_score", ascending=False)

# ===============================
# 결과 테이블
# ===============================
st.subheader("📋 AP 리스트 (상위 20개)")

st.dataframe(
    df_sorted[["ap_id", "speed_score", "distance_m", "lat", "lon"]].head(20),
    use_container_width=True
)
