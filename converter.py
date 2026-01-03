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
    st.caption("Professional Engineering Kit")

    # 1. 언어 설정
    st.markdown("### 🌐 Language")
    lang = st.radio("언어 선택", ["🇰🇷 한국어", "🇺🇸 English"], label_visibility="collapsed")
    is_kor = lang == "🇰🇷 한국어"

    st.divider()

    # 2. 메인 메뉴 (아이콘 + 기능명)
    st.markdown("### 🚀 Menu")
    menu_options = [
        "☀️ 스마트 양생 (Concrete WX)",
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
    st.caption("Contact: shban127@gmail.com")

# ==========================================
# 📺 메인 화면
# ==========================================

# 1. ☀️ 스마트 양생
if "스마트 양생" in selected_menu:
    st.header("☀️ 스마트 콘크리트 양생 관리")
    st.caption("ACI 305R/306R Standard Based Curing Manager")

    col_main, col_res = st.columns([1, 1.2])  # 레이아웃 분할

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
                            st.session_state.temp_val = t
                            st.session_state.humid_val = int(h)
                            st.session_state.wind_val = w
                            st.success(f"✅ 로딩 완료: {loc_input}")

            st.divider()
            st.caption("또는 수동 입력")
            temp_f = st.number_input("기온 (Temp °F)", value=st.session_state.temp_val, format="%.1f")
            humid = st.number_input("습도 (Humidity %)", value=st.session_state.humid_val)
            wind = st.number_input("풍속 (Wind mph)", value=st.session_state.wind_val)

    with col_res:
        evap_rate = calc_evaporation_rate((temp_f - 32) * 5 / 9, humid, wind)
        temp_c = (temp_f - 32) * 5 / 9

        with st.container(border=True):
            st.markdown("#### 📊 분석 리포트")

            # 온도 분석
            st.markdown("**1. 온도 조건 (Temperature)**")
            c1, c2 = st.columns(2)
            c1.metric("섭씨 변환", f"{temp_c:.1f}°C")
            if temp_f < 40:
                c2.error("❄️ 한중 (Cold)")
                st.caption("🚨 40°F 미만! 보온 양생(Heating) 필수")
            elif temp_f > 90:
                c2.error("🔥 서중 (Hot)")
                st.caption("🚨 90°F 초과! 쿨링(Cooling) 대책 수립")
            else:
                c2.success("✅ 적정 (Good)")
                st.caption("양생하기 좋은 온도입니다.")

            st.divider()

            # 증발률 분석
            st.markdown("**2. 균열 위험도 (Evaporation Rate)**")
            st.metric("수분 증발률", f"{evap_rate:.3f}", "lb/ft²/hr")

            if evap_rate > 0.2:
                st.error("🚨 위험 (Critical) - 즉시 조치 필요")
                st.markdown("- 콘크리트 타설 즉시 **방풍막** 설치\n- **포깅(Fogging)** 장비 가동 필수")
            elif evap_rate > 0.1:
                st.warning("⚠️ 주의 (Caution) - 모니터링")
                st.markdown("- 표면 건조 주의, 양생제 도포 철저")
            else:
                st.success("✅ 안전 (Safe) - 작업 양호")

# 2. 🛡️ 안전 관리
elif "안전" in selected_menu:
    st.header("🛡️ 안전 관리 (Safety Manager)")

    tab1, tab2 = st.tabs(["📋 JHA 생성기", "🛑 치명적 위험 점검"])

    with tab1:
        st.caption("작업별 위험성 평가 및 대책 자동 생성")
        c1, c2 = st.columns([1, 2])

        with c1:
            with st.container(border=True):
                st.markdown("#### 작업 선택")
                work_type = st.radio("종류", ["용접/절단", "고소 작업", "중량물 인양", "굴착 작업"])

        with c2:
            jha_db = {
                "용접/절단": ("화재, 폭발, 흄, 화상",
                          "1. 화기작업 허가서 발행 (Hot Work Permit)\n2. 소화기 비치 (30ft 이내)\n3. 불티 비산 방지포 설치\n4. 화재 감시자(Fire Watch) 배치"),
                "고소 작업": ("추락, 낙하물, 장비 전도",
                          "1. 6ft 이상 100% 체결 (Tie-off)\n2. 안전벨트/고리 사전 점검\n3. 공구 낙하방지 끈 사용\n4. 리프트 작동 상태 점검"),
                "중량물 인양": ("낙하, 협착, 장비 파손",
                           "1. 인양 반경 내 접근 금지 구획 설정\n2. 리깅 도구(슬링/샤클) 점검\n3. 유도 로프(Tag line) 사용\n4. 하부 통행 절대 금지"),
                "굴착 작업": ("붕괴, 매설물 파손",
                          "1. 굴착 전 811 신고 (매설물 확인)\n2. 5ft 이상 시 흙막이(Trench Box) 설치\n3. 굴착 토사 2ft 이상 이격 적재")
            }
            h, c = jha_db[work_type]

            with st.container(border=True):
                st.markdown(f"#### 📄 {work_type} JHA")
                st.warning(f"**⚠️ 위험 요인 (Hazards)**\n\n{h}")
                st.success(f"**✅ 안전 대책 (Controls)**\n\n{c}")

    with tab2:
        st.caption("Zero Tolerance: 위반 시 즉시 퇴출 항목 점검")
        col_check, col_guide = st.columns([1, 1.5])

        with col_check:
            with st.container(border=True):
                st.markdown("#### 점검 대상")
                check = st.radio("항목", ["추락 (Fall)", "전기 (Electrical)", "LOTO (잠금)"])

        with col_guide:
            with st.container(border=True):
                if "추락" in check:
                    st.error("🚨 추락 위험 (Fall Protection)")
                    st.markdown("""
                    - [ ] **6ft(1.8m) 이상 높이**에서 안전고리를 체결했는가?
                    - [ ] 고소작업대(Lift) **출입문**을 닫았는가?
                    - [ ] 안전벨트 웨빙에 **손상**이 없는가?
                    """)
                elif "전기" in check:
                    st.warning("⚡ 전기 위험 (Electrical Safety)")
                    st.markdown("""
                    - [ ] 모든 전동 공구에 **GFCI**를 사용 중인가?
                    - [ ] 전선(Cord)의 **피복**이 벗겨지지 않았는가?
                    - [ ] 분전반 앞 **36인치(90cm)** 공간이 확보되었는가?
                    """)
                elif "LOTO" in check:
                    st.info("🔐 잠금장치 (Hazardous Energy)")
                    st.markdown("""
                    - [ ] 에너지원에 **자물쇠와 태그**가 있는가?
                    - [ ] LOTO 대장에 **기록**되었는가?
                    - [ ] **열쇠**를 작업자 본인이 소지했는가?
                    """)

# 3. 🛒 추천템
elif "추천템" in selected_menu:
    st.header("🛒 PM's Pick: 현장 필구템")
    st.caption("OSHA/ANSI 규격 만족 & 아마존 베스트셀러 엄선")

    link_boot = "https://amzn.to/3YkSN1g"
    link_glass = "https://amzn.to/3LgnNMS"
    link_laser = "https://amzn.to/4smcR0J"
    link_tool = "https://amzn.to/3YQyn02"

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        with st.container(border=True):
            st.image("https://m.media-amazon.com/images/I/81+F-wV-QLL._AC_SY695_.jpg",
                     caption="Timberland PRO")  # 이미지 예시 (실제론 안 뜰 수도 있음)
            st.markdown("**🥾 안전화 대장**")
            st.caption("방수/절연/편안함")
            st.link_button("👉 최저가 보기", link_boot, use_container_width=True)

    with c2:
        with st.container(border=True):
            st.markdown("**👓 안티포그 고글**")
            st.caption("DeWalt (김서림 방지)")
            st.write("배터리 공장 필수")
            st.link_button("👉 최저가 보기", link_glass, use_container_width=True)

    with c3:
        with st.container(border=True):
            st.markdown("**📏 그린 레이저**")
            st.caption("Klein Tools")
            st.write("전기/설비팀 추천")
            st.link_button("👉 최저가 보기", link_laser, use_container_width=True)

    with c4:
        with st.container(border=True):
            st.markdown("**🧰 끝판왕 공구**")
            st.caption("DeWalt 247pcs")
            st.write("현장 정비용 세트")
            st.link_button("👉 최저가 보기", link_tool, use_container_width=True)

# 4. 🚦 호환성
elif "호환" in selected_menu:
    st.header("🚦 호환성 판독 (Compatibility)")
    st.caption("현장에서 가장 헷갈리는 규격 호환 여부 판독기")

    comp_tabs = st.tabs(["🔧 렌치/소켓", "🔩 배관 나사", "🔘 플랜지"])

    with comp_tabs[0]:
        c1, c2 = st.columns([1, 2])
        with c1:
            with st.container(border=True):
                st.markdown("#### 인치 규격 입력")
                inch_size = st.selectbox("Size",
                                         ["5/16\"", "3/8\"", "7/16\"", "1/2\"", "9/16\"", "5/8\"", "3/4\"", "7/8\"",
                                          "15/16\"", "1\""])

        with c2:
            match_db = {
                "5/16\"": ("8mm", "✅ 완벽 호환 (Perfect)"),
                "3/8\"": ("10mm", "❌ 사용 불가 (9.5mm vs 10mm 헛돔)"),
                "7/16\"": ("11mm", "⚠️ 헐거움 (Loose) - 비상시만"),
                "1/2\"": ("13mm", "✅ 사용 가능 (12.7mm vs 13mm)"),
                "9/16\"": ("14mm", "✅ 사용 가능 (14.2mm vs 14mm 꽉 낌)"),
                "5/8\"": ("16mm", "✅ 사용 가능 (15.8mm vs 16mm)"),
                "3/4\"": ("19mm", "✅ 완벽 호환 (Perfect)"),
                "7/8\"": ("22mm", "✅ 사용 가능 (22.2mm vs 22mm)"),
                "15/16\"": ("24mm", "✅ 완벽 호환 (Perfect)"),
                "1\"": ("25mm", "❌ 사용 불가 (25.4mm vs 25mm 안 들어감)")
            }
            res_mm, res_msg = match_db[inch_size]

            with st.container(border=True):
                st.markdown("#### 🔍 판독 결과")
                st.metric("대체 가능 mm 공구", res_mm)
                if "✅" in res_msg:
                    st.success(res_msg)
                elif "⚠️" in res_msg:
                    st.warning(res_msg)
                else:
                    st.error(res_msg)

    with comp_tabs[1]:
        with st.container(border=True):
            st.markdown("#### 🔩 NPT(미국) vs PT(한국) 배관")
            c1, c2 = st.columns(2)
            c1.error("🚫 호환 불가")
            c1.write("억지로 끼우면 100% 누수 발생")
            c2.info("💡 해결책")
            c2.write("반드시 **변환 어댑터** 사용")
            st.divider()
            st.markdown("- **NPT**: 60도 나사산 (미국 표준)\n- **PT(BSP)**: 55도 나사산 (한국/유럽 표준)")

    with comp_tabs[2]:
        with st.container(border=True):
            st.markdown("#### 🔘 ANSI vs JIS 플랜지")
            st.warning("⚠️ 호환 불가 (볼트 구멍 안 맞음)")
            st.write("미국 ANSI 150#와 한국 JIS 10K는 볼트 구멍 간격(PCD)이 미세하게 달라서 볼트가 들어가지 않습니다.")

# 5. 공학 계산
elif "공학" in selected_menu:
    st.header("📐 공학 계산기")

    sub_tabs = st.tabs(["🔧 볼트 토크", "📉 배관 구배", "🏗️ 크레인", "⚡ 케이블 트레이"])

    with sub_tabs[0]:
        with st.container(border=True):
            st.markdown("#### 볼트 적정 토크 (AISC)")
            c1, c2 = st.columns(2)
            sz = c1.selectbox("볼트 직경", ["1/2", "5/8", "3/4", "7/8", "1"])
            gr = c2.selectbox("등급 (Grade)", ["A325", "A490"])
            tdb = {"A325": {"1/2": 90, "5/8": 180, "3/4": 320, "7/8": 500, "1": 750},
                   "A490": {"1/2": 110, "5/8": 220, "3/4": 390, "7/8": 600, "1": 900}}
            st.divider()
            st.success(f"🎯 권장 토크: **{tdb.get(gr, {}).get(sz, 0)} ft-lbs**")

    with sub_tabs[1]:
        with st.container(border=True):
            st.markdown("#### 배관 높이 차이 (Drop)")
            c1, c2 = st.columns(2)
            l = c1.number_input("배관 길이 (ft)", 100.0)
            s = c2.select_slider("구배 (Slope)", ["1/8", "1/4", "1/2", "1"])
            drop = l * {"1/8": 0.125, "1/4": 0.25, "1/2": 0.5, "1": 1.0}[s]
            st.divider()
            st.info(f"⬇️ 높이 차이: **{drop:.2f} inch** ({drop * 25.4:.1f} mm)")

    with sub_tabs[2]:
        with st.container(border=True):
            st.markdown("#### 크레인 부하 모멘트")
            c1, c2 = st.columns(2)
            w = c1.number_input("인양 무게 (lbs)", 5000)
            r = c2.number_input("작업 반경 (ft)", 50)
            st.divider()
            st.metric("Load Moment", f"{w * r:,.0f} lbs-ft")

    with sub_tabs[3]:
        with st.container(border=True):
            st.markdown("#### 트레이 채움률 계산")
            c1, c2, c3 = st.columns(3)
            w = c1.selectbox("폭 (Width)", [12, 18, 24, 30, 36])
            d = c2.selectbox("깊이 (Depth)", [4, 6])
            dia = c3.number_input("케이블 외경 (inch)", 1.0)
            cnt = st.slider("가닥수", 1, 100, 20)

            ratio = ((math.pi * (dia / 2) ** 2) * cnt / (w * d)) * 100
            st.divider()
            st.metric("현재 채움률", f"{ratio:.1f}%", "Limit: 40%")
            if ratio > 40:
                st.error("❌ 초과 (Overfilled)")
            else:
                st.success("✅ 적합 (Pass)")

# 6. 생활/금융
elif "생활" in selected_menu:
    st.header("💰 생활 & 금융")

    sub_tabs = st.tabs(["💱 환율/시차", "💰 야근 비용", "💸 연봉 계산", "🍽️ 팁 계산"])

    with sub_tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown("#### 💱 실시간 환율")
                rate = 1450.0
                df = get_exchange_rate()
                if df is not None: rate = df['Close'].iloc[-1]
                st.metric("USD/KRW", f"{rate:.1f} 원")
                usd = st.number_input("달러 ($)", 1000)
                st.caption(f"≒ {int(usd * rate):,} 원")
        with c2:
            with st.container(border=True):
                st.markdown("#### ⏰ 시차 확인")
                tz_e = pytz.timezone('US/Eastern');
                tz_k = pytz.timezone('Asia/Seoul')
                now = datetime.now(tz_e)
                st.metric("🇺🇸 미국 동부", now.strftime('%I:%M %p'))
                st.metric("🇰🇷 한국", now.astimezone(tz_k).strftime('%I:%M %p'))

    with sub_tabs[1]:
        with st.container(border=True):
            st.markdown("#### 💰 야근 비용 시뮬레이션")
            c1, c2 = st.columns(2)
            ppl = c1.number_input("투입 인원 (명)", 5)
            rate_hr = c2.number_input("평균 시급 ($)", 40.0)
            c3, c4 = st.columns(2)
            hrs = c3.number_input("추가 시간 (hr)", 2.0)
            mul = c4.radio("할증", ["1.5배", "2.0배"], horizontal=True)
            m_val = 1.5 if "1.5" in mul else 2.0
            st.divider()
            st.metric("예상 추가 비용", f"${ppl * rate_hr * hrs * m_val:,.0f}")

    with sub_tabs[2]:
        with st.container(border=True):
            st.markdown("#### 💸 연봉 실수령액 (Net)")
            s = st.number_input("계약 연봉 ($)", 80000, step=1000)
            net = s - (max(0, s - 14600) * 0.22)  # 단순화된 세율
            st.divider()
            st.metric("월 예상 수령액", f"${net / 12:,.0f}")

    with sub_tabs[3]:
        with st.container(border=True):
            st.markdown("#### 🍽️ 팁 & 더치페이")
            c1, c2 = st.columns(2)
            bill = c1.number_input("청구 금액 ($)", 50.0)
            tip = c2.slider("팁 비율 (%)", 15, 25, 18)
            ppl = st.number_input("인원 수", 1)
            total = bill * (1 + tip / 100)
            st.divider()
            st.metric("1인당 지불액", f"${total / ppl:.2f}")

# 7. 치수 변환
elif "치수" in selected_menu:
    st.header("📏 치수 변환 (Unit Converter)")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("#### mm ➡️ ft-in")
            mm = st.number_input("mm 입력", 1000)
            st.success(f"**{mm / 25.4 / 12:.2f} ft**")
    with c2:
        with st.container(border=True):
            st.markdown("#### ft ➡️ mm")
            ft = st.number_input("ft 입력", 10)
            st.info(f"**{ft * 304.8:.0f} mm**")

# 8. 자재/배관
elif "자재" in selected_menu:
    st.header("🏗️ 자재/배관")
    with st.container(border=True):
        st.markdown("#### 🚛 레미콘 물량 변환")
        c1, c2 = st.columns(2)
        m3 = c1.number_input("루베 (m³)", 10.0)
        c2.metric("야드 (yd³)", f"{m3 * 1.308:.2f}")