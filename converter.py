import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math
import requests
from datetime import datetime
import pytz

# yfinance 안전 로딩
try:
    import yfinance as yf

    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

st.set_page_config(page_title="Daily Toolbox", page_icon="🧰", layout="centered")


# ==========================================
# 🕵️‍♂️ GA Code (추적 코드 유지)
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


# --- 날씨 함수 (API) ---
def get_weather_data(location):
    try:
        url = f"https://wttr.in/{location}?format=j1"
        response = requests.get(url, timeout=5)
        data = response.json()
        current = data['current_condition'][0]
        return float(current['temp_F']), float(current['humidity']), float(current['windspeedMiles']), None
    except:
        return None, None, None, "Error"


# --- 증발률 계산 (ACI 305R) ---
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

# --- 사이드바 ---
with st.sidebar:
    st.header("🌐 Language")
    lang = st.radio("Select Language", ["🇰🇷 한국어", "🇺🇸 English"])
    is_kor = lang == "🇰🇷 한국어"

    st.divider()
    st.subheader("☕ Support")
    if is_kor:
        st.caption("개발자에게 커피 한 잔 후원하기")
    else:
        st.caption("Support the developer!")

    bmc_link = "https://www.buymeacoffee.com/vvaann"
    st.markdown(
        f"""<a href="{bmc_link}" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" style="width: 100% !important;"></a>""",
        unsafe_allow_html=True)
    st.write("")

    # ▼▼▼ PayPal 주소 ▼▼▼
    paypal_url = "https://www.paypal.com/paypalme/아이디를입력하세요"
    btn_text = "💳 PayPal로 후원하기" if is_kor else "💳 Donate with PayPal"
    st.markdown(
        f"""<a href="{paypal_url}" target="_blank"><button style="background-color: #0070BA; color: white; border: none; padding: 10px; border-radius: 5px; width: 100%; font-weight: bold; cursor: pointer;">{btn_text}</button></a>""",
        unsafe_allow_html=True)

    st.divider()
    st.subheader("📧 Contact")
    st.code("shban127@gmail.com")

# --- 메인 타이틀 ---
if is_kor:
    st.title("🧰 데일리 툴박스 (Pro)")
    st.markdown("현장 전문가를 위한 **올인원 엔지니어링 킷**")
    tab_names = ["☀️ 스마트 양생", "🗣️ 소통/영어", "📐 공학 계산", "💰 생활/금융", "📏 치수 변환", "🏗️ 자재/배관", "🚦 호환성", "📋 규격표", "📧 보고서"]
else:
    st.title("🧰 The Daily Toolbox")
    st.markdown("All-in-One Engineering Kit for Professionals")
    tab_names = ["☀️ Concrete WX", "🗣️ Comm", "📐 Eng Calc", "💰 Life", "📏 Dim", "🏗️ Mat", "🚦 Comp", "📋 Charts",
                 "📧 Report"]

tabs = st.tabs(tab_names)

