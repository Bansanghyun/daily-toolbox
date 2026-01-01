import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math
import requests
from datetime import datetime, timedelta
import pytz

# yfinance 안전 로딩
try:
    import yfinance as yf

    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

st.set_page_config(page_title="Daily Toolbox", page_icon="🧰", layout="centered")


# ==========================================
# 🕵️‍♂️ GA Code (유지)
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
# TAB 1: ☀️ 스마트 양생 (V30 유지)
# =================================================
with tabs[0]:
    if is_kor:
        st.markdown("### ☀️ 스마트 콘크리트 양생 관리")
        st.caption("지역명 입력 시 날씨 자동 연동 (ACI 305R/306R 기반)")
        with st.container(border=True):
            col_search, col_btn = st.columns([3, 1])
            loc_input = col_search.text_input("위치 검색 (예: Atlanta, 30303)", placeholder="도시명 또는 ZIP Code")
            if col_btn.button("🔍 날씨 가져오기", use_container_width=True):
                if loc_input:
                    with st.spinner("날씨 정보를 불러오는 중..."):
                        t, h, w, err = get_weather_data(loc_input)
                        if err:
                            st.error("위치를 찾을 수 없습니다.")
                        else:
                            st.session_state.temp_val = t
                            st.session_state.humid_val = int(h)
                            st.session_state.wind_val = w
                            st.success(f"✅ 로딩 완료: {loc_input}")
            st.divider()
            c1, c2, c3 = st.columns(3)
            temp_f = c1.number_input("기온 (Temp °F)", value=st.session_state.temp_val, step=1.0, format="%.1f")
            humid = c2.number_input("습도 (Humidity %)", value=st.session_state.humid_val, step=5, max_value=100)
            wind = c3.number_input("풍속 (Wind mph)", value=st.session_state.wind_val, step=1.0)
            st.caption(f"🌡️ 변환 온도: {(temp_f - 32) * 5 / 9:.1f}°C")
        evap_rate = calc_evaporation_rate((temp_f - 32) * 5 / 9, humid, wind)
        st.markdown("#### 📊 분석 결과")
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            st.markdown("**1. 온도 기준**")
            if temp_f < 40:
                st.error("❄️ **한중 콘크리트 (Cold)**"); st.caption("🚨 40°F 미만! 보온 필수")
            elif temp_f > 90:
                st.error("🔥 **서중 콘크리트 (Hot)**"); st.caption("🚨 90°F 초과! 쿨링 필요")
            else:
                st.success("✅ **적정 온도 (Good)**"); st.caption("40°F ~ 90°F")
        with col_r2:
            st.markdown("**2. 균열 위험도**")
            st.metric("증발률 (lb/ft²/hr)", f"{evap_rate:.3f}")
            if evap_rate > 0.2:
                st.error("🚨 **위험 (Critical)**"); st.caption("즉시 균열 위험! 방풍막/포깅")
            elif evap_rate > 0.1:
                st.warning("⚠️ **주의 (Caution)**"); st.caption("모니터링 강화")
            else:
                st.success("✅ **안전 (Safe)**")
    else:
        st.markdown("### ☀️ Concrete Curing Manager")
        st.caption("Auto-weather based on ACI 305R/306R Standards.")
        with st.container(border=True):
            col_search, col_btn = st.columns([3, 1])
            loc_input = col_search.text_input("Search Location (e.g., Atlanta, 30303)", placeholder="City or ZIP")
            if col_btn.button("🔍 Get Weather", use_container_width=True):
                if loc_input:
                    with st.spinner("Fetching data..."):
                        t, h, w, err = get_weather_data(loc_input)
                        if err:
                            st.error("Location not found.")
                        else:
                            st.session_state.temp_val = t
                            st.session_state.humid_val = int(h)
                            st.session_state.wind_val = w
                            st.success(f"✅ Loaded: {loc_input}")
            st.divider()
            c1, c2, c3 = st.columns(3)
            temp_f = c1.number_input("Temp (°F)", value=st.session_state.temp_val, step=1.0, format="%.1f")
            humid = c2.number_input("Humidity (%)", value=st.session_state.humid_val, step=5, max_value=100)
            wind = c3.number_input("Wind Speed (mph)", value=st.session_state.wind_val, step=1.0)
            st.caption(f"🌡️ In Celsius: {(temp_f - 32) * 5 / 9:.1f}°C")
        evap_rate = calc_evaporation_rate((temp_f - 32) * 5 / 9, humid, wind)
        st.markdown("#### 📊 Analysis Result")
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            st.markdown("**1. Temperature Check**")
            if temp_f < 40:
                st.error("❄️ **Cold Weather**"); st.caption("🚨 Below 40°F! Protection required.")
            elif temp_f > 90:
                st.error("🔥 **Hot Weather**"); st.caption("🚨 Above 90°F! Cooling required.")
            else:
                st.success("✅ **Good Condition**"); st.caption("Within 40°F ~ 90°F")
        with col_r2:
            st.markdown("**2. Cracking Risk**")
            st.metric("Evaporation Rate", f"{evap_rate:.3f}")
            if evap_rate > 0.2:
                st.error("🚨 **CRITICAL**"); st.caption("High risk! Use windbreaks/fogging.")
            elif evap_rate > 0.1:
                st.warning("⚠️ **CAUTION**"); st.caption("Monitor closely.")
            else:
                st.success("✅ **SAFE**")

