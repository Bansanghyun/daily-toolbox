import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math
import requests  # 👈 날씨 가져오는 도구
from datetime import datetime
import pytz

# yfinance 안전 로딩
try:
    import yfinance as yf

    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

st.set_page_config(page_title="데일리 툴박스", page_icon="🧰", layout="centered")


# ==========================================
# 🕵️‍♂️ 구글 애널리틱스 (V26 동일)
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


# --- 🌤️ 날씨 가져오기 함수 (wttr.in 사용) ---
def get_weather_data(location):
    try:
        # wttr.in은 무료 날씨 API입니다 (JSON 포맷)
        url = f"https://wttr.in/{location}?format=j1"
        response = requests.get(url, timeout=5)
        data = response.json()

        current = data['current_condition'][0]
        temp_f = float(current['temp_F'])
        humid = float(current['humidity'])
        wind_mph = float(current['windspeedMiles'])

        return temp_f, humid, wind_mph, None  # None은 에러 없음
    except Exception as e:
        return None, None, None, "위치를 찾을 수 없습니다. 철자를 확인해주세요."


# --- ACI 증발률 계산 함수 ---
def calc_evaporation_rate(tc, rh, v_mph):
    tc_f = (tc * 9 / 5) + 32
    conc_f = tc_f  # 콘크리트 온도 가정
    try:
        e = 5 * ((conc_f + 18) ** 2.5 - (rh / 100) * (tc_f + 18) ** 2.5) * (v_mph + 4) * (10 ** -6)
        return max(0, e)
    except:
        return 0.0


# --- 세션 상태 초기화 (날씨 자동 입력을 위해 필요) ---
if 'temp_val' not in st.session_state: st.session_state.temp_val = 75.0
if 'humid_val' not in st.session_state: st.session_state.humid_val = 50
if 'wind_val' not in st.session_state: st.session_state.wind_val = 5.0

# --- 사이드바 ---
with st.sidebar:
    st.header("🌐 언어 설정")
    lang = st.radio("Language", ["🇰🇷 한국어", "🇺🇸 English"])
    is_kor = lang == "🇰🇷 한국어"
    st.divider()
    st.subheader("☕ Support")
    bmc_link = "https://www.buymeacoffee.com/vvaann"
    st.markdown(
        f"""<a href="{bmc_link}" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" style="width: 100% !important;"></a>""",
        unsafe_allow_html=True)
    st.write("")
    paypal_url = "https://www.paypal.com/paypalme/아이디를입력하세요"
    btn_text = "💳 PayPal로 후원하기" if is_kor else "💳 Donate with PayPal"
    st.markdown(
        f"""<a href="{paypal_url}" target="_blank"><button style="background-color: #0070BA; color: white; border: none; padding: 10px; border-radius: 5px; width: 100%; font-weight: bold; cursor: pointer;">{btn_text}</button></a>""",
        unsafe_allow_html=True)
    st.divider()
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
# TAB 1: ☀️ 스마트 양생 (자동 날씨 연동)
# =================================================
with tabs[0]:
    st.markdown("### ☀️ Concrete Curing Manager")
    if is_kor:
        st.caption("지역명을 입력하면 실시간 날씨를 가져옵니다.")
    else:
        st.caption("Enter location to fetch real-time weather.")

    # 🔍 날씨 검색 UI
    with st.container(border=True):
        col_search, col_btn = st.columns([3, 1])
        loc_input = col_search.text_input("위치 검색 (예: Ohio, Atlanta, 45177)", placeholder="City or ZIP Code")

        if col_btn.button("🔍 날씨 가져오기", use_container_width=True):
            if loc_input:
                with st.spinner("Fetching weather..."):
                    t, h, w, err = get_weather_data(loc_input)
                    if err:
                        st.error(err)
                    else:
                        # 세션 상태 업데이트 (값 덮어쓰기)
                        st.session_state.temp_val = t
                        st.session_state.humid_val = int(h)
                        st.session_state.wind_val = w
                        st.success(f"✅ Loaded: {loc_input}")
            else:
                st.warning("위치를 입력하세요.")

        st.divider()

        # 입력창 (자동으로 값이 들어감)
        c1, c2, c3 = st.columns(3)
        temp_f = c1.number_input("기온 (Temp °F)", value=st.session_state.temp_val, step=1.0, format="%.1f",
                                 key="temp_input")
        humid = c2.number_input("습도 (Humidity %)", value=st.session_state.humid_val, step=5, max_value=100,
                                key="humid_input")
        wind = c3.number_input("풍속 (Wind mph)", value=st.session_state.wind_val, step=1.0, key="wind_input")

        # 섭씨 자동 변환 표시
        temp_c = (temp_f - 32) * 5 / 9
        st.caption(f"🌡️ 변환 온도: {temp_c:.1f}°C")

    # 분석 로직 (V26과 동일)
    evap_rate = calc_evaporation_rate(temp_c, humid, wind)

    st.markdown("#### 📊 분석 결과 (Analysis)")
    col_res1, col_res2 = st.columns([1, 1])

    with col_res1:
        st.markdown("**1. 온도 기준 (Temperature)**")
        if temp_f < 40:
            st.error("❄️ **한중 콘크리트 (Cold Weather)**")
            st.caption("🚨 40°F 미만! 보온 양생 필수")
        elif temp_f > 90:
            st.error("🔥 **서중 콘크리트 (Hot Weather)**")
            st.caption("🚨 90°F 초과! 쿨링 대책 필요")
        else:
            st.success("✅ **적정 온도 (Good)**")
            st.caption("표준 시방 범위 내 (40°F ~ 90°F)")

    with col_res2:
        st.markdown("**2. 소성 수축 균열 (Cracking Risk)**")
        st.metric("수분 증발률 (lb/ft²/hr)", f"{evap_rate:.3f}")

        if evap_rate > 0.2:
            st.error("🚨 **위험 (Critical)**")
            st.caption("0.2 초과! 즉시 균열 발생 가능. 방풍막/포깅 필수.")
        elif evap_rate > 0.1:
            st.warning("⚠️ **주의 (Caution)**")
            st.caption("0.1 초과. 모니터링 강화.")
        else:
            st.success("✅ **안전 (Safe)**")

