import streamlit as st
import pandas as pd
import numpy as np
import folium
from geopy.distance import geodesic
from streamlit_folium import st_folium
from streamlit_javascript import st_javascript
from streamlit_geolocation import streamlit_geolocation


# ===============================
# 데이터 로드 (단일 CSV)
# ===============================
@st.cache_data
def load_data():
    return pd.read_csv("data/AP_data.csv")

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

    # ===============================
    # 자치구 선택
    # ===============================
    st.subheader("📍 자치구 선택")
    gu_list = sorted(df["gu"].dropna().unique())
    selected_gu = st.selectbox("서울시 자치구", gu_list)

    df_gu = df[df["gu"] == selected_gu].copy()

    # ===============================
    # 레이아웃
    # ===============================
    left, right = st.columns([1, 2])

    # ===============================
    # 좌측: 위치 입력
    # ===============================
    with left:
        st.subheader("📌 내 위치 입력")

        if st.button("📍 브라우저 위치 자동입력"):
            st.session_state.request_browser_location = True

        if st.session_state.get("request_browser_location", False):
            location = st_javascript(
                """
                new Promise((resolve) => {
                    if (!navigator.geolocation) resolve(null);
                    navigator.geolocation.getCurrentPosition(
                        pos => resolve({lat: pos.coords.latitude, lon: pos.coords.longitude}),
                        err => resolve(null)
                    );
                });
                """,
                key="browser_location",
            )

            if isinstance(location, dict):
                st.session_state.user_lat = location["lat"]
                st.session_state.user_lon = location["lon"]
                st.session_state.request_browser_location = False
                st.success("현재 위치를 불러왔어요!")

        st.session_state.user_lat = st.number_input(
            "위도", value=float(st.session_state.user_lat), format="%.6f"
        )
        st.session_state.user_lon = st.number_input(
            "경도", value=float(st.session_state.user_lon), format="%.6f"
        )

    # ===============================
    # 우측: 지도
    # ===============================
    with right:
        location = streamlit_geolocation()
        if isinstance(location, dict) and location.get("latitude"):
            st.session_state.user_lat = location["latitude"]
            st.session_state.user_lon = location["longitude"]

        m = folium.Map(
            location=[st.session_state.user_lat, st.session_state.user_lon],
            zoom_start=13,
            tiles="cartodbpositron"
        )

        folium.Marker(
            [st.session_state.user_lat, st.session_state.user_lon],
            tooltip="내 위치",
            icon=folium.Icon(color="red", icon="user"),
        ).add_to(m)

        for _, row in df_gu.iterrows():
            folium.CircleMarker(
                [row["lat"], row["lon"]],
                radius=4,
                fill=True,
                fill_opacity=0.6,
                color="blue",
            ).add_to(m)

        map_data = st_folium(m, height=520, returned_objects=["last_clicked"])

    # 지도 클릭 → 위치 반영
    clicked = map_data.get("last_clicked") if map_data else None
    if clicked:
        st.session_state.user_lat = clicked["lat"]
        st.session_state.user_lon = clicked["lng"]
        st.rerun()

    # ===============================
    # 거리 계산
    # ===============================
    df_gu["distance_m"] = df_gu.apply(
        lambda r: geodesic(
            (st.session_state.user_lat, st.session_state.user_lon),
            (r["lat"], r["lon"])
        ).meters,
        axis=1
    )

    # ===============================
    # 🔥 Wi-Fi 성능 점수 계산 (핵심)
    # ===============================
    # 가까울수록 좋음
    df_gu["distance_score"] = 1 / (df_gu["distance_m"] + 1)

    # 이용량·밀집도·노후도는 낮을수록 좋음 → (1 - norm)
    df_gu["wifi_quality_score"] = (
        0.4 * (1 - df_gu["usage_norm"]) +
        0.3 * (1 - df_gu["density_norm"]) +
        0.3 * (1 - df_gu["age_norm"])
    )

    # 최종 속도 점수
    df_gu["final_score"] = (
        0.6 * df_gu["wifi_quality_score"] +
        0.4 * df_gu["distance_score"]
    )

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
        df_sorted = df_gu.sort_values("wifi_quality_score", ascending=False)
    else:
        df_sorted = df_gu.sort_values("final_score", ascending=False)

    # ===============================
    # 결과 테이블
    # ===============================
    st.subheader("📋 AP 리스트 (상위 10개)")

    st.dataframe(
        df_sorted[
            [
                "ap_id",
                "final_score",
                "wifi_quality_score",
                "distance_m",
                "usage_norm",
                "density_norm",
                "age_norm",
            ]
        ].head(10),
        use_container_width=True,
    )