# =================================================
# TAB 2: 소통 (V30 유지)
# =================================================
with tabs[1]:
    if is_kor:
        comm_type = st.radio("기능", ["📻 무전 용어", "📖 건설 약어", "📧 이메일 템플릿"], horizontal=True)
        st.divider()
        if "무전" in comm_type:
            st.table(pd.DataFrame([{"용어": "10-4", "의미": "수신 양호"}, {"용어": "Copy that", "의미": "내용 이해함"},
                                   {"용어": "What's your 20?", "의미": "현재 위치?"}, {"용어": "Go ahead", "의미": "말해라"}]))
        elif "약어" in comm_type:
            st.dataframe(pd.DataFrame([{"약어": "RFI", "원어": "Request for Information", "설명": "질의서"},
                                       {"약어": "CO", "원어": "Change Order", "설명": "설계 변경"},
                                       {"약어": "NTP", "원어": "Notice to Proceed", "설명": "착공 지시"}]), hide_index=True,
                         use_container_width=True)
        elif "이메일" in comm_type:
            t = st.selectbox("상황", ["자재 지연", "검측 요청"])
            i = st.text_input("항목", "Piping")
            if st.button("생성"):
                if "지연" in t:
                    st.info(
                        f"Subject: Delay Notice - {i}\n\nDear Manager,\nWe regret to inform you of a delay regarding **{i}**.")
                else:
                    st.success(
                        f"Subject: Inspection Request - {i}\n\nDear Manager,\nInstallation of **{i}** is complete.")
    else:
        comm_type = st.radio("Tool", ["📻 Radio Terms", "📖 Acronyms", "📧 Email Templates"], horizontal=True)
        st.divider()
        if "Radio" in comm_type:
            st.table(pd.DataFrame(
                [{"Term": "10-4", "Meaning": "Received"}, {"Term": "Copy that", "Meaning": "Understood"},
                 {"Term": "What's your 20?", "Meaning": "Location?"}, {"Term": "Go ahead", "Meaning": "Listening"}]))
        elif "Acronyms" in comm_type:
            st.dataframe(pd.DataFrame(
                [{"Abbr": "RFI", "Full": "Request for Information"}, {"Abbr": "CO", "Full": "Change Order"},
                 {"Abbr": "NTP", "Full": "Notice to Proceed"}]), hide_index=True, use_container_width=True)
        elif "Email" in comm_type:
            t = st.selectbox("Situation", ["Delay Notice", "Inspection Request"])
            i = st.text_input("Item", "Piping")
            if st.button("Generate"):
                if "Delay" in t:
                    st.info(
                        f"Subject: Delay Notice - {i}\n\nDear Manager,\nWe regret to inform you of a delay regarding **{i}**.")
                else:
                    st.success(
                        f"Subject: Inspection Request - {i}\n\nDear Manager,\nInstallation of **{i}** is complete.")