# =================================================
# TAB 2~9: 기존 기능 유지 (생략 없이 V26과 동일하게 사용)
# =================================================
# (나머지 탭 코드는 V26과 완전히 동일하므로, 복사할 때 위쪽 TAB 1까지만 바꾸고 나머지는 그대로 두셔도 됩니다.
#  혹시 헷갈리실까봐 V26의 나머지 탭 코드를 여기에 붙여넣으세요)
with tabs[1]:
    if is_kor:
        comm_type = st.radio("기능", ["📻 무전 용어", "📖 건설 약어", "📧 이메일 템플릿"], horizontal=True)
    else:
        comm_type = st.radio("Tool", ["📻 Radio Terms", "📖 Acronyms", "📧 Email Templates"], horizontal=True)
    st.divider()

    if "Radio" in comm_type or "무전" in comm_type:
        st.subheader("📻 필수 무전 용어")
        radio_data = [
            {"Term": "10-4", "Meaning": "수신 양호 (Received)"},
            {"Term": "Copy that", "Meaning": "이해함 (Understood)"},
            {"Term": "What's your 20?", "Meaning": "현재 위치? (Location)"},
            {"Term": "Go ahead", "Meaning": "말해라 (Listening)"},
            {"Term": "Stand by", "Meaning": "대기하라 (Wait)"}
        ]
        st.table(pd.DataFrame(radio_data))

    elif "Acronyms" in comm_type or "약어" in comm_type:
        st.subheader("📖 건설 현장 약어")
        acronyms = [
            {"Abbr": "RFI", "Full": "Request for Information", "Desc": "설계 질의서"},
            {"Abbr": "CO", "Full": "Change Order", "Desc": "설계 변경 (비용발생)"},
            {"Abbr": "NTP", "Full": "Notice to Proceed", "Desc": "착공 지시서"},
            {"Abbr": "TBM", "Full": "Toolbox Meeting", "Desc": "작업 전 안전 조회"}
        ]
        df_acro = pd.DataFrame(acronyms)
        st.dataframe(df_acro, hide_index=True, use_container_width=True)

    elif "Email" in comm_type or "이메일" in comm_type:
        st.subheader("📧 이메일 작성기")
        type_ = st.selectbox("유형", ["자재 지연 (Delay)", "검측 요청 (Inspection)"])
        item = st.text_input("대상 항목", "Piping")
        if st.button("Generate"):
            if "Delay" in type_:
                st.info(
                    f"Subject: Notice of Delay - {item}\n\nDear Manager,\nWe regret to inform you of a delay regarding **{item}** due to unforeseen supply chain issues.")
            else:
                st.success(
                    f"Subject: Inspection Request - {item}\n\nDear Manager,\nInstallation of **{item}** is complete. Please schedule an inspection.")

