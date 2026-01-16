import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium  

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

st.set_page_config(
    page_title="지도",
    page_icon="🗺️",
    layout="wide",   # 왼쪽 패널 + 오른쪽 지도 넓게 쓰기
)

# -----------------------------
# 0) 세션 상태 초기화
# -----------------------------
if "mode" not in st.session_state:
    st.session_state.mode = "overview"     # "overview" or "detail"
if "selected_gu" not in st.session_state:
    st.session_state.selected_gu = None

# 제목 + 새로고침 버튼을 한 줄에 배치
title_col, button_col = st.columns([6, 1])

with title_col:
    icon("🗺️")
    st.title("지도")

with button_col:
    if st.button("↻ 다른 구 선택하기", help="지도 초기화"):
        st.session_state.mode = "overview"
        st.session_state.selected_gu = None
        st.rerun()

# -----------------------------
# 1) 데이터 불러오기 (원본은 df_all)
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/AP_all_data.csv")

df_all = load_data()

# ap_id 문자열 통일
df_all["ap_id"] = (
    df_all["ap_id"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
)

# =====================================================================
# ① 개요 모드: 자치구별 AP 개수만 보여주는 모드
# =====================================================================
if st.session_state.mode == "overview":
    # 구별 중심좌표 + AP 개수
    gu_stats = (
        df_all.groupby("gu")
        .agg(
            lat=("lat", "mean"),
            lon=("lon", "mean"),
            ap_count=("ap_id", "count")
        )
        .reset_index()
    )

    # ----- AP 개수에 따라 색 단계 (초록-노랑-빨강) + 구간 내 밝기 조절 -----
    c_min = gu_stats["ap_count"].min()
    c_max = gu_stats["ap_count"].max()

    # 하위 / 중간 / 상위 1/3 지점
    q1 = gu_stats["ap_count"].quantile(1/3)
    q2 = gu_stats["ap_count"].quantile(2/3)

    def _blend_with_white(hex_color, t):
        """hex_color를 흰색과 t(0~1) 비율로 섞어서 더 밝게"""
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # t가 클수록 더 흰색에 가까워지게
        r = int(r + (255 - r) * (1-t))
        g = int(g + (255 - g) * (1-t))
        b = int(b + (255 - b) * (1-t))

        return f"#{r:02X}{g:02X}{b:02X}"

    def count_to_color(count):
        # 1) 어느 구간(초/중/상)에 속하는지 결정
        if count <= q1:
            base = "#2E7D32"   # green (low 구간 기본색)
            band_min, band_max = c_min, q1
        elif count <= q2:
            base = "#F9A825"   # yellow (mid 구간 기본색)
            band_min, band_max = q1, q2
        else:
            base = "#C62828"   # red (high 구간 기본색)
            band_min, band_max = q2, c_max

        # 2) 해당 구간 내부에서 최소~최대 기준으로 0~1 정규화
        if band_max == band_min:
            t_local = 0.0
        else:
            t_local = (count - band_min) / (band_max - band_min)  # 0~1

        # 3) t_local이 클수록 더 밝게 (0.2 ~ 0.8 사이로 제한)
        blend_ratio = 0.2 + 0.6 * t_local

        return _blend_with_white(base, blend_ratio)

    center_lat = df_all["lat"].mean()
    center_lon = df_all["lon"].mean()

    # 지도 생성
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles="cartodbpositron",
    )

    # 각 구마다 동그란 숫자 마커 (구 이름은 표시 X, 숫자만)
    for _, row in gu_stats.iterrows():
        gu_name = row["gu"]
        count = int(row["ap_count"])
        color = count_to_color(count)

        html = f"""
        <div style="
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: {color}E6;
            backdrop-filter: blur(2px);
            color: #333333;
            font-size: 14px;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow:
                0 4px 10px rgba(0, 0, 0, 0.35),  
                inset 0 2px 4px rgba(255, 255, 255, 0.25);
        ">
            {count}
        </div>
        """
        icon_div = folium.DivIcon(html=html)

        folium.Marker(
            location=[row["lat"], row["lon"]],
            icon=icon_div,
            popup=gu_name,                    # ★ 클릭 시 구 이름이 넘어감
            tooltip=f"{gu_name} (AP {count}개)",
        ).add_to(m)

    # 개요 모드: 왼쪽은 안내만, 오른쪽에 지도
    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.subheader("AP 상세 카드")
        st.write("먼저 오른쪽 지도에서 **자치구를 선택**해 주세요.")

    with right_col:
        map_data = st_folium(m, width=900, height=700)

    # 구 클릭 감지 → detail 모드로 전환
    if map_data is not None:
        gu_clicked = map_data.get("last_object_clicked_popup", None)
        if gu_clicked is not None:
            st.session_state.selected_gu = str(gu_clicked)
            st.session_state.mode = "detail"
            st.rerun()