# =================================================
# TAB 3: 공학 계산 (🔥 볼트 토크 기능 추가됨)
# =================================================
with tabs[2]:
    if is_kor:
        # 🔧 '볼트 토크' 메뉴 추가
        eng_menu = st.radio("계산기", ["📉 배관 구배", "⚡ 트레이 채움률", "🏗️ 크레인 양중", "🔧 볼트 토크"], horizontal=True)
        st.divider()
        if "구배" in eng_menu:
            c1, c2 = st.columns(2)
            l = c1.number_input("길이 (ft)", 50.0)
            s = c2.select_slider("구배", ["1/8\"", "1/4\"", "1/2\"", "1\""])
            d = l * {"1/8\"": 0.125, "1/4\"": 0.25, "1/2\"": 0.5, "1\"": 1.0}[s]
            st.info(f"⬇️ **높이 차이: {d:.2f} inch ({d * 25.4:.1f} mm)**")
        elif "트레이" in eng_menu:
            c1, c2, c3 = st.columns(3)
            w = c1.selectbox("폭 (Width)", [12, 18, 24, 30, 36])
            d = c2.selectbox("깊이 (Depth)", [4, 6])
            dia = c3.number_input("케이블 외경 (in)", 1.0)
            cnt = st.slider("가닥수", 1, 100, 20)
            r = ((math.pi * (dia / 2) ** 2) * cnt / (w * d)) * 100
            st.metric("채움률 (Limit 40%)", f"{r:.1f}%")
            if r > 40:
                st.error("❌ 초과 (Overfilled)")
            else:
                st.success("✅ 양호 (Pass)")
        elif "크레인" in eng_menu:
            w = st.number_input("무게 (lbs)", 5000)
            r = st.number_input("반경 (ft)", 50)
            st.metric("부하 모멘트", f"{w * r:,.0f} lbs-ft")
        elif "볼트" in eng_menu:
            # 🔧 볼트 토크 로직 (한국어)
            st.subheader("🔧 볼트 체결 토크 (AISC/RCSC)")
            st.caption("고장력 볼트(High Strength Bolt) 권장 토크값")
            c1, c2 = st.columns(2)
            b_size = c1.selectbox("볼트 직경 (Inch)", ["1/2", "5/8", "3/4", "7/8", "1"])
            b_grade = c2.selectbox("등급 (Grade)", ["A325", "A490"])

            # 토크 데이터 (ft-lbs) - 일반적인 현장 참조값
            torque_db = {
                "A325": {"1/2": 90, "5/8": 180, "3/4": 320, "7/8": 500, "1": 750},
                "A490": {"1/2": 110, "5/8": 220, "3/4": 390, "7/8": 600, "1": 900}
            }
            res = torque_db[b_grade][b_size]
            st.success(f"🎯 **권장 토크: {res} ft-lbs**")
            st.caption("※ 현장 상황/윤활 여부에 따라 달라질 수 있음.")

    else:
        # 🔧 Added 'Bolt Torque'
        eng_menu = st.radio("Tool", ["📉 Slope Calc", "⚡ Tray Fill", "🏗️ Crane Lift", "🔧 Bolt Torque"], horizontal=True)
        st.divider()
        if "Slope" in eng_menu:
            c1, c2 = st.columns(2)
            l = c1.number_input("Length (ft)", 50.0)
            s = c2.select_slider("Slope", ["1/8\"", "1/4\"", "1/2\"", "1\""])
            d = l * {"1/8\"": 0.125, "1/4\"": 0.25, "1/2\"": 0.5, "1\"": 1.0}[s]
            st.info(f"⬇️ **Drop: {d:.2f} inch ({d * 25.4:.1f} mm)**")
        elif "Tray" in eng_menu:
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
            w = st.number_input("Weight (lbs)", 5000)
            r = st.number_input("Radius (ft)", 50)
            st.metric("Load Moment", f"{w * r:,.0f} lbs-ft")
        elif "Bolt" in eng_menu:
            # 🔧 Bolt Torque Logic (English)
            st.subheader("🔧 Bolt Tightening Torque")
            st.caption("Based on AISC/RCSC Standards")
            c1, c2 = st.columns(2)
            b_size = c1.selectbox("Diameter (Inch)", ["1/2", "5/8", "3/4", "7/8", "1"])
            b_grade = c2.selectbox("Grade", ["A325", "A490"])

            torque_db = {
                "A325": {"1/2": 90, "5/8": 180, "3/4": 320, "7/8": 500, "1": 750},
                "A490": {"1/2": 110, "5/8": 220, "3/4": 390, "7/8": 600, "1": 900}
            }
            res = torque_db[b_grade][b_size]
            st.success(f"🎯 **Target Torque: {res} ft-lbs**")