# =================================================
# TAB 1: ☀️ 스마트 양생 (UI 복구 + 언어 분리)
# =================================================
with tabs[0]:
    if is_kor:
        # [한국어 UI]
        st.markdown("### ☀️ 스마트 콘크리트 양생 관리")
        st.caption("ACI 305R/306R 기반 분석. 지역명을 입력하면 날씨를 자동으로 가져옵니다.")

        # 검색창 UI (V27 디자인)
        with st.container(border=True):
            col_search, col_btn = st.columns([3, 1])
            loc_input = col_search.text_input("위치 검색 (예: Atlanta, 30303)", placeholder="도시명 또는 ZIP Code")
            if col_btn.button("🔍 날씨 가져오기", use_container_width=True):
                if loc_input:
                    with st.spinner("날씨 정보를 불러오는 중..."):
                        t, h, w, err = get_weather_data(loc_input)
                        if err:
                            st.error("위치를 찾을 수 없습니다. 철자를 확인해주세요.")
                        else:
                            st.session_state.temp_val = t
                            st.session_state.humid_val = int(h)
                            st.session_state.wind_val = w
                            st.success(f"✅ 로딩 완료: {loc_input}")

            st.divider()
            # 입력창
            c1, c2, c3 = st.columns(3)
            temp_f = c1.number_input("기온 (Temp °F)", value=st.session_state.temp_val, step=1.0, format="%.1f")
            humid = c2.number_input("습도 (Humidity %)", value=st.session_state.humid_val, step=5, max_value=100)
            wind = c3.number_input("풍속 (Wind mph)", value=st.session_state.wind_val, step=1.0)

            temp_c = (temp_f - 32) * 5 / 9
            st.caption(f"🌡️ 변환 온도: {temp_c:.1f}°C")

        # 분석 및 결과 표시 (한국어)
        evap_rate = calc_evaporation_rate(temp_c, humid, wind)
        st.markdown("#### 📊 분석 결과")
        col_r1, col_r2 = st.columns([1, 1])

        with col_r1:
            st.markdown("**1. 온도 기준**")
            if temp_f < 40:
                st.error("❄️ **한중 콘크리트 (Cold Weather)**");
                st.caption("🚨 40°F 미만! 보온 양생 필수")
            elif temp_f > 90:
                st.error("🔥 **서중 콘크리트 (Hot Weather)**");
                st.caption("🚨 90°F 초과! 쿨링 대책 필요")
            else:
                st.success("✅ **적정 온도 (Good)**");
                st.caption("표준 시방 범위 내 (40°F ~ 90°F)")

        with col_r2:
            st.markdown("**2. 소성 수축 균열**")
            st.metric("수분 증발률 (lb/ft²/hr)", f"{evap_rate:.3f}")
            if evap_rate > 0.2:
                st.error("🚨 **위험 (Critical)**");
                st.caption("0.2 초과! 즉시 균열 발생 가능. 방풍막/포깅 필수.")
            elif evap_rate > 0.1:
                st.warning("⚠️ **주의 (Caution)**");
                st.caption("0.1 초과. 모니터링 강화.")
            else:
                st.success("✅ **안전 (Safe)**");
                st.caption("균열 위험 낮음.")

        with st.expander("💡 소장님을 위한 팁 (Pro Tip)"):
            st.markdown("* **Cold Weather:** 초기 동해 주의. 보온 덮개 필수.\n* **Evaporation:** 바람이 10mph만 넘어도 위험합니다.")

    else:
        # [ENGLISH UI] - Perfectly Translated
        st.markdown("### ☀️ Concrete Curing Manager")
        st.caption("Based on ACI 305R/306R. Enter location for auto-weather.")

        # Search UI (English)
        with st.container(border=True):
            col_search, col_btn = st.columns([3, 1])
            loc_input = col_search.text_input("Search Location (e.g., Atlanta, 30303)", placeholder="City or ZIP Code")
            if col_btn.button("🔍 Get Weather", use_container_width=True):
                if loc_input:
                    with st.spinner("Fetching data..."):
                        t, h, w, err = get_weather_data(loc_input)
                        if err:
                            st.error("Location not found. Check spelling.")
                        else:
                            st.session_state.temp_val = t
                            st.session_state.humid_val = int(h)
                            st.session_state.wind_val = w
                            st.success(f"✅ Loaded: {loc_input}")

            st.divider()
            # Inputs
            c1, c2, c3 = st.columns(3)
            temp_f = c1.number_input("Temp (°F)", value=st.session_state.temp_val, step=1.0, format="%.1f")
            humid = c2.number_input("Humidity (%)", value=st.session_state.humid_val, step=5, max_value=100)
            wind = c3.number_input("Wind Speed (mph)", value=st.session_state.wind_val, step=1.0)

            temp_c = (temp_f - 32) * 5 / 9
            st.caption(f"🌡️ In Celsius: {temp_c:.1f}°C")

        # Analysis Logic & Display (English)
        evap_rate = calc_evaporation_rate(temp_c, humid, wind)
        st.markdown("#### 📊 Analysis Result")
        col_r1, col_r2 = st.columns([1, 1])

        with col_r1:
            st.markdown("**1. Temperature Check**")
            if temp_f < 40:
                st.error("❄️ **Cold Weather Concrete**");
                st.caption("🚨 Below 40°F! Thermal protection required.")
            elif temp_f > 90:
                st.error("🔥 **Hot Weather Concrete**");
                st.caption("🚨 Above 90°F! Cooling measures required.")
            else:
                st.success("✅ **Good Condition**");
                st.caption("Within ACI standard range (40°F ~ 90°F).")

        with col_r2:
            st.markdown("**2. Cracking Risk**")
            st.metric("Evaporation Rate", f"{evap_rate:.3f}")
            if evap_rate > 0.2:
                st.error("🚨 **CRITICAL**");
                st.caption("Over 0.2! High risk. Windbreaks/Fogging required.")
            elif evap_rate > 0.1:
                st.warning("⚠️ **CAUTION**");
                st.caption("Over 0.1. Monitor closely.")
            else:
                st.success("✅ **SAFE**");
                st.caption("Low cracking risk.")

        with st.expander("💡 Pro Tips"):
            st.markdown(
                "* **Cold Weather:** Freezing reduces strength by 50%. Use insulation.\n* **Wind:** Wind > 10mph drastically increases evaporation.")

