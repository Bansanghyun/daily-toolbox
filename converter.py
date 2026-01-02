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

# 화면 넓게 쓰기 (Layout: Wide)
st.set_page_config(page_title="Daily Toolbox Pro", page_icon="🧰", layout="wide")


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

# ==========================================
# 🎨 사이드바 (메뉴 & 설정)
# ==========================================
with st.sidebar:
    st.title("🧰 Daily Toolbox")

    # 1. 언어 설정
    st.markdown("### 🌐 Language")
    lang = st.radio("언어 선택", ["🇰🇷 한국어", "🇺🇸 English"], label_visibility="collapsed")
    is_kor = lang == "🇰🇷 한국어"

    st.divider()

    # 2. 메인 메뉴 (요청하신 대로 불필요한 탭 삭제 & 핵심 기능 위주 배치)
    st.markdown("### 🚀 Menu")
    menu_options = [
        "☀️ 스마트 양생 (Concrete WX)",
        "🛡️ 안전 관리 (Safety)",
        "🛒 추천템 (Picks) 🔥",
        "📐 공학 계산 (Eng Calc)",
        "💰 생활/금융 (Life)",
        "📏 치수 변환 (Unit)",
        "🏗️ 자재/배관 (Material)",
        "🚦 호환성 (Compatibility)"
    ]
    selected_menu = st.radio("기능 선택", menu_options, label_visibility="collapsed")

    st.divider()

    # 3. 후원
    st.markdown("### ☕ Support")
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
    st.caption("shban127@gmail.com")

# ==========================================
# 📺 메인 화면 (기능별 상세 로직 복구 완료)
# ==========================================

# 1. ☀️ 스마트 양생
if "스마트 양생" in selected_menu:
    if is_kor:
        st.header("☀️ 스마트 콘크리트 양생 관리")
        st.caption("ACI 305R/306R 기반. 지역명 입력 시 날씨 자동 연동")
        with st.container(border=True):
            col_search, col_btn = st.columns([3, 1])
            loc_input = col_search.text_input("위치 검색 (예: Atlanta, 30303)", placeholder="City or ZIP")
            if col_btn.button("🔍 날씨 가져오기", use_container_width=True):
                if loc_input:
                    with st.spinner("Loading..."):
                        t, h, w, err = get_weather_data(loc_input)
                        if err:
                            st.error("위치를 찾을 수 없습니다.")
                        else:
                            st.session_state.temp_val = t
                            st.session_state.humid_val = int(h)
                            st.session_state.wind_val = w
                            st.success(f"✅ 로딩 완료: {loc_input}")
            c1, c2, c3 = st.columns(3)
            temp_f = c1.number_input("기온 (Temp °F)", value=st.session_state.temp_val, format="%.1f")
            humid = c2.number_input("습도 (Humidity %)", value=st.session_state.humid_val)
            wind = c3.number_input("풍속 (Wind mph)", value=st.session_state.wind_val)
            st.caption(f"🌡️ 변환 온도: {(temp_f - 32) * 5 / 9:.1f}°C")

        evap_rate = calc_evaporation_rate((temp_f - 32) * 5 / 9, humid, wind)
        st.subheader("📊 분석 결과")
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown("**1. 온도 기준**")
                if temp_f < 40:
                    st.error("❄️ **한중 (Cold)**\n\n40°F 미만! 보온 필수");
                elif temp_f > 90:
                    st.error("🔥 **서중 (Hot)**\n\n90°F 초과! 쿨링 필요");
                else:
                    st.success("✅ **적정 (Good)**\n\n40°F ~ 90°F")
        with c2:
            with st.container(border=True):
                st.markdown("**2. 균열 위험도**")
                st.metric("증발률", f"{evap_rate:.3f}", "lb/ft²/hr")
                if evap_rate > 0.2:
                    st.error("🚨 **위험 (Critical)**\n\n즉시 균열 위험! 방풍막/포깅")
                elif evap_rate > 0.1:
                    st.warning("⚠️ **주의 (Caution)**\n\n모니터링 강화")
                else:
                    st.success("✅ **안전 (Safe)**")
    else:
        st.header("☀️ Concrete Curing Manager")
        st.caption("ACI 305R/306R Standards.")
        with st.container(border=True):
            col_search, col_btn = st.columns([3, 1])
            loc_input = col_search.text_input("Search Location", placeholder="City or ZIP")
            if col_btn.button("🔍 Get Weather"):
                if loc_input:
                    with st.spinner("Fetching..."):
                        t, h, w, err = get_weather_data(loc_input)
                        if err:
                            st.error("Location not found.")
                        else:
                            st.session_state.temp_val = t
                            st.session_state.humid_val = int(h)
                            st.session_state.wind_val = w
                            st.success(f"✅ Loaded: {loc_input}")
            c1, c2, c3 = st.columns(3)
            temp_f = c1.number_input("Temp (°F)", value=st.session_state.temp_val, format="%.1f")
            humid = c2.number_input("Humidity (%)", value=st.session_state.humid_val)
            wind = c3.number_input("Wind (mph)", value=st.session_state.wind_val)

        evap_rate = calc_evaporation_rate((temp_f - 32) * 5 / 9, humid, wind)
        st.subheader("📊 Analysis")
        c1, c2 = st.columns(2)
        with c1:
            if temp_f < 40:
                st.error("❄️ **Cold Weather**\n\nProtection required");
            elif temp_f > 90:
                st.error("🔥 **Hot Weather**\n\nCooling required");
            else:
                st.success("✅ **Good**")
        with c2:
            st.metric("Evaporation Rate", f"{evap_rate:.3f}")
            if evap_rate > 0.2:
                st.error("🚨 **CRITICAL**");
            elif evap_rate > 0.1:
                st.warning("⚠️ **CAUTION**");
            else:
                st.success("✅ **SAFE**")