# =================================================
# TAB 4: 생활/금융 (🔥 야근 비용 기능 추가됨)
# =================================================
with tabs[3]:
    if is_kor:
        # 💰 '야근 비용' 메뉴 추가
        life_menu = st.radio("메뉴", ["💱 실시간 환율", "⏰ 한-미 시차", "💸 연봉 실수령액", "💰 야근 비용", "🍽️ 팁/더치페이"], horizontal=True)
        st.divider()

        if "환율" in life_menu:
            st.subheader("💱 원/달러 환율 (USD/KRW)")
            df_rate = get_exchange_rate()
            if df_rate is not None:
                curr = df_rate['Close'].iloc[-1];
                prev = df_rate['Close'].iloc[-2]
                c1, c2 = st.columns([1, 2])
                c1.metric("현재 환율", f"{curr:.2f} 원", f"{curr - prev:.2f} 원")
                st.line_chart(df_rate['Close'])
                rate = curr
            else:
                st.warning("⚠️ 인터넷 연결 실패. 수동 입력해주세요.")
                rate = st.number_input("환율 직접 입력 (원)", 1450.0)
            c1, c2 = st.columns(2)
            u_in = c1.number_input("달러 (USD)", 1000.0)
            c2.metric("원화 (KRW)", f"{int(u_in * rate):,} 원")

        elif "시차" in life_menu:
            st.subheader("🌏 글로벌 시차 시뮬레이션")
            tz_e = pytz.timezone('US/Eastern');
            tz_w = pytz.timezone('US/Pacific');
            tz_k = pytz.timezone('Asia/Seoul')
            now = datetime.now(tz_e)
            offset = st.slider("시간 조절 (Time Slider)", 0, 23, now.hour)
            target = now.replace(hour=offset, minute=0, second=0)
            c1, c2, c3 = st.columns(3)
            c1.metric("미국 동부 (ET)", target.astimezone(tz_e).strftime('%I:%M %p'))
            c2.metric("미국 서부 (PT)", target.astimezone(tz_w).strftime('%I:%M %p'))
            c3.metric("한국 (KST)", target.astimezone(tz_k).strftime('%I:%M %p'))
            kh = target.astimezone(tz_k).hour
            if 22 <= kh or kh < 7:
                st.error("💤 한국은 지금 자는 시간입니다.")
            elif 9 <= kh < 18:
                st.success("✅ 한국은 업무 시간입니다.")
            else:
                st.warning("🌙 한국은 퇴근 후입니다.")

        elif "연봉" in life_menu:
            st.subheader("💸 연봉 실수령액 (Net Salary)")
            s = st.number_input("연봉 (Gross Salary $)", 80000, step=1000)
            tax = max(0, s - 14600) * (0.18 if s > 100000 else 0.12)
            fica = s * 0.0765
            net = s - tax - fica
            c1, c2 = st.columns(2)
            c1.metric("예상 세금 (Tax)", f"-${(tax + fica):,.0f}")
            c2.metric("월 실수령액", f"${net / 12:,.0f}")

        elif "야근" in life_menu:
            # 💰 야근 비용 계산 로직 (한국어)
            st.subheader("💰 야근/특근 비용 계산기")
            st.caption("추가 작업(Overtime) 발생 시 예상 비용")

            c1, c2 = st.columns(2)
            ppl = c1.number_input("투입 인원 (명)", 1, 50, 5)
            rate = c2.number_input("평균 시급 ($)", 25.0, 100.0, 40.0)

            c3, c4 = st.columns(2)
            hours = c3.number_input("추가 시간 (Hours)", 1.0, 24.0, 2.0)
            mul = c4.radio("할증 비율", ["1.5배 (평일OT)", "2.0배 (휴일/심야)"], horizontal=True)

            m_val = 1.5 if "1.5" in mul else 2.0
            total_cost = ppl * rate * hours * m_val

            st.divider()
            st.metric("💸 총 예상 비용", f"${total_cost:,.0f}")
            st.info(f"계산식: {ppl}명 x ${rate} x {hours}시간 x {m_val}배")

        elif "팁" in life_menu:
            st.subheader("🍽️ 팁 & 더치페이 계산기")
            c1, c2 = st.columns(2)
            bill = c1.number_input("음식값 ($)", 50.0)
            tip_p = c2.select_slider("팁 비율 (%)", [15, 18, 20, 22, 25], value=18)
            ppl = st.number_input("인원 수", 1, 10, 1)
            total = bill * (1 + tip_p / 100)
            per_person = total / ppl
            col_res1, col_res2 = st.columns(2)
            col_res1.metric("총 지불액", f"${total:.2f}")
            col_res2.success(f"🙆‍♂️ 1인당: **${per_person:.2f}**")

    else:
        # [ENGLISH MODE]
        # 💰 Added 'OT Cost'
        life_menu = st.radio("Menu", ["💱 Exchange Rate", "⏰ Timezone", "💸 Net Salary", "💰 OT Cost", "🍽️ Tip Calc"],
                             horizontal=True)
        st.divider()

        if "Exchange" in life_menu:
            st.subheader("💱 USD/KRW Exchange Rate")
            df_rate = get_exchange_rate()
            if df_rate is not None:
                curr = df_rate['Close'].iloc[-1]
                st.metric("Current Rate", f"{curr:.2f} KRW")
                st.line_chart(df_rate['Close'])
                rate = curr
            else:
                st.warning("Offline mode.")
                rate = st.number_input("Manual Rate", 1450.0)
            c1, c2 = st.columns(2)
            u_in = c1.number_input("USD ($)", 1000.0)
            c2.metric("KRW (won)", f"{int(u_in * rate):,}")

        elif "Time" in life_menu:
            st.subheader("🌏 Global Time Converter")
            tz_e = pytz.timezone('US/Eastern');
            tz_w = pytz.timezone('US/Pacific');
            tz_k = pytz.timezone('Asia/Seoul')
            now = datetime.now(tz_e)
            offset = st.slider("Adjust Time (Hour)", 0, 23, now.hour)
            target = now.replace(hour=offset, minute=0, second=0)
            c1, c2, c3 = st.columns(3)
            c1.metric("US East (ET)", target.astimezone(tz_e).strftime('%I:%M %p'))
            c2.metric("US West (PT)", target.astimezone(tz_w).strftime('%I:%M %p'))
            c3.metric("Korea (KST)", target.astimezone(tz_k).strftime('%I:%M %p'))
            kh = target.astimezone(tz_k).hour
            if 22 <= kh or kh < 7:
                st.error("💤 Korea is sleeping.")
            elif 9 <= kh < 18:
                st.success("✅ Korea Business Hours.")
            else:
                st.warning("🌙 Korea After work.")

        elif "Salary" in life_menu:
            st.subheader("💸 Net Salary Calculator")
            s = st.number_input("Annual Gross Salary ($)", 80000, step=1000)
            tax = max(0, s - 14600) * (0.18 if s > 100000 else 0.12)
            fica = s * 0.0765
            net = s - tax - fica
            c1, c2 = st.columns(2)
            c1.metric("Est. Tax", f"-${(tax + fica):,.0f}")
            c2.metric("Monthly Net", f"${net / 12:,.0f}")

        elif "OT" in life_menu:
            # 💰 OT Cost Logic (English)
            st.subheader("💰 Overtime Cost Estimator")
            st.caption("Calculate extra labor cost for overtime work.")

            c1, c2 = st.columns(2)
            ppl = c1.number_input("Manpower", 1, 50, 5)
            rate = c2.number_input("Avg Hourly Rate ($)", 25.0, 100.0, 40.0)

            c3, c4 = st.columns(2)
            hours = c3.number_input("OT Hours", 1.0, 24.0, 2.0)
            mul = c4.radio("Multiplier", ["1.5x (Regular OT)", "2.0x (Holiday/Sunday)"], horizontal=True)

            m_val = 1.5 if "1.5" in mul else 2.0
            total_cost = ppl * rate * hours * m_val

            st.divider()
            st.metric("💸 Estimated Cost", f"${total_cost:,.0f}")
            st.info(f"Formula: {ppl} men x ${rate} x {hours} hrs x {m_val}")

        elif "Tip" in life_menu:
            st.subheader("🍽️ Tip & Split")
            c1, c2 = st.columns(2)
            bill = c1.number_input("Bill Amount ($)", 50.0)
            tip_p = c2.select_slider("Tip %", [15, 18, 20, 22, 25], value=18)
            ppl = st.number_input("People", 1, 10, 1)
            total = bill * (1 + tip_p / 100)
            per_person = total / ppl
            col_res1, col_res2 = st.columns(2)
            col_res1.metric("Total", f"${total:.2f}")
            col_res2.success(f"🙆‍♂️ Per Person: **${per_person:.2f}**")

# =================================================
# TAB 5~9: 공통 기능 (V30 유지)
# =================================================
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