# =================================================
# TAB 2: 소통/영어 (언어 분리)
# =================================================
with tabs[1]:
    if is_kor:
        comm_type = st.radio("기능 선택", ["📻 무전 용어", "📖 건설 약어", "📧 이메일 템플릿"], horizontal=True)
        st.divider()
        if "무전" in comm_type:
            st.subheader("📻 필수 무전 용어")
            st.table(pd.DataFrame([
                {"용어": "10-4", "의미": "수신 양호"}, {"용어": "Copy that", "의미": "내용 이해함"},
                {"용어": "What's your 20?", "의미": "현재 위치?"}, {"용어": "Go ahead", "의미": "말해라"},
                {"용어": "Stand by", "의미": "대기하라"}
            ]))
        elif "약어" in comm_type:
            st.subheader("📖 건설 현장 약어")
            st.dataframe(pd.DataFrame([
                {"약어": "RFI", "원어": "Request for Information", "설명": "설계 질의서"},
                {"약어": "CO", "원어": "Change Order", "설명": "설계 변경"},
                {"약어": "NTP", "원어": "Notice to Proceed", "설명": "착공 지시서"},
                {"약어": "TBM", "원어": "Toolbox Meeting", "설명": "작업 전 안전 조회"}
            ]), hide_index=True, use_container_width=True)
        elif "이메일" in comm_type:
            st.subheader("📧 이메일 작성기")
            type_ = st.selectbox("상황", ["자재 지연 (Delay)", "검측 요청 (Inspection)"])
            item = st.text_input("대상 항목", "Piping")
            if st.button("생성하기"):
                if "Delay" in type_:
                    st.info(
                        f"Subject: Notice of Delay - {item}\n\nDear Manager,\nWe regret to inform you of a delay regarding **{item}**.")
                else:
                    st.success(
                        f"Subject: Inspection Request - {item}\n\nDear Manager,\nInstallation of **{item}** is complete.")
    else:
        # [ENGLISH UI]
        comm_type = st.radio("Select Tool", ["📻 Radio Terms", "📖 Acronyms", "📧 Email Templates"], horizontal=True)
        st.divider()
        if "Radio" in comm_type:
            st.subheader("📻 Radio Terms")
            st.table(pd.DataFrame([
                {"Term": "10-4", "Meaning": "Received / OK"}, {"Term": "Copy that", "Meaning": "Understood"},
                {"Term": "What's your 20?", "Meaning": "Current Location?"},
                {"Term": "Go ahead", "Meaning": "Ready to listen"},
                {"Term": "Stand by", "Meaning": "Wait"}
            ]))
        elif "Acronyms" in comm_type:
            st.subheader("📖 Acronyms")
            st.dataframe(pd.DataFrame([
                {"Abbr": "RFI", "Full": "Request for Information"}, {"Abbr": "CO", "Full": "Change Order"},
                {"Abbr": "NTP", "Full": "Notice to Proceed"}, {"Abbr": "TBM", "Full": "Toolbox Meeting"}
            ]), hide_index=True, use_container_width=True)
        elif "Email" in comm_type:
            st.subheader("📧 Email Generator")
            type_ = st.selectbox("Situation", ["Delay Notice", "Inspection Request"])
            item = st.text_input("Item / Subject", "Piping Material")
            if st.button("Generate"):
                if "Delay" in type_:
                    st.info(
                        f"Subject: Notice of Delay - {item}\n\nDear Manager,\nWe regret to inform you of a delay regarding **{item}**.")
                else:
                    st.success(
                        f"Subject: Inspection Request - {item}\n\nDear Manager,\nInstallation of **{item}** is complete.")

