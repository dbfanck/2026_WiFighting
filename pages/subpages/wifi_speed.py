import streamlit as st
import pandas as pd
import numpy as np
import folium
from geopy.distance import geodesic
from streamlit_folium import st_folium
from streamlit_javascript import st_javascript
from streamlit_geolocation import streamlit_geolocation

# ===============================
# 데이터 로드
# ===============================
@st.cache_data
def load_data():
    return pd.read_csv("data/공공와이파이_최종데이터.csv")

df = load_data()

def render():
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

        # 위도/경도 기본값 (처음 접속 시 한 번만 세팅)
        if "user_lat" not in st.session_state:
            st.session_state.user_lat = 37.5665      # 서울 시청 근처
        if "user_lon" not in st.session_state:
            st.session_state.user_lon = 126.9780

        # 1. 버튼: 위치 요청 플래그만 켜기
        if st.button("📍 브라우저 위치 자동입력", key="btn_browser_location"):
            st.session_state.request_browser_location = True

        # 2. 플래그가 켜져 있으면 JS로 브라우저 위치 요청
        if st.session_state.get("request_browser_location", False):
            location = st_javascript(
                """
                new Promise((resolve) => {
                    if (!navigator.geolocation) {
                        resolve(null);
                        return;
                    }
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
                });
                """,
                key="get_browser_location",
            )

            # 정상적으로 위치가 딕셔너리로 들어온 경우
            if isinstance(location, dict) and "lat" in location and "lon" in location:
                st.session_state.user_lat = float(location["lat"])
                st.session_state.user_lon = float(location["lon"])
                st.session_state.request_browser_location = False
                st.success(
                    f"현재 위치를 가져왔어요! "
                    f"(lat: {st.session_state.user_lat:.6f}, lon: {st.session_state.user_lon:.6f})"
                )
            elif location is None:
                st.session_state.request_browser_location = False
                st.warning("브라우저에서 위치 권한을 허용해야 자동입력이 가능합니다 🙏")
            # location이 0 같은 값일 땐 다음 rerun에서 다시 들어오게 두면 됨

        # 3. 수동 입력 (key 꼭 지정해서 중복 방지)
        st.session_state.user_lat = st.number_input(
            "위도",
            key="user_lat_input",
            value=float(st.session_state.user_lat),
            format="%.6f",
        )
        st.session_state.user_lon = st.number_input(
            "경도",
            key="user_lon_input",
            value=float(st.session_state.user_lon),
            format="%.6f",
        )

        st.caption("👉 지도 클릭 · AP 마커 클릭 · 브라우저 위치 자동입력 지원")

    with right:

        # 1) 브라우저 GPS로 내 위치 가져오기
        #    (버튼 + 권한 요청까지 이 함수가 알아서 해줌)
        location = streamlit_geolocation()

        # 위치가 정상적으로 들어온 경우 세션에 반영
        if isinstance(location, dict) and location.get("latitude") is not None:
            st.session_state.user_lat = float(location["latitude"])
            st.session_state.user_lon = float(location["longitude"])
            st.success(
                f"현재 위치를 가져왔어요! "
                f"(lat: {st.session_state.user_lat:.6f}, lon: {st.session_state.user_lon:.6f})"
            )

        # ===============================
        # 지도 생성 (항상 최신 user_lat / user_lon 사용)
        # ===============================
        m = folium.Map(
            location=[st.session_state.user_lat, st.session_state.user_lon],
            zoom_start=13,
            tiles="cartodbpositron"
        )

        # 내 위치 마커 (빨간색)
        folium.Marker(
            location=[st.session_state.user_lat, st.session_state.user_lon],
            tooltip="내 위치",
            icon=folium.Icon(color="red", icon="user")
        ).add_to(m)

        # AP 마커 표시 (기존 코드 그대로)
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

        # 지도 렌더링
        map_data = st_folium(
            m,
            height=520,
            returned_objects=["last_clicked"]
        )

    # 지도 클릭 → 위경도 자동 입력 (이 부분은 그대로 유지)
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
    st.subheader("📋 AP 리스트 (상위 10개)")

    st.dataframe(
        df_sorted[["ap_id", "speed_score", "distance_m", "lat", "lon"]].head(10),
        use_container_width=True
    )