with tabs[2]:
    if is_kor:
        eng_menu = st.radio("계산기", ["📉 배관 구배", "⚡ 트레이 채움률", "🏗️ 크레인 양중"], horizontal=True)
    else:
        eng_menu = st.radio("Tool", ["📉 Slope", "⚡ Tray Fill", "🏗️ Crane"], horizontal=True)
    st.divider()

    if "구배" in eng_menu or "Slope" in eng_menu:
        st.subheader("📉 배관 구배 (Slope Drop)")
        c1, c2 = st.columns(2)
        l_ft = c1.number_input("길이 (ft)", 50.0)
        slope = c2.select_slider("구배 (Slope)", ["1/8\"", "1/4\"", "1/2\"", "1\""])
        val = {"1/8\"": 0.125, "1/4\"": 0.25, "1/2\"": 0.5, "1\"": 1.0}[slope]
        drop = l_ft * val
        st.info(f"⬇️ **높이 차이: {drop:.2f} inch ({drop * 25.4:.1f} mm)**")

    elif "트레이" in eng_menu or "Tray" in eng_menu:
        st.subheader("⚡ 트레이 채움률 (Fill Ratio)")
        c1, c2, c3 = st.columns(3)
        w = c1.selectbox("Width (in)", [12, 18, 24, 30, 36])
        d = c2.selectbox("Depth (in)", [4, 6])
        dia = c3.number_input("Cable OD (in)", 1.0)
        cnt = st.slider("케이블 가닥수", 1, 100, 20)

        area = w * d;
        cable_area = (math.pi * (dia / 2) ** 2) * cnt
        ratio = (cable_area / area) * 100
        st.progress(min(ratio / 100, 1.0))
        st.metric("채움률 (Limit: 40%)", f"{ratio:.1f}%")
        if ratio > 40:
            st.error("❌ 초과 (Overfilled)")
        else:
            st.success("✅ 양호 (Pass)")

    elif "크레인" in eng_menu or "Crane" in eng_menu:
        st.subheader("🏗️ 양중 모멘트")
        w = st.number_input("무게 (lbs)", 5000)
        r = st.number_input("반경 (ft)", 50)
        st.metric("Load Moment", f"{w * r:,.0f} lbs-ft")

with tabs[3]:
    st.subheader("💱 실시간 환율 & 시차")
    df = get_exchange_rate()
    rate = df['Close'].iloc[-1] if df is not None else 1450.0

    c1, c2 = st.columns(2)
    c1.metric("USD/KRW", f"{rate:.1f}원")

    usd = c2.number_input("달러 ($)", 1000)
    c2.caption(f"≒ {int(usd * rate):,} 원")

    st.divider()
    st.subheader("⏰ 현장 시차")
    utc = datetime.now(pytz.utc)
    kr = utc.astimezone(pytz.timezone('Asia/Seoul'))
    us_et = utc.astimezone(pytz.timezone('US/Eastern'))

    col_t1, col_t2 = st.columns(2)
    col_t1.info(f"🇺🇸 현장 (ET)\n\n**{us_et.strftime('%H:%M')}**")
    col_t2.success(f"🇰🇷 한국 (KST)\n\n**{kr.strftime('%H:%M')}**")

with tabs[4]:
    st.subheader("📏 치수 변환")
    c1, c2 = st.columns(2)
    mm = c1.number_input("mm ➡️ ft-in", 1000)
    c1.code(f"{mm / 25.4 / 12:.2f} ft")
    ft = c2.number_input("ft ➡️ mm", 10)
    c2.code(f"{ft * 304.8:.0f} mm")

with tabs[5]:
    st.subheader("🚛 콘크리트 물량")
    m3 = st.number_input("입방미터 (m³)", 10.0)
    st.metric("야드 (yd³)", f"{m3 * 1.308:.2f}")

with tabs[6]:
    st.subheader("🚦 볼트/공구 호환성")
    b_type = st.selectbox("볼트 규격", ["1/2 inch", "3/4 inch", "M12", "M20"])
    if "inch" in b_type:
        st.error("⚠️ mm 공구 사용 금지 (헐거움 주의)")
    else:
        st.success("✅ inch 공구 일부 호환 가능 (확인 필요)")

with tabs[7]:
    st.subheader("📋 철근 규격")
    st.dataframe(pd.DataFrame({"US": ["#4", "#5", "#6"], "KR": ["D13", "D16", "D19"], "Dia(mm)": [12.7, 15.9, 19.1]}),
                 hide_index=True)

with tabs[8]:
    st.subheader("📝 Daily Report Generator")
    work = st.text_input("금일 작업", "Concrete Pouring at Zone A")
    if st.button("Create Report"):
        st.code(f"[Daily Report]\nDate: {datetime.now().date()}\nWork: {work}\nStatus: Ongoing")