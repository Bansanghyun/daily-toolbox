# 🧰 Daily Toolbox Pro

Streamlit으로 만든 현장/공학 실무용 멀티 툴킷입니다. 콘크리트 양생 분석, 엑셀 일괄 수정, 안전 관리, 단위 변환 등 여러 기능을 하나의 앱에서 제공합니다.

## 주요 기능

- ☀️ **스마트 양생 (Concrete WX)** — ACI 305R/306R 기준 콘크리트 수분 증발률 계산 및 위험도 평가
- 📝 **엑셀 일괄 수정 (Excel Batch)** — 서식과 수식을 유지한 채 여러 xlsx 파일의 텍스트를 일괄 치환
- 🛡️ **안전 관리 (Safety)** — 작업 종류별 JHA(작업위험성평가) 생성
- 🛒 **추천템 (Picks)** — 현장 필수 장비 추천
- 🚦 **호환성 판독 (Compatibility)** — 인치/mm 규격 변환
- 📐 **공학 계산 (Eng Calc)** — 볼트 토크 등 공학 계산
- 💰 **생활/금융 (Life)** — 환율, 시차 조회
- 📏 **치수 변환 (Unit)** — mm ↔ ft 변환
- 🏗️ **자재/배관 (Material)** — m³ ↔ yd³ 변환

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run converter.py
```

브라우저에서 `http://localhost:8501` 로 접속하면 앱을 사용할 수 있습니다.

## Codespaces / Dev Container

이 저장소는 `.devcontainer` 설정을 포함하고 있어 GitHub Codespaces에서 바로 실행할 수 있습니다. 컨테이너가 시작되면 의존성이 자동으로 설치되고 Streamlit 서버가 실행됩니다.

## 의존성

`requirements.txt`에 정의되어 있습니다: `streamlit`, `pandas`, `openpyxl`, `yfinance`, `requests`, `pytz`