# =================================================
# TAB 3: 공학 계산 (언어 분리)
# =================================================
with tabs[2]:
    if is_kor:
        eng_menu = st.radio("계산기", ["📉 배관 구배", "⚡ 트레이 채움률", "🏗️ 크레인 양중"], horizontal=True)
        st.divider()
        if "구배" in eng_menu:
            st.subheader("📉 배관 구배 계산")
            c1, c2 = st.columns(2)
            l = c1.number_input("길이 (ft)", 50.0)
            s = c2.select_slider("구배 (Slope)", ["1/8\"", "1/4\"", "1/2\"", "1\""])
            val = {"1/8\"": 0.125, "1/4\"": 0.25, "1/2\"": 0.5, "1\"": 1.0}[s]
            d = l * val
            st.info(f"⬇️ **높이 차이: {d:.2f} inch ({d * 25.4:.1f} mm)**")
        elif "트레이" in eng_menu:
            st.subheader("⚡ 트레이 채움률")
            c1, c2, c3 = st.columns(3)
            w = c1.selectbox("폭 (Width)", [12, 18, 24, 30, 36])
            d = c2.selectbox("깊이 (Depth)", [4, 6])
            dia = c3.number_input("케이블 외경 (in)", 1.0)
            cnt = st.slider("가닥수", 1, 100, 20)
            r = ((math.pi * (dia / 2) ** 2) * cnt / (w * d)) * 100
            st.metric("채움률 (최대 40%)", f"{r:.1f}%")
            if r > 40:
                st.error("❌ 초과 (Overfilled)")
            else:
                st.success("✅ 양호 (Pass)")
        elif "크레인" in eng_menu:
            st.subheader("🏗️ 양중 모멘트")
            w = st.number_input("무게 (lbs)", 5000)
            r = st.number_input("반경 (ft)", 50)
            st.metric("부하 모멘트", f"{w * r:,.0f} lbs-ft")
    else:
        # [ENGLISH UI]
        eng_menu = st.radio("Select Tool", ["📉 Slope Calc", "⚡ Tray Fill", "🏗️ Crane Lift"], horizontal=True)
        st.divider()
        if "Slope" in eng_menu:
            st.subheader("📉 Slope Calculator")
            c1, c2 = st.columns(2)
            l = c1.number_input("Length (ft)", 50.0)
            s = c2.select_slider("Slope", ["1/8\"", "1/4\"", "1/2\"", "1\""])
            val = {"1/8\"": 0.125, "1/4\"": 0.25, "1/2\"": 0.5, "1\"": 1.0}[s]
            d = l * val
            st.info(f"⬇️ **Drop: {d:.2f} inch ({d * 25.4:.1f} mm)**")
        elif "Tray" in eng_menu:
            st.subheader("⚡ Tray Fill Ratio")
            c1, c2, c3 = st.columns(3)
            w = c1.selectbox("Width (in)", [12, 18, 24, 30, 36])
            d = c2.selectbox("Depth (in)", [4, 6])
            dia = c3.number_input("Cable OD (in)", 1.0)
            cnt = st.slider("Count", 1, 100, 20)
            r = ((math.pi * (dia / 2) ** 2) * cnt / (w * d)) * 100
            st.metric("Fill Ratio (Max 40%)", f"{r:.1f}%")
            if r > 40:
                st.error("❌ Overfilled")
            else:
                st.success("✅ Pass")
        elif "Crane" in eng_menu:
            st.subheader("🏗️ Load Moment")
            w = st.number_input("Weight (lbs)", 5000)
            r = st.number_input("Radius (ft)", 50)
            st.metric("Load Moment", f"{w * r:,.0f} lbs-ft")

