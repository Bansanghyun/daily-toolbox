import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math
import requests
import io
import zipfile
import openpyxl
from datetime import datetime
import pytz

# yfinance 안전 로딩
try:
    import yfinance as yf

    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

# 화면 넓게 쓰기 (Layout: Wide)
st.set_page_config(page_title="Daily Toolbox Pro", page_icon="🧰", layout="wide")


# ==========================================
# 🕵️‍♂️ GA Code
# ==========================================
def inject_ga():
    GA_ID = "G-4460NPEL99"
    ga_code = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{GA_ID}', {{ 'cookie_flags': 'SameSite=None;Secure' }});
    </script>
    """
    components.html(ga_code, height=1)


inject_ga()


# --- 캐싱 함수 ---
@st.cache_data(ttl=3600)
def get_exchange_rate():
    if not HAS_YFINANCE: return None
    try:
        ticker = yf.Ticker("KRW=X")
        data = ticker.history(period="1mo", auto_adjust=True)
        return None if data.empty else data
    except:
        return None


# --- 날씨 함수 ---
def get_weather_data(location):
    try:
        url = f"https://wttr.in/{location}?format=j1"
        response = requests.get(url, timeout=5)
        data = response.json()
        current = data['current_condition'][0]
        return float(current['temp_F']), float(current['humidity']), float(current['windspeedMiles']), None
    except:
        return None, None, None, "Error"


# --- 증발률 계산 ---
def calc_evaporation_rate(tc, rh, v_mph):
    tc_f = (tc * 9 / 5) + 32
    conc_f = tc_f
    try:
        e = 5 * ((conc_f + 18) ** 2.5 - (rh / 100) * (tc_f + 18) ** 2.5) * (v_mph + 4) * (10 ** -6)
        return max(0, e)
    except:
        return 0.0


# --- 세션 초기화 ---
if 'temp_val' not in st.session_state: st.session_state.temp_val = 75.0
if 'humid_val' not in st.session_state: st.session_state.humid_val = 50
if 'wind_val' not in st.session_state: st.session_state.wind_val = 5.0
if 'excel_rows' not in st.session_state: st.session_state.excel_rows = 1

# ==========================================
# 🎨 사이드바 (메뉴 & 설정)
# ==========================================
with st.sidebar:
    st.title("🧰 Daily Toolbox")
    st.caption("Professional Engineering Kit")

    st.markdown("### 🌐 Language")
    lang = st.radio("언어 선택", ["🇰🇷 한국어", "🇺🇸 English"], label_visibility="collapsed")
    is_kor = lang == "🇰🇷 한국어"

    st.divider()

    st.markdown("### 🚀 Menu")
    menu_options = [
        "☀️ 스마트 양생 (Concrete WX)",
        "📝 엑셀 일괄 수정 (Excel Batch) 🆕",
        "🛡️ 안전 관리 (Safety)",
        "🛒 추천템 (Picks) 🔥",
        "🚦 호환성 판독 (Compatibility)",
        "📐 공학 계산 (Eng Calc)",
        "💰 생활/금융 (Life)",
        "📏 치수 변환 (Unit)",
        "🏗️ 자재/배관 (Material)"
    ]
    selected_menu = st.radio("기능 선택", menu_options, label_visibility="collapsed")

    st.divider()
    st.markdown("### ☕ Support")
    bmc_link = "https://www.buymeacoffee.com/vvaann"
    st.markdown(
        f"""<a href="{bmc_link}" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" style="width: 100% !important;"></a>""",
        unsafe_allow_html=True)
    st.caption("Contact: shban127@gmail.com")

# ==========================================
# 📺 메인 화면 로직
# ==========================================

