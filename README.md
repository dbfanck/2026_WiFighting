# 2026_WiFighting

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
├─ pages/
│  ├─ 1_메인_대시보드.py # 메인 화면
│  ├─ 2_전체_AP_수.py # 전체 AP 수 & 데이터 시각화
│  ├─ 3_지도.py # 지도 페이지
│  ├─ 4_위치별_Wi-Fi_예상_속도.py # 위치별 속도 예상
│  └─ 5_정책_의사_결정.py # 정책 관련 페이지
│
├─ app.py # 메인 앱
├─ requirements.txt
└─ README.md
```

## 🌱 Git 브랜치 네이밍 규칙
다음과 같은 네이밍 규칙 사용
```
<type>/<description>
```

**브랜치 타입**
| 타입         | 용도         |
| ---------- | ---------- |
| `feature`  | 새로운 기능 개발  |
| `fix`      | 버그 수정      |
| `refactor` | 코드 구조 개선   |
| `docs`     | 문서 작성 및 수정 |
