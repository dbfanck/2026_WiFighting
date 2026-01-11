import streamlit as st
import pandas as pd
from geopy.distance import geodesic

# ===============================
# 페이지 설정
# ===============================
st.set_page_config(
    page_title="위치별 Wi-Fi 예상 속도",
    page_icon="⚡",
    layout="wide"
)

st.title("📶 위치별 Wi-Fi 예상 속도 분석")

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
# 2. 자치구 선택
# ===============================
st.subheader("📍 자치구 선택")

gu_list = sorted(df["gu"].unique())
selected_gu = st.selectbox("서울시 자치구", gu_list)

df_gu = df[df["gu"] == selected_gu].copy()

# ===============================
# 3. 사용자 위치 입력
# ===============================
st.subheader("📌 내 위치 입력")

col1, col2 = st.columns(2)
with col1:
    user_lat = st.number_input("위도", value=37.5665, format="%.6f")
with col2:
    user_lon = st.number_input("경도", value=126.9780, format="%.6f")

# ===============================
# 4. 거리 계산
# ===============================
def calc_distance(row):
    return geodesic(
        (user_lat, user_lon),
        (row["lat"], row["lon"])
    ).meters

df_gu["distance_m"] = df_gu.apply(calc_distance, axis=1)

# ===============================
# 5. Wi-Fi 예상 속도 점수
# (이용량이 높을수록 느리다고 가정)
# ===============================
df_gu["speed_score"] = 1 - df_gu["usage_norm"]

# ===============================
# 6. 정렬 기준 선택
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
    # 거리 + 속도 혼합 점수
    df_gu["distance_score"] = 1 / (df_gu["distance_m"] + 1)
    df_gu["final_score"] = (
        0.5 * df_gu["distance_score"] +
        0.5 * df_gu["speed_score"]
    )
    df_sorted = df_gu.sort_values("final_score", ascending=False)

# ===============================
# 7. 결과 테이블 출력
# ===============================
st.subheader("📋 AP 리스트 (상위 20개)")

st.dataframe(
    df_sorted[
        ["ap_id", "speed_score", "distance_m", "lat", "lon"]
    ].head(20),
    use_container_width=True
)