# 2. 🛡️ 안전 관리 (V37 기능 복구)
elif "안전" in selected_menu:
    st.header("🛡️ 안전 관리 (Safety Manager)")
    if is_kor:
        tab1, tab2 = st.tabs(["📋 JHA 생성기", "🛑 치명적 위험 점검"])
        with tab1:
            st.subheader("📋 JHA (Job Hazard Analysis)")
            work_type = st.selectbox("작업 종류", ["용접/절단 (Hot Work)", "고소 작업 (Working at Heights)", "중량물 인양 (Lifting)",
                                               "굴착 (Excavation)"])
            jha_db = {
                "용접/절단 (Hot Work)": ("Fire, Fumes, Burns",
                                     "1. Hot Work Permit.\n2. Fire Extinguisher (30ft).\n3. Fire Watch.\n4. Face Shield."),
                "고소 작업 (Working at Heights)": ("Falls, Falling objects",
                                               "1. 100% Tie-off (>6ft).\n2. Inspect Harness.\n3. Secure tools.\n4. Check Lift."),
                "중량물 인양 (Lifting)": ("Dropped load, Swing",
                                     "1. Barricade area.\n2. Inspect Rigging.\n3. Tag lines.\n4. No standing under load."),
                "굴착 (Excavation)": (
                "Cave-ins, Utilities", "1. Call 811.\n2. Trench Box (>5ft).\n3. Spoil pile 2ft back.\n4. Barricades.")
            }
            h, c = jha_db[work_type]
            with st.container(border=True):
                st.warning(f"**⚠️ 위험 요인 (Hazards):**\n{h}")
                st.success(f"**✅ 안전 대책 (Controls):**\n{c}")

        with tab2:
            st.subheader("🛑 Life Critical Checklist")
            check = st.selectbox("점검 항목", ["추락 (Fall)", "전기 (Electrical)", "LOTO"])
            with st.container(border=True):
                if "추락" in check:
                    st.markdown("- [ ] 6ft 이상 100% 체결했는가?\n- [ ] 리프트 문을 닫았는가?\n- [ ] 안전벨트 파손이 없는가?")
                    st.error("🚨 위반 시 즉시 퇴출 (Kick-out)")
                elif "전기" in check:
                    st.markdown("- [ ] 모든 공구 GFCI 사용 중인가?\n- [ ] 전선 피복 상태 양호한가?\n- [ ] 분전반 앞 36인치 확보되었는가?")
                elif "LOTO" in check:
                    st.markdown("- [ ] 자물쇠/태그가 체결되었는가?\n- [ ] 대장에 기록되었는가?\n- [ ] 열쇠를 본인이 소지했는가?")
    else:
        # English simple version
        st.subheader("Safety Tools")
        st.info("Switch to Korean mode for detailed Safety Checklist.")

# 3. 🛒 추천템 (링크 4개 적용)
elif "추천템" in selected_menu:
    # ▼▼▼ 링크 4개 적용 완료 ▼▼▼
    link_boot = "https://amzn.to/3YkSN1g"
    link_glass = "https://amzn.to/3LgnNMS"
    link_laser = "https://amzn.to/4smcR0J"
    link_tool = "https://amzn.to/3YQyn02"

    st.header("🛒 PM's Pick: 현장 필구템")
    st.markdown("미국 현장 엔지니어가 검증한 **OSHA/ANSI 인증** 베스트셀러")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### 🥾 안전화 대장")
            st.caption("Timberland PRO (Waterproof)")
            st.markdown("미국 현장 국룰. 방수/절연/편안함.")
            st.link_button("👉 아마존 최저가 확인", link_boot, use_container_width=True)
    with col2:
        with st.container(border=True):
            st.markdown("### 👓 김서림 방지 고글")
            st.caption("DeWalt Anti-Fog")
            st.markdown("습기 안 차는 고글. 배터리 공장 필수.")
            st.link_button("👉 아마존 최저가 확인", link_glass, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        with st.container(border=True):
            st.markdown("### 📏 그린 레이저 레벨")
            st.caption("Klein Tools Green Cross-Line")
            st.markdown("전기/설비팀 필수. 시인성 최고.")
            st.link_button("👉 아마존 최저가 확인", link_laser, use_container_width=True)
    with col4:
        with st.container(border=True):
            st.markdown("### 🧰 끝판왕 공구세트")
            st.caption("DeWalt 247pc Mechanics Set")
            st.markdown("이거 하나면 현장/정비 끝. 가성비 갑.")
            st.link_button("👉 아마존 최저가 확인", link_tool, use_container_width=True)

# 4. 공학 계산 (로직 100% 복구)
elif "공학" in selected_menu:
    st.header("📐 공학 계산기")

    # 탭으로 서브 메뉴 구성 (더 깔끔하게)
    sub_tabs = st.tabs(["🔧 볼트 토크", "📉 배관 구배", "🏗️ 크레인 양중", "⚡ 트레이 채움률"])

    with sub_tabs[0]:  # 볼트
        st.subheader("🔧 볼트 체결 토크 (A325/A490)")
        c1, c2 = st.columns(2)
        sz = c1.selectbox("Size", ["1/2", "5/8", "3/4", "7/8", "1"])
        gr = c2.selectbox("Grade", ["A325", "A490"])
        tdb = {"A325": {"1/2": 90, "5/8": 180, "3/4": 320, "7/8": 500, "1": 750},
               "A490": {"1/2": 110, "5/8": 220, "3/4": 390, "7/8": 600, "1": 900}}
        val = tdb.get(gr, {}).get(sz, 0)
        st.success(f"🎯 권장 토크: **{val} ft-lbs**")

    with sub_tabs[1]:  # 구배
        st.subheader("📉 배관 구배 계산")
        c1, c2 = st.columns(2)
        l = c1.number_input("길이 (ft)", 100.0)
        s = c2.select_slider("Slope (inch/ft)", ["1/8", "1/4", "1/2", "1"])
        sl_val = {"1/8": 0.125, "1/4": 0.25, "1/2": 0.5, "1": 1.0}[s]
        drop = l * sl_val
        st.info(f"⬇️ 높이 차이 (Drop): **{drop:.2f} inch** ({drop * 25.4:.1f} mm)")

    with sub_tabs[2]:  # 크레인
        st.subheader("🏗️ 크레인 부하 모멘트")
        c1, c2 = st.columns(2)
        w = c1.number_input("무게 (lbs)", 5000)
        r = c2.number_input("작업 반경 (ft)", 50)
        st.metric("Load Moment", f"{w * r:,.0f}", "lbs-ft")

    with sub_tabs[3]:  # 트레이
        st.subheader("⚡ 케이블 트레이 채움률")
        c1, c2, c3 = st.columns(3)
        w = c1.selectbox("폭 (Width)", [12, 18, 24, 30, 36])
        d = c2.selectbox("깊이 (Depth)", [4, 6])
        dia = c3.number_input("케이블 외경 (inch)", 1.0)
        cnt = st.slider("가닥수", 1, 100, 20)

        area_tray = w * d
        area_cable = (math.pi * (dia / 2) ** 2) * cnt
        ratio = (area_cable / area_tray) * 100

        st.metric("채움률 (Limit: 40%)", f"{ratio:.1f}%")
        if ratio > 40:
            st.error("❌ 초과 (Overfilled)")
        else:
            st.success("✅ 양호 (Pass)")

# 5. 생활/금융 (로직 100% 복구)
elif "생활" in selected_menu:
    st.header("💰 생활 & 금융")
    sub_tabs = st.tabs(["💱 환율", "💰 야근 비용", "💸 연봉 실수령", "⏰ 시차", "🍽️ 팁"])

    with sub_tabs[0]:  # 환율
        rate = 1450.0
        df = get_exchange_rate()
        if df is not None: rate = df['Close'].iloc[-1]

        c1, c2 = st.columns(2)
        c1.metric("USD/KRW", f"{rate:.1f} 원")
        usd = c2.number_input("달러 입력 ($)", 1000)
        c2.caption(f"≒ {int(usd * rate):,} 원")
        if df is not None: st.line_chart(df['Close'])

    with sub_tabs[1]:  # 야근
        st.subheader("💰 야근 비용 계산기")
        c1, c2 = st.columns(2)
        ppl = c1.number_input("인원 (명)", 5)
        rate_hr = c2.number_input("시급 ($)", 40.0)
        c3, c4 = st.columns(2)
        hrs = c3.number_input("시간 (hr)", 2.0)
        mul = c4.radio("배수", ["1.5배", "2.0배"], horizontal=True)
        m_val = 1.5 if "1.5" in mul else 2.0
        st.metric("총 비용", f"${ppl * rate_hr * hrs * m_val:,.0f}")

    with sub_tabs[2]:  # 연봉
        st.subheader("💸 연봉 실수령액 (Net Salary)")
        s = st.number_input("연봉 ($)", 80000, step=1000)
        tax = max(0, s - 14600) * 0.22  # 대략적 세율
        net = s - tax
        st.metric("월 실수령액 (예상)", f"${net / 12:,.0f}")

    with sub_tabs[3]:  # 시차
        st.subheader("🌏 글로벌 시차")
        tz_e = pytz.timezone('US/Eastern');
        tz_k = pytz.timezone('Asia/Seoul')
        now = datetime.now(tz_e)
        c1, c2 = st.columns(2)
        c1.metric("미국 동부 (ET)", now.strftime('%I:%M %p'))
        c2.metric("한국 (KST)", now.astimezone(tz_k).strftime('%I:%M %p'))

    with sub_tabs[4]:  # 팁
        st.subheader("🍽️ 팁 & 더치페이")
        bill = st.number_input("Bill ($)", 50.0)
        tip = st.slider("Tip %", 15, 25, 18)
        ppl = st.number_input("People", 1, 10, 1)
        total = bill * (1 + tip / 100)
        st.metric("인당 지불액", f"${total / ppl:.2f}")

# 6. 치수 변환 (복구)
elif "치수" in selected_menu:
    st.header("📏 치수 변환")
    c1, c2 = st.columns(2)
    with c1:
        mm = st.number_input("mm ➡️ ft-in", 1000)
        st.code(f"{mm / 25.4 / 12:.2f} ft")
    with c2:
        ft = st.number_input("ft ➡️ mm", 10)
        st.code(f"{ft * 304.8:.0f} mm")

# 7. 자재/배관 (복구)
elif "자재" in selected_menu:
    st.header("🏗️ 자재/배관")
    st.subheader("🚛 콘크리트 물량 변환")
    m3 = st.number_input("입방미터 (m³)", 10.0)
    st.metric("야드 (yd³)", f"{m3 * 1.308:.2f}")

# 8. 호환성 (복구)
elif "호환" in selected_menu:
    st.header("🚦 호환성 판독")
    tool = st.selectbox("Tool / Bolt", ["1/2 inch", "M12"])
    if "inch" in tool:
        st.error("⚠️ mm 공구 사용 금지! (규격 불일치)")
    else:
        st.success("✅ inch 공구 일부 호환 가능")