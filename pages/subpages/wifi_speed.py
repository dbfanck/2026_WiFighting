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
    if "show_top10_only" not in st.session_state:
        st.session_state.show_top10_only = False
    if "sort_type" not in st.session_state:
        st.session_state.sort_type = "가까운 순"

    # ===============================
    # 자치구 선택
    # ===============================
    st.subheader("📍 자치구 선택")
    gu_list = sorted(df["gu"].unique())
    selected_gu = st.selectbox("서울시 자치구", gu_list)

    df_gu = df[df["gu"] == selected_gu].copy()

    # ===============================
    # 레이아웃: 왼쪽(입력/정렬) / 오른쪽(지도)
    # ===============================
    left, right = st.columns([1, 2])

    # ---- 왼쪽: 내 위치 + 정렬 기준 + 버튼 ----
    with left:
        st.subheader("📌 내 위치 입력")

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

        # 정렬 기준
        st.subheader("🔽 정렬 기준 선택")
        st.session_state.sort_type = st.radio(
            "정렬 방식",
            ["가까운 순", "Wi-Fi 빠른 순", "가까움 + 빠름 혼합"],
            horizontal=True,
            key="sort_type_radio",
            index=["가까운 순", "Wi-Fi 빠른 순", "가까움 + 빠름 혼합"].index(
                st.session_state.sort_type
            ),
        )

        # TOP10 / 전체 토글 버튼 (rerun 제거)
        if st.session_state.show_top10_only:
            btn_label = "전체 AP 지도 보기"
        else:
            btn_label = "TOP10 지도에 표시"

        if st.button(btn_label, key="toggle_top10_btn"):
            st.session_state.show_top10_only = not st.session_state.show_top10_only
            # 🔴 여기에서 st.rerun()을 호출하지 않음


    # ---- 오른쪽: GPS + 지도 ----
    with right:
        # 브라우저 GPS
        location = streamlit_geolocation()
        if isinstance(location, dict) and location.get("latitude") is not None:
            st.session_state.user_lat = float(location["latitude"])
            st.session_state.user_lon = float(location["longitude"])
            st.success(
                f"현재 위치를 가져왔어요! "
                f"(lat: {st.session_state.user_lat:.6f}, lon: {st.session_state.user_lon:.6f})"
            )

        # ===== 거리 / 속도 계산 =====
        def calc_distance(row):
            return geodesic(
                (st.session_state.user_lat, st.session_state.user_lon),
                (row["lat"], row["lon"]),
            ).meters

        df_gu["distance_m"] = df_gu.apply(calc_distance, axis=1)
        df_gu["speed_score"] = 1 - df_gu["usage_norm"]

        sort_type = st.session_state.sort_type

        if sort_type == "가까운 순":
            df_sorted = df_gu.sort_values("distance_m")
        elif sort_type == "Wi-Fi 빠른 순":
            df_sorted = df_gu.sort_values("speed_score", ascending=False)
        else:
            df_gu["distance_score"] = 1 / (df_gu["distance_m"] + 1)
            df_gu["final_score"] = (
                0.5 * df_gu["distance_score"] + 0.5 * df_gu["speed_score"]
            )
            df_sorted = df_gu.sort_values("final_score", ascending=False)

        # TOP10 만들기 (순위 컬럼 포함)
        df_top10 = df_sorted.head(10).copy()
        df_top10.insert(0, "rank", range(1, len(df_top10) + 1))        # 실제 순위 1~10
        df_top10["rank_display"] = len(df_top10) - df_top10["rank"] + 1  # 표시용 10~1

        # ===== 지도 생성 =====
        m = folium.Map(
            location=[st.session_state.user_lat, st.session_state.user_lon],
            zoom_start=13,
            tiles="cartodbpositron",
        )

        # 내 위치 마커 (항상 고정)
        folium.Marker(
            location=[st.session_state.user_lat, st.session_state.user_lon],
            tooltip="내 위치",
            icon=folium.Icon(color="red", icon="user"),
        ).add_to(m)

        # 지도에 표시할 데이터 선택
        if st.session_state.show_top10_only:
            data_for_map = df_top10.copy()
            data_for_map["plot_lat"] = data_for_map["lat"]
            data_for_map["plot_lon"] = data_for_map["lon"]

            # 같은 좌표 살짝 벌리기
            dup_groups = (
                data_for_map.groupby(["lat", "lon"])
                .size()
                .reset_index(name="count")
            )
            data_for_map = data_for_map.merge(
                dup_groups, on=["lat", "lon"], how="left"
            )
            data_for_map["idx_in_group"] = (
                data_for_map.groupby(["lat", "lon"]).cumcount()
            )

            base_radius = 0.0001  # 약 11m
            for i in data_for_map.index:
                count = data_for_map.at[i, "count"]
                idx = data_for_map.at[i, "idx_in_group"]
                if count > 1:
                    angle = 2 * np.pi * idx / count
                    r = base_radius
                    data_for_map.at[i, "plot_lat"] += r * np.cos(angle)
                    data_for_map.at[i, "plot_lon"] += r * np.sin(angle)
        else:
            data_for_map = df_gu.copy()
            data_for_map["plot_lat"] = data_for_map["lat"]
            data_for_map["plot_lon"] = data_for_map["lon"]

        # 마커 그리기
        for _, row in data_for_map.iterrows():
            lat = row["plot_lat"]
            lon = row["plot_lon"]

            if st.session_state.show_top10_only:
                rank = int(row["rank_display"])
                html = f"""
                <div style="
                    width: 16px;
                    height: 16px;
                    border-radius: 50%;
                    background: rgba(52, 152, 219, 0.75);
                    color: #ffffff;
                    font-size: 8px;
                    font-weight: 700;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 0 8px rgba(0,0,0,0.35);
                ">
                    {rank}
                </div>
                """
                icon = folium.DivIcon(html=html)

                popup_html = f"""
                <b>표시 순위:</b> {rank}위<br>
                <b>실제 순위:</b> {int(row['rank'])}위<br>
                <b>AP ID:</b> {row['ap_id']}<br>
                <b>거리:</b> {row['distance_m']:.1f} m<br>
                <b>speed_score:</b> {row['speed_score']:.3f}
                """

                folium.Marker(
                    location=[lat, lon],
                    icon=icon,
                    tooltip=f"{rank}위 / AP {row['ap_id']}",
                    popup=popup_html,
                ).add_to(m)
            else:
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    fill=True,
                    fill_opacity=0.7,
                    popup=f"""
                    <b>AP ID:</b> {row['ap_id']}<br>
                    <b>lat:</b> {row['lat']}<br>
                    <b>lon:</b> {row['lon']}
                    """,
                    color="blue",
                ).add_to(m)

        # TOP10 모드일 때: bounds 계산에 '내 위치'도 포함
        if st.session_state.show_top10_only and len(data_for_map) > 0:
            lat_list = list(data_for_map["plot_lat"]) + [st.session_state.user_lat]
            lon_list = list(data_for_map["plot_lon"]) + [st.session_state.user_lon]

            min_lat = min(lat_list)
            max_lat = max(lat_list)
            min_lon = min(lon_list)
            max_lon = max(lon_list)

            m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]], padding=(30, 30))

        map_data = st_folium(
            m,
            height=520,
            returned_objects=["last_clicked"],
        )

    # ===============================
    # 지도 클릭 → 위경도 자동 입력
    # ===============================
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
    # 결과 테이블 (TOP10)
    # ===============================
    st.subheader("📋 AP 리스트 (상위 10개)")
    st.dataframe(
        df_top10[["rank_display", "rank", "ap_id", "speed_score", "distance_m", "lat", "lon"]]
        .rename(columns={"rank_display": "표시순위(10→1)", "rank": "실제순위(1→10)"}),
        use_container_width=True,
    )