# 1. ☀️ 스마트 양생
if "스마트 양생" in selected_menu:
    st.header("☀️ 스마트 콘크리트 양생 관리")
    st.caption("ACI 305R/306R Standard Based Curing Manager")
    col_main, col_res = st.columns([1, 1.2])
    with col_main:
        with st.container(border=True):
            st.markdown("#### 📍 현장 날씨 입력")
            col_search, col_btn = st.columns([3, 1])
            loc_input = col_search.text_input("위치 검색 (City or ZIP)", placeholder="예: Atlanta, 30303")
            if col_btn.button("🔍 검색", use_container_width=True):
                if loc_input:
                    with st.spinner("날씨 정보 수신 중..."):
                        t, h, w, err = get_weather_data(loc_input)
                        if err:
                            st.error("위치를 찾을 수 없습니다.")
                        else:
                            st.session_state.temp_val, st.session_state.humid_val, st.session_state.wind_val = t, int(
                                h), w
                            st.success(f"✅ 로딩 완료: {loc_input}")
            st.divider()
            temp_f = st.number_input("기온 (Temp °F)", value=st.session_state.temp_val, format="%.1f")
            humid = st.number_input("습도 (Humidity %)", value=st.session_state.humid_val)
            wind = st.number_input("풍속 (Wind mph)", value=st.session_state.wind_val)
    with col_res:
        evap_rate = calc_evaporation_rate((temp_f - 32) * 5 / 9, humid, wind)
        with st.container(border=True):
            st.markdown("#### 📊 분석 리포트")
            st.metric("수분 증발률", f"{evap_rate:.3f}", "lb/ft²/hr")
            if evap_rate > 0.2:
                st.error("🚨 위험 (Critical)")
            elif evap_rate > 0.1:
                st.warning("⚠️ 주의 (Caution)")
            else:
                st.success("✅ 안전 (Safe)")

# 2. 📝 엑셀 일괄 수정 (통합된 신규 기능)
elif "엑셀 일괄 수정" in selected_menu:
    st.header("📝 엑셀 서식 보존 일괄 수정")
    st.info("파일의 수식, 서식, 시트 구조를 그대로 유지하면서 특정 텍스트만 교체합니다.")

    with st.container(border=True):
        st.markdown("#### 1️⃣ 변경 규칙 설정")
        c1, c2 = st.columns([1, 4])
        if c1.button("규칙 추가 +"): st.session_state.excel_rows += 1
        if c1.button("초기화 ↺"): st.session_state.excel_rows = 1

        rules = {}
        for i in range(st.session_state.excel_rows):
            r_col1, r_col2 = st.columns(2)
            old_t = r_col1.text_input(f"찾을 내용 {i + 1}", key=f"ot_{i}")
            new_t = r_col2.text_input(f"바꿀 내용 {i + 1}", key=f"nt_{i}")
            if old_t: rules[old_t] = new_t

    uploaded_files = st.file_uploader("#### 2️⃣ 엑셀 파일 업로드 (xlsx 여러 개 가능)", type="xlsx", accept_multiple_files=True)

    if uploaded_files and rules:
        if st.button("🚀 일괄 수정 후 압축파일 생성", use_container_width=True):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                progress_text = st.empty()
                progress_bar = st.progress(0)

                for idx, file in enumerate(uploaded_files):
                    progress_text.text(f"처리 중: {file.name} ({idx + 1}/{len(uploaded_files)})")
                    wb = openpyxl.load_workbook(file, data_only=False)
                    for sheet in wb.worksheets:
                        for row in sheet.iter_rows():
                            for cell in row:
                                if cell.value and isinstance(cell.value, str):
                                    v = cell.value
                                    for o, n in rules.items():
                                        if o in v: v = v.replace(o, n)
                                    cell.value = v

                    output = io.BytesIO()
                    wb.save(output)
                    zip_file.writestr(file.name, output.getvalue())
                    progress_bar.progress((idx + 1) / len(uploaded_files))

                progress_text.text("✅ 모든 작업 완료!")

            st.download_button(
                label="📥 수정된 파일들(ZIP) 다운로드",
                data=zip_buffer.getvalue(),
                file_name=f"Fixed_Excels_{datetime.now().strftime('%m%d_%H%M')}.zip",
                mime="application/zip",
                use_container_width=True
            )