# =====================================================================
# ② 상세 모드: 선택한 구의 AP만 보여주는 모드
# =====================================================================
else:
    selected_gu = st.session_state.selected_gu

    if selected_gu is None:
        # 혹시 모드만 detail이고 구가 없다면 강제 초기화
        st.session_state.mode = "overview"
        st.rerun()

    st.markdown(f"### 2단계: `{selected_gu}` AP 상세 보기")

    # 이 구의 AP만 사용
    df = df_all[df_all["gu"] == selected_gu].copy()

    if df.empty:
        st.warning(f"{selected_gu} 구에는 AP 데이터가 없습니다.")
    else:
        center_lat = df["lat"].mean()
        center_lon = df["lon"].mean()

        # 지도 생성
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles="cartodbpositron",
        )

        marker_cluster = MarkerCluster().add_to(m)

        for _, row in df.iterrows():
            apid = (
                str(row["ap_id"])
                .strip()
                .replace(".0", "")
            )
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=4,
                popup=apid,      # ★ 클릭 시 AP ID가 넘어감
                tooltip=apid,
                color="blue",
                fill=True,
                fill_opacity=0.7,
            ).add_to(marker_cluster)

        # 레이아웃: 왼쪽 카드, 오른쪽 지도
        left_col, right_col = st.columns([1, 2])

        with right_col:
            map_data = st_folium(m, width=900, height=700)

        with left_col:
            st.subheader("AP 상세 카드")
            st.caption(f"선택한 구: {selected_gu} (AP {len(df)}개)")

            default_msg = "지도 위 AP 점을 클릭하면 이곳에 상세 정보가 표시됩니다."

            if map_data is None:
                st.write(default_msg)
            else:
                ap_id_clicked = map_data.get("last_object_clicked_popup", None)

                if ap_id_clicked is None:
                    st.write(default_msg)
                else:
                    ap_id_clicked = (
                        str(ap_id_clicked)
                        .strip()
                        .replace(".0", "")
                    )

                    # 선택한 구 안에서 ap_id로 검색
                    row_sel = df[df["ap_id"] == ap_id_clicked]

                    if row_sel.empty:
                        st.write("선택한 AP 정보를 찾을 수 없습니다.")
                        st.write(f"(ap_id: {ap_id_clicked})")
                    else:
                        row = row_sel.iloc[0]

                        st.markdown(f"### AP ID: `{row['ap_id']}`")
                        st.markdown("---")
                        st.markdown(f"**구:** {row['gu']}")
                        st.markdown(f"**설치 연도:** {row['install_year']}")
                        st.markdown(f"**설치유형 코드:** {row['install_type_code']}")
                        st.markdown(f"**설치유형:** {row['install_type']}")
                        st.markdown(f"**실내/실외:** {row['indoor_outdoor']}")
                        st.markdown(f"**위도(lat):** {row['lat']:.6f}")
                        st.markdown(f"**경도(lon):** {row['lon']:.6f}")
                        st.markdown(f"**이용량(GB):** {row['usage_gb']}")
