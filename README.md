# 2026_WiFighting

## 페이지 링크
https://wifighting-2026.streamlit.app/

## 🧭 프로젝트 개요
[광운대학교 파이썬 SW 활용 경진대회]

공공 와이파이 데이터를 기반으로
와이파이 밀집도 및 노후화 현황을 분석하고<br>
이를 바탕으로 정책적 시사점 및 개선 방향을 제시하는 프로젝트입니다.

## 🛠️ 개발 환경
- Python: 3.9 ~ 3.13
- OS: Windows / macOS / Linux

## 🔧 설치
1. 저장소 클론
```bash
git clone https://github.com/dbfanck/2026_WiFighting.git
cd 2026_WiFighting
```
2. 가상환경 생성 및 활성화 (권장)
- Windows (PowerShell)
```bash
python -m venv venv
.\venv\Scripts\Activate
```
- macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```
3. 패키지 설치
```bash
pip install -r requirements.txt
```
## ▶️ 실행 방법 (종료는 Ctrl+C)
```bash
streamlit run app.py
```
## 📁 프로젝트 구조
```
2026_WiFighting/
├─ data/ # 데이터
├─ fonts/ # 폰트
├─ images/ # 이미지
├─ pages/
│  ├─ 1_메인_대시보드.py # 메인 화면
│  ├─ 2_AP_현황_대시보드.py # 전체 AP 관련 시각화
│  ├─ 3_AP_상세_지도.py # AP별 상세 지도
│  ├─ 4_목적.py # 프로젝트 목적
│  ├─ 5_기대효과.py # 프로젝트 기대효과
│  ├─ 6_구별_정책_의사결정_시나리오.py # 구별 AP 정책
│  ├─ 7_서비스_확장_구조.py # 서비스 확장 구조
│  └─ subpages/
│     ├─ tour_map.py # 서비스 확장 구조 - 관광 지도
│     └─ wifi_speed.py # 서비스 확장 구조 - 와이파이 속도 예측
├─ app.py # 메인 앱
├─ requirements.txt
└─ README.md
```