# 3. 🛡️ 안전 관리
elif "안전" in selected_menu:
    st.header("🛡️ 안전 관리 (Safety Manager)")
    tab1, tab2 = st.tabs(["📋 JHA 생성기", "🛑 치명적 위험 점검"])
    with tab1:
        work_type = st.radio("작업 종류", ["용접/절단", "고소 작업", "중량물 인양", "굴착 작업"], horizontal=True)
        jha_db = {
            "용접/절단": ("화재, 폭발, 흄", "1. 화기허가서 2. 소화기 비치 3. 불티 방지포"),
            "고소 작업": ("추락, 낙하", "1. 100% 체결 2. 리프트 점검 3. 하부 통제"),
            "중량물 인양": ("낙하, 협착", "1. 인양반경 통제 2. 슬링 점검 3. 유도로프"),
            "굴착 작업": ("붕괴, 매설물", "1. 811 신고 2. 흙막이 설치 3. 2ft 이격")
        }
        h, c = jha_db[work_type]
        st.warning(f"**위험 요인:** {h}");
        st.success(f"**안전 대책:** {c}")

# 4. 🛒 추천템
elif "추천템" in selected_menu:
    st.header("🛒 PM's Pick: 현장 필구템")
    c1, c2, c3, c4 = st.columns(4)
    items = [
        ("🥾 안전화", "Timberland PRO", "https://amzn.to/3YkSN1g"),
        ("👓 고글", "DeWalt Anti-Fog", "https://amzn.to/3LgnNMS"),
        ("📏 레이저", "Klein Tools", "https://amzn.to/4smcR0J"),
        ("🧰 공구세트", "DeWalt 247pcs", "https://amzn.to/3YQyn02")
    ]
    for col, (name, desc, link) in zip([c1, c2, c3, c4], items):
        with col.container(border=True):
            st.markdown(f"**{name}**\n\n{desc}")
            st.link_button("최저가 보기", link, use_container_width=True)

# 5. 🚦 호환성
elif "호환" in selected_menu:
    st.header("🚦 호환성 판독")
    inch_size = st.selectbox("인치 규격", ["5/16\"", "1/2\"", "3/4\"", "1\""])
    db = {"5/16\"": "8mm (✅)", "1/2\"": "13mm (✅)", "3/4\"": "19mm (✅)", "1\"": "25mm (❌)"}
    st.metric("대체 mm 공구", db[inch_size])

# 6. 📐 공학 계산
elif "공학" in selected_menu:
    st.header("📐 공학 계산기")
    calc_type = st.tabs(["🔧 볼트 토크", "📉 배관 구배", "⚡ 트레이"])
    with calc_type[0]:
        sz = st.selectbox("볼트", ["1/2", "3/4", "1"])
        st.write(f"권장 토크: {90 if sz == '1/2' else 320 if sz == '3/4' else 750} ft-lbs")

# 7. 💰 생활/금융
elif "생활" in selected_menu:
    st.header("💰 생활 & 금융")
    c1, c2 = st.columns(2)
    with c1:
        rate = 1450.0
        df = get_exchange_rate()
        if df is not None: rate = df['Close'].iloc[-1]
        st.metric("USD/KRW", f"{rate:.1f} 원")
    with c2:
        tz_e = pytz.timezone('US/Eastern');
        tz_k = pytz.timezone('Asia/Seoul')
        st.metric("🇺🇸 미국 동부", datetime.now(tz_e).strftime('%I:%M %p'))

# 8. 📏 치수 변환
elif "치수" in selected_menu:
    st.header("📏 치수 변환")
    mm = st.number_input("mm ➡️ ft", value=1000)
    st.write(f"{mm / 25.4 / 12:.2f} ft")

# 9. 🏗️ 자재/배관
elif "자재" in selected_menu:
    st.header("🏗️ 자재/배관")
    m3 = st.number_input("m³ ➡️ yd³", value=10.0)
    st.metric("야드", f"{m3 * 1.308:.2f}")