# =================================================
# TAB 4~9: 나머지 (공통 기능도 언어 분리 적용)
# =================================================
with tabs[3]:  # 생활
    st.subheader("💱 Exchange Rate" if not is_kor else "💱 실시간 환율")
    df = get_exchange_rate()
    rate = df['Close'].iloc[-1] if df is not None else 1450.0
    c1, c2 = st.columns(2)
    c1.metric("USD/KRW", f"{rate:.1f}")
    usd = c2.number_input("USD ($)", 1000)
    c2.caption(f"≒ {int(usd * rate):,} KRW")

    st.divider()
    st.subheader("⏰ Timezone" if not is_kor else "⏰ 현장 시차")
    utc = datetime.now(pytz.utc)
    c1, c2 = st.columns(2)
    c1.info(f"🇺🇸 ET: **{utc.astimezone(pytz.timezone('US/Eastern')).strftime('%H:%M')}**")
    c2.success(f"🇰🇷 KST: **{utc.astimezone(pytz.timezone('Asia/Seoul')).strftime('%H:%M')}**")

with tabs[4]:  # 치수
    st.subheader("📏 Unit Conversion" if not is_kor else "📏 치수 변환")
    c1, c2 = st.columns(2)
    mm = c1.number_input("mm ➡️ ft-in", 1000)
    c1.code(f"{mm / 25.4 / 12:.2f} ft")
    ft = c2.number_input("ft ➡️ mm", 10)
    c2.code(f"{ft * 304.8:.0f} mm")

with tabs[5]:  # 자재
    st.subheader("🚛 Concrete Volume" if not is_kor else "🚛 콘크리트 물량")
    m3 = st.number_input("m³", 10.0)
    st.metric("yd³", f"{m3 * 1.308:.2f}")

with tabs[6]:  # 호환성
    st.subheader("🚦 Compatibility" if not is_kor else "🚦 호환성 판독")
    b = st.selectbox("Bolt/Tool", ["1/2 inch", "M12"])
    if "inch" in b:
        st.error("⚠️ Do NOT use mm tools" if not is_kor else "⚠️ mm 공구 금지")
    else:
        st.success("✅ Inch tools maybe ok" if not is_kor else "✅ inch 공구 일부 호환")

with tabs[7]:  # 규격표
    st.subheader("📋 Rebar Size" if not is_kor else "📋 철근 규격")
    st.dataframe(pd.DataFrame({"US": ["#4", "#5"], "KR": ["D13", "D16"], "mm": [12.7, 15.9]}), hide_index=True)

with tabs[8]:  # 보고서
    st.subheader("📝 Daily Report" if not is_kor else "📝 일일 보고서")
    work = st.text_input("Work" if not is_kor else "작업 내용", "Concrete Pouring")
    if st.button("Create" if not is_kor else "생성"):
        st.code(f"Date: {datetime.now().date()}\nWork: {work}\nStatus: OK")