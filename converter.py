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
# 🕵️‍♂️ GA Code (V26 유지)
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

    # ▼▼▼ PayPal 주소 확인 ▼▼▼
    paypal_url = "https://www.paypal.com/paypalme/아이디를입력하세요"

    btn_text = "💳 PayPal로 후원하기" if is_kor else "💳 Donate with PayPal"
    st.markdown(
        f"""<a href="{paypal_url}" target="_blank"><button style="background-color: #0070BA; color: white; border: none; padding: 10px; border-radius: 5px; width: 100%; font-weight: bold; cursor: pointer;">{btn_text}</button></a>""",
        unsafe_allow_html=True)

    st.divider()
    st.subheader("📧 Contact")
    if is_kor:
        st.caption("비즈니스 / 기능 제안")
    else:
        st.caption("Business & Feedback")
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
# TAB 1: ☀️ 스마트 양생 (완벽 번역)
# =================================================
with tabs[0]:
    if is_kor:
        st.markdown("### ☀️ 스마트 콘크리트 양생 관리")
        st.caption("지역명을 입력하면 실시간 날씨를 가져옵니다.")
        lbl_search = "위치 검색 (예: Atlanta, 30303)"
        lbl_btn = "🔍 날씨 가져오기"
        err_msg = "위치를 찾을 수 없습니다."
        suc_msg = "날씨 로딩 완료:"
        lbl_temp = "기온 (Temp °F)"
        lbl_humid = "습도 (Humidity %)"
        lbl_wind = "풍속 (Wind mph)"
        lbl_conv = "🌡️ 변환 온도:"
        head_res = "#### 📊 분석 결과"
        head_temp = "**1. 온도 기준**"
        head_crack = "**2. 소성 수축 균열 (Cracking Risk)**"
        txt_evap = "수분 증발률"

        # 결과 메시지 (한글)
        res_cold = ("❄️ **한중 콘크리트 (Cold Weather)**", "🚨 40°F 미만! 보온 양생 필수")
        res_hot = ("🔥 **서중 콘크리트 (Hot Weather)**", "🚨 90°F 초과! 쿨링 대책 필요")
        res_good = ("✅ **적정 온도 (Good)**", "표준 시방 범위 내 (40°F ~ 90°F)")

        risk_crit = ("🚨 **위험 (Critical)**", "0.2 초과! 즉시 균열 발생 가능. 방풍막/포깅 필수.")
        risk_warn = ("⚠️ **주의 (Caution)**", "0.1 초과. 모니터링 강화.")
        risk_safe = ("✅ **안전 (Safe)**", "균열 위험 낮음.")

        tip_title = "💡 소장님을 위한 팁 (Pro Tip)"
        tip_txt = """
        * **Cold Weather (40°F↓):** 초기 동해 주의. 보온 덮개 필수.
        * **Evaporation:** 바람이 10mph만 넘어도 위험합니다. 포깅(Fogging) 준비하세요.
        """
    else:
        st.markdown("### ☀️ Concrete Curing Manager")
        st.caption("Enter location to fetch real-time weather.")
        lbl_search = "Search Location (e.g., Atlanta, 30303)"
        lbl_btn = "🔍 Get Weather"
        err_msg = "Location not found. Check spelling."
        suc_msg = "Loaded:"
        lbl_temp = "Temp (°F)"
        lbl_humid = "Humidity (%)"
        lbl_wind = "Wind Speed (mph)"
        lbl_conv = "🌡️ In Celsius:"
        head_res = "#### 📊 Analysis Result"
        head_temp = "**1. Temperature Check**"
        head_crack = "**2. Cracking Risk (Evaporation)**"
        txt_evap = "Evaporation Rate"

        # 결과 메시지 (영어)
        res_cold = ("❄️ **Cold Weather Concrete**", "🚨 Below 40°F! Thermal protection required.")
        res_hot = ("🔥 **Hot Weather Concrete**", "🚨 Above 90°F! Cooling measures required.")
        res_good = ("✅ **Good Condition**", "Within ACI standard range (40°F ~ 90°F).")

        risk_crit = ("🚨 **CRITICAL**", "Over 0.2! High cracking risk. Windbreaks/Fogging required.")
        risk_warn = ("⚠️ **CAUTION**", "Over 0.1. Monitor closely.")
        risk_safe = ("✅ **SAFE**", "Low cracking risk.")

        tip_title = "💡 Pro Tips"
        tip_txt = """
        * **Cold Weather (40°F↓):** Early freezing reduces strength by 50%. Use insulation blankets.
        * **Evaporation:** Wind over 10mph drastically increases evaporation. Be ready to mist/fog.
        """

    # UI 구성
    with st.container(border=True):
        col_search, col_btn = st.columns([3, 1])
        loc_input = col_search.text_input(lbl_search, placeholder="City or ZIP")

        if col_btn.button(lbl_btn, use_container_width=True):
            if loc_input:
                with st.spinner("Loading..."):
                    t, h, w, err = get_weather_data(loc_input)
                    if err:
                        st.error(err_msg)
                    else:
                        st.session_state.temp_val = t
                        st.session_state.humid_val = int(h)
                        st.session_state.wind_val = w
                        st.success(f"✅ {suc_msg} {loc_input}")

        st.divider()
        c1, c2, c3 = st.columns(3)
        temp_f = c1.number_input(lbl_temp, value=st.session_state.temp_val, step=1.0, format="%.1f")
        humid = c2.number_input(lbl_humid, value=st.session_state.humid_val, step=5, max_value=100)
        wind = c3.number_input(lbl_wind, value=st.session_state.wind_val, step=1.0)

        temp_c = (temp_f - 32) * 5 / 9
        st.caption(f"{lbl_conv} {temp_c:.1f}°C")

    # 분석
    evap_rate = calc_evaporation_rate(temp_c, humid, wind)

    st.markdown(head_res)
    col_r1, col_r2 = st.columns([1, 1])

    with col_r1:
        st.markdown(head_temp)
        if temp_f < 40:
            st.error(res_cold[0]);
            st.caption(res_cold[1])
        elif temp_f > 90:
            st.error(res_hot[0]);
            st.caption(res_hot[1])
        else:
            st.success(res_good[0]);
            st.caption(res_good[1])

    with col_r2:
        st.markdown(head_crack)
        st.metric(f"{txt_evap} (lb/ft²/hr)", f"{evap_rate:.3f}")

        if evap_rate > 0.2:
            st.error(risk_crit[0]);
            st.caption(risk_crit[1])
        elif evap_rate > 0.1:
            st.warning(risk_warn[0]);
            st.caption(risk_warn[1])
        else:
            st.success(risk_safe[0]);
            st.caption(risk_safe[1])

    with st.expander(tip_title):
        st.markdown(tip_txt)

# =================================================
# TAB 2: 소통 (완벽 번역)
# =================================================
with tabs[1]:
    # 라디오 버튼 옵션 다국어 처리
    opt_radio = "📻 무전 용어" if is_kor else "📻 Radio Terms"
    opt_acro = "📖 건설 약어" if is_kor else "📖 Acronyms"
    opt_email = "📧 이메일 템플릿" if is_kor else "📧 Email Templates"

    lbl_func = "기능 선택" if is_kor else "Select Tool"
    comm_type = st.radio(lbl_func, [opt_radio, opt_acro, opt_email], horizontal=True)
    st.divider()

    if opt_radio in comm_type:
        st.subheader(opt_radio)
        radio_data = [
            {"Term": "10-4", "Meaning": "Received / OK"},
            {"Term": "Copy that", "Meaning": "Understood"},
            {"Term": "What's your 20?", "Meaning": "Current Location?"},
            {"Term": "Go ahead", "Meaning": "Ready to listen"},
            {"Term": "Stand by", "Meaning": "Wait"}
        ]
        st.table(pd.DataFrame(radio_data))

    elif opt_acro in comm_type:
        st.subheader(opt_acro)
        acronyms = [
            {"Abbr": "RFI", "Full": "Request for Information"},
            {"Abbr": "CO", "Full": "Change Order"},
            {"Abbr": "NTP", "Full": "Notice to Proceed"},
            {"Abbr": "TBM", "Full": "Toolbox Meeting"}
        ]
        st.dataframe(pd.DataFrame(acronyms), hide_index=True, use_container_width=True)

    elif opt_email in comm_type:
        st.subheader("📧 Email Generator")
        lbl_type = "상황 선택" if is_kor else "Select Situation"
        lbl_item = "대상 항목" if is_kor else "Item / Subject"
        lbl_btn = "생성하기" if is_kor else "Generate"

        opt_delay = "자재 지연 (Delay)" if is_kor else "Delay Notice"
        opt_insp = "검측 요청 (Inspection)" if is_kor else "Inspection Request"

        type_ = st.selectbox(lbl_type, [opt_delay, opt_insp])
        item = st.text_input(lbl_item, "Piping Material")

        if st.button(lbl_btn):
            if "Delay" in type_ or "Delay" in type_:
                st.info(
                    f"Subject: Notice of Delay - {item}\n\nDear Manager,\nWe regret to inform you of a delay regarding **{item}** due to supply chain issues.\nWe will update the schedule shortly.")
            else:
                st.success(
                    f"Subject: Inspection Request - {item}\n\nDear Manager,\nInstallation of **{item}** is complete.\nPlease schedule an inspection at your earliest convenience.")

# =================================================
# TAB 3: 공학 계산 (완벽 번역)
# =================================================
with tabs[2]:
    # 메뉴 다국어
    opt_slope = "📉 배관 구배" if is_kor else "📉 Slope Calc"
    opt_tray = "⚡ 트레이 채움률" if is_kor else "⚡ Tray Fill"
    opt_crane = "🏗️ 크레인 양중" if is_kor else "🏗️ Crane Lift"

    eng_menu = st.radio("Menu", [opt_slope, opt_tray, opt_crane], horizontal=True)
    st.divider()

    if opt_slope in eng_menu:
        st.subheader("📉 Slope Calculator")
        c1, c2 = st.columns(2)
        lbl_len = "설치 길이 (ft)" if is_kor else "Length (ft)"
        lbl_slp = "구배 (Slope)" if is_kor else "Slope"

        l_ft = c1.number_input(lbl_len, 50.0)
        slope = c2.select_slider(lbl_slp, ["1/8\"", "1/4\"", "1/2\"", "1\""])
        val = {"1/8\"": 0.125, "1/4\"": 0.25, "1/2\"": 0.5, "1\"": 1.0}[slope]
        drop = l_ft * val

        lbl_res = "높이 차이" if is_kor else "Drop"
        st.info(f"⬇️ **{lbl_res}: {drop:.2f} inch ({drop * 25.4:.1f} mm)**")

    elif opt_tray in eng_menu:
        st.subheader("⚡ Tray Fill Ratio")
        c1, c2, c3 = st.columns(3)
        lbl_w = "폭 (Width)" if is_kor else "Width (in)"
        lbl_d = "깊이 (Depth)" if is_kor else "Depth (in)"
        lbl_od = "케이블 외경" if is_kor else "Cable OD (in)"
        lbl_cnt = "가닥수" if is_kor else "Count"

        w = c1.selectbox(lbl_w, [12, 18, 24, 30, 36])
        d = c2.selectbox(lbl_d, [4, 6])
        dia = c3.number_input(lbl_od, 1.0)
        cnt = st.slider(lbl_cnt, 1, 100, 20)

        area = w * d;
        cable_area = (math.pi * (dia / 2) ** 2) * cnt
        ratio = (cable_area / area) * 100
        st.progress(min(ratio / 100, 1.0))

        lbl_fill = "채움률" if is_kor else "Fill Ratio"
        msg_over = "❌ 초과 (Overfilled)" if is_kor else "❌ Overfilled"
        msg_pass = "✅ 양호 (Pass)" if is_kor else "✅ Pass"

        st.metric(f"{lbl_fill} (Max 40%)", f"{ratio:.1f}%")
        if ratio > 40:
            st.error(msg_over)
        else:
            st.success(msg_pass)

    elif opt_crane in eng_menu:
        st.subheader("🏗️ Load Moment")
        lbl_w = "무게 (lbs)" if is_kor else "Weight (lbs)"
        lbl_r = "작업 반경 (ft)" if is_kor else "Radius (ft)"

        w = st.number_input(lbl_w, 5000)
        r = st.number_input(lbl_r, 50)
        st.metric("Load Moment", f"{w * r:,.0f} lbs-ft")

# =================================================
# TAB 4: 생활 (완벽 번역)
# =================================================
with tabs[3]:
    st.subheader("💱 Exchange Rate & Time")
    df = get_exchange_rate()
    rate = df['Close'].iloc[-1] if df is not None else 1450.0

    c1, c2 = st.columns(2)
    c1.metric("USD/KRW", f"{rate:.1f}")

    lbl_usd = "달러 ($)" if is_kor else "USD ($)"
    usd = c2.number_input(lbl_usd, 1000)
    c2.caption(f"≒ {int(usd * rate):,} KRW")

    st.divider()
    st.subheader("⏰ World Time")
    utc = datetime.now(pytz.utc)
    kr = utc.astimezone(pytz.timezone('Asia/Seoul'))
    us_et = utc.astimezone(pytz.timezone('US/Eastern'))

    lbl_us = "🇺🇸 현장 (ET)" if is_kor else "🇺🇸 Site (ET)"
    lbl_kr = "🇰🇷 한국 (KST)" if is_kor else "🇰🇷 Korea (KST)"

    col_t1, col_t2 = st.columns(2)
    col_t1.info(f"{lbl_us}\n\n**{us_et.strftime('%H:%M')}**")
    col_t2.success(f"{lbl_kr}\n\n**{kr.strftime('%H:%M')}**")

# =================================================
# TAB 5~9: 기타 유틸 (라벨 영문화 적용)
# =================================================
with tabs[4]:  # 치수
    st.subheader("📏 Unit Conversion")
    c1, c2 = st.columns(2)
    mm = c1.number_input("mm ➡️ ft-in", 1000)
    c1.code(f"{mm / 25.4 / 12:.2f} ft")
    ft = c2.number_input("ft ➡️ mm", 10)
    c2.code(f"{ft * 304.8:.0f} mm")

with tabs[5]:  # 자재
    head_mat = "🚛 콘크리트 물량" if is_kor else "🚛 Concrete Volume"
    lbl_m3 = "입방미터 (m³)" if is_kor else "Cubic Meter (m³)"
    lbl_yd = "야드 (yd³)" if is_kor else "Cubic Yard (yd³)"

    st.subheader(head_mat)
    m3 = st.number_input(lbl_m3, 10.0)
    st.metric(lbl_yd, f"{m3 * 1.308:.2f}")

with tabs[6]:  # 호환성
    st.subheader("🚦 Tool Compatibility")
    lbl_bolt = "볼트 규격" if is_kor else "Bolt Size"
    b_type = st.selectbox(lbl_bolt, ["1/2 inch", "3/4 inch", "M12", "M20"])

    msg_warn = "⚠️ mm 공구 금지 (헐거움)" if is_kor else "⚠️ Do NOT use mm tools (Loose fit)"
    msg_ok = "✅ inch 공구 호환 가능" if is_kor else "✅ Inch tools compatible (Check fit)"

    if "inch" in b_type:
        st.error(msg_warn)
    else:
        st.success(msg_ok)

with tabs[7]:  # 규격표
    st.subheader("📋 Rebar Size")
    st.dataframe(pd.DataFrame({"US": ["#4", "#5", "#6"], "KR": ["D13", "D16", "D19"], "Dia(mm)": [12.7, 15.9, 19.1]}),
                 hide_index=True)

with tabs[8]:  # 보고서
    st.subheader("📝 Daily Report")
    lbl_work = "금일 작업" if is_kor else "Today's Work"
    btn_rpt = "보고서 생성" if is_kor else "Create Report"

    work = st.text_input(lbl_work, "Concrete Pouring at Zone A")
    if st.button(btn_rpt):
        st.code(f"[Daily Report]\nDate: {datetime.now().date()}\nWork: {work}\nStatus: Ongoing")