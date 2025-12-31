import streamlit as st
import streamlit.components.v1 as components  # 👈 애널리틱스용 필수 부품 추가
import pandas as pd
import math
from datetime import datetime
import pytz

# yfinance 안전 로딩
try:
    import yfinance as yf

    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

# --- 페이지 설정 ---
st.set_page_config(page_title="데일리 툴박스", page_icon="🧰", layout="centered")


# ==========================================
# 🕵️‍♂️ 구글 애널리틱스 추적 코드 (수정버전)
# ==========================================
def inject_ga():
    GA_ID = "G-4460NPEL99"  # PM님 ID 확인 완료

    # 설정 변경: iframe 안에서도 쿠키가 작동하도록 'cookie_flags' 추가
    ga_code = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        
        // ⚠️ 중요: Streamlit Iframe 환경을 위한 쿠키 설정 추가
        gtag('config', '{GA_ID}', {{
            'cookie_flags': 'SameSite=None;Secure'
        }});
    </script>
    """
    
    # height=0으로 두면 가끔 실행 안 될 때가 있어서 1px로 설정 후 숨김 처리
    components.html(ga_code, height=1)

# 앱 실행
inject_ga()

# ==========================================

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


# --- 사이드바 ---
with st.sidebar:
    st.header("🌐 언어 설정 (Language)")
    lang = st.radio("Select Language", ["🇰🇷 한국어", "🇺🇸 English"])
    is_kor = lang == "🇰🇷 한국어"

    st.divider()

    # 💰 후원 섹션
    st.subheader("☕ Support")
    if is_kor:
        st.caption("개발자에게 커피 한 잔 후원하기")
    else:
        st.caption("Support the developer!")

    # 1. Buy Me a Coffee
    bmc_link = "https://www.buymeacoffee.com/vvaann"
    st.markdown(
        f"""
        <a href="{bmc_link}" target="_blank">
            <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 100% !important;" >
        </a>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    # 2. PayPal
    # ▼▼▼ [수정] 페이팔 주소 확인! ▼▼▼
    paypal_url = "https://www.paypal.com/paypalme/SanghyunBan"

    btn_text = "💳 PayPal로 후원하기" if is_kor else "💳 Donate with PayPal"
    st.markdown(
        f"""
        <a href="{paypal_url}" target="_blank">
            <button style="
                background-color: #0070BA; color: white; border: none; padding: 10px; 
                border-radius: 5px; font-weight: bold; cursor: pointer; width: 100%; font-family: sans-serif;">
                {btn_text}
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # 연락처 & 법적 고지
    st.subheader("📧 Contact")
    st.caption("비즈니스/기능 제안")
    st.code("shban127@gmail.com")

    with st.expander("⚠️ 법적 고지 / Disclaimer", expanded=True):
        if is_kor:
            st.markdown("**[면책 조항]**\n본 앱의 결과는 참고용이며, 시공 및 안전에 대한 최종 책임은 사용자에게 있습니다.")
        else:
            st.markdown("**[Disclaimer]**\nCalculations are for Reference Only. The developer assumes NO liability.")


# --- 유틸리티 함수 ---
def mm_to_feet_inch_fraction(mm_val):
    if mm_val == 0: return "0' 0\""
    total_inches = mm_val / 25.4
    feet = int(total_inches // 12)
    inches = int(total_inches % 12)
    remainder = total_inches - (feet * 12) - inches
    numerator = round(remainder * 16)
    if numerator == 16: inches += 1; numerator = 0
    if inches == 12: feet += 1; inches = 0
    fraction_str = ""
    if numerator > 0:
        if numerator % 8 == 0:
            fraction_str = "-1/2"
        elif numerator % 4 == 0:
            fraction_str = f"-{numerator // 4}/4"
        elif numerator % 2 == 0:
            fraction_str = f"-{numerator // 2}/8"
        else:
            fraction_str = f"-{numerator}/16"
    return f"{feet}' {inches}{fraction_str}\""


# --- 메인 타이틀 ---
if is_kor:
    st.title("🧰 데일리 툴박스 (US)")
    st.markdown("현장 치수 변환부터 **공학 계산, 업무 보고**까지!")
    tab_names = ["🗣️ 소통/영어", "📐 공학 계산", "💰 생활/금융", "📏 치수 변환", "🏗️ 자재/배관", "🚦 호환성", "📋 규격표", "📧 보고서", "💡 기능 제안"]
else:
    st.title("🧰 The Daily Toolbox")
    st.markdown("Your essential kit: Eng Calc, Conversions, and Reports.")
    tab_names = ["🗣️ Comm", "📐 Eng Calc", "💰 Life", "📏 Dim", "🏗️ Mat", "🚦 Comp", "📋 Charts", "📧 Report", "💡 Feedback"]

# 탭 생성
tab_comm, tab_eng, tab_life, tab_dim, tab_mat, tab_comp, tab_chart, tab_rpt, tab_feed = st.tabs(tab_names)

# =================================================
# TAB 1: 소통/영어
# =================================================
with tab_comm:
    if is_kor:
        comm_type = st.radio("기능 선택", ["📻 무전 용어", "📖 건설 약어", "📧 이메일 템플릿"], horizontal=True)
    else:
        comm_type = st.radio("Select Tool", ["📻 Radio Terms", "📖 Acronyms", "📧 Email Templates"], horizontal=True)
    st.divider()

    if "Radio" in comm_type or "무전" in comm_type:
        st.subheader("📻 필수 무전 용어 가이드")
        radio_data = [
            {"Term": "10-4", "Meaning (KR)": "알겠다 / 수신 양호", "Meaning (US)": "OK / Message Received"},
            {"Term": "Copy that", "Meaning (KR)": "내용 이해함", "Meaning (US)": "Understood"},
            {"Term": "What's your 20?", "Meaning (KR)": "현재 위치?", "Meaning (US)": "Where are you?"},
            {"Term": "Go ahead", "Meaning (KR)": "말해라 (수신 대기)", "Meaning (US)": "Ready to listen"},
            {"Term": "Stand by", "Meaning (KR)": "잠시 대기", "Meaning (US)": "Wait a moment"},
            {"Term": "Radio Check", "Meaning (KR)": "무전기 잘 들리나?", "Meaning (US)": "Can you hear me?"}
        ]
        st.table(pd.DataFrame(radio_data))

    elif "Acronyms" in comm_type or "약어" in comm_type:
        st.subheader("📖 건설 현장 약어 사전")
        acronyms = [
            {"Abbr": "RFI", "Full Name": "Request for Information", "Note": "설계 질의서"},
            {"Abbr": "CO", "Full Name": "Change Order", "Note": "설계 변경"},
            {"Abbr": "NTP", "Full Name": "Notice to Proceed", "Note": "착공 지시서"},
            {"Abbr": "MEP", "Full Name": "Mechanical, Electrical, Plumbing", "Note": "기계/전기/배관"},
            {"Abbr": "TBM", "Full Name": "Toolbox Meeting", "Note": "안전 조회"},
            {"Abbr": "IFC", "Full Name": "Issued for Construction", "Note": "시공용 도면"}
        ]
        df_acro = pd.DataFrame(acronyms)
        search = st.text_input("약어 검색 (예: RFI)" if is_kor else "Search Acronym (e.g. RFI)")
        if search: df_acro = df_acro[df_acro["Abbr"].str.contains(search.upper())]
        st.dataframe(df_acro, hide_index=True, use_container_width=True)

    elif "Email" in comm_type or "이메일" in comm_type:
        st.subheader("📧 비즈니스 이메일 생성기")
        situation = st.selectbox("상황 선택", ["자재 지연 (Delay)", "검측 요청 (Inspection)", "도면 질의 (RFI)"])
        c1, c2 = st.columns(2)
        recipient = c1.text_input("수신자 (To)", "Mr. Smith");
        my_name = c2.text_input("발신자 (From)", "PM Kim")
        detail = st.text_input("상세 내용", "Piping Material")

        if st.button("이메일 생성"):
            if "Delay" in situation:
                body = f"Dear {recipient},\n\nWriting to inform you of a delay regarding **{detail}** due to supply issues.\nWe expect it by [Date].\n\nRegards,\n{my_name}"
            elif "Inspection" in situation:
                body = f"Dear {recipient},\n\nInstallation of **{detail}** is complete.\nRequesting official inspection.\n\nRegards,\n{my_name}"
            else:
                body = f"Dear {recipient},\n\nWe have a question regarding **{detail}**.\nPlease review attached RFI.\n\nRegards,\n{my_name}"
            st.code(body)

# =================================================
# TAB 2: 공학 계산
# =================================================
with tab_eng:
    if is_kor:
        st.error("⚠️ 주의: 본 계산 결과는 단순 참고용입니다. 시공 전 반드시 공식 도면을 확인하세요.")
    else:
        st.error("⚠️ Warning: Calculations are for reference only. Verify with official drawings.")

    if is_kor:
        eng_menu = st.radio("계산기 선택", ["📉 배관/덕트 구배", "⚡ 케이블 트레이 채움률", "🏗️ 크레인 양중"], horizontal=True)
    else:
        eng_menu = st.radio("Select Tool", ["📉 Slope Calc", "⚡ Tray Fill Ratio", "🏗️ Crane Lift Check"],
                            horizontal=True)
    st.divider()

    if "구배" in eng_menu or "Slope" in eng_menu:
        st.subheader("📉 구배 높이차 계산")
        c1, c2 = st.columns(2)
        length_ft = c1.number_input("설치 길이 (ft)", 50.0, step=5.0)
        slope_sel = c2.selectbox("구배 기준", ["1/8\" per foot", "1/4\" per foot", "1/2\" per foot", "1\" per foot"])
        slope_val = {"1/8": 0.125, "1/4": 0.25, "1/2": 0.5, "1\"": 1.0}
        key = slope_sel.split('"')[0]
        drop_inch = length_ft * slope_val.get(key, 0.125)
        cc1, cc2 = st.columns(2)
        cc1.metric("높이 차이 (Inch)", f"{drop_inch:.2f}\"")
        cc2.metric("높이 차이 (mm)", f"{drop_inch * 25.4:.1f} mm")

    elif "트레이" in eng_menu or "Tray" in eng_menu:
        st.subheader("⚡ 트레이 채움률 (40% 기준)")
        c1, c2 = st.columns(2)
        w = c1.selectbox("폭 (Width)", [6, 12, 18, 24, 30, 36])
        d = c2.selectbox("깊이 (Depth)", [4, 6])
        area_total = w * d
        cc1, cc2 = st.columns(2)
        dia = cc1.number_input("케이블 외경 (inch)", 1.0, step=0.1)
        cnt = cc2.number_input("가닥수", 10)
        ratio = ((math.pi * ((dia / 2) ** 2)) * cnt / area_total) * 100
        col_res1, col_res2 = st.columns(2)
        col_res1.metric("현재 채움률", f"{ratio:.1f}%")
        col_res2.metric("허용 면적 (40%)", f"{area_total * 0.4:.1f} sq in")
        if ratio > 40:
            st.error("🔴 규정 위반 (Overfilled)")
        elif ratio > 35:
            st.warning("🟡 주의 (Near Limit)")
        else:
            st.success("🟢 양호 (Pass)")

    elif "크레인" in eng_menu or "Crane" in eng_menu:
        st.subheader("🏗️ 크레인 양중 검토")
        c1, c2 = st.columns(2)
        weight = c1.number_input("무게 (lbs)", 5000.0, step=500.0)
        radius = c2.number_input("작업 반경 (ft)", 50.0, step=5.0)
        st.metric("예상 부하 모멘트", f"{weight * radius:,.0f} lbs-ft")
        st.info("※ 참고용 단순 계산입니다. 실제 양중 계획(Lift Plan)을 따르세요.")

# =================================================
# TAB 3: 생활/금융
# =================================================
with tab_life:
    if is_kor:
        life_menu = st.radio("메뉴", ["💱 실시간 환율", "⏰ 한-미 시차", "💸 연봉 실수령액", "🍽️ 팁 & 더치페이", "🍕 피자 가성비"], horizontal=True)
    else:
        life_menu = st.radio("Menu", ["💱 Exchange Rate", "⏰ Timezone", "💸 Net Salary", "🍽️ Tip Calc", "🍕 Pizza Math"],
                             horizontal=True)
    st.divider()

    if "Exchange" in life_menu or "환율" in life_menu:
        st.subheader("💱 원/달러 환율 (USD/KRW)")
        df_rate = get_exchange_rate()
        if df_rate is not None:
            curr = df_rate['Close'].iloc[-1];
            prev = df_rate['Close'].iloc[-2]
            c1, c2 = st.columns([1, 2])
            c1.metric("현재 환율", f"{curr:.2f} 원", f"{curr - prev:.2f} 원")
            if is_kor: c2.caption("데이터: 야후 파이낸스")
            st.line_chart(df_rate['Close'])
            calc_rate = curr
        else:
            if is_kor: st.warning("⚠️ 인터넷 연결 실패. 수동 입력해주세요.")
            calc_rate = st.number_input("환율 직접 입력 (원)", 1450.0)

        st.markdown("##### 💵 간편 환전")
        c1, c2 = st.columns(2)
        u_in = c1.number_input("달러 (USD)", 1000.0)
        c2.metric("원화 (KRW)", f"{int(u_in * calc_rate):,} 원")

    elif "Time" in life_menu or "시차" in life_menu:
        st.subheader("🌏 글로벌 시차 확인")
        if is_kor:
            base_loc = st.radio("내 위치", ["미국 동부", "미국 서부"], horizontal=True)
        else:
            base_loc = st.radio("Loc", ["Eastern", "Pacific"], horizontal=True)
        tz_e = pytz.timezone('US/Eastern');
        tz_w = pytz.timezone('US/Pacific');
        tz_k = pytz.timezone('Asia/Seoul')
        base_tz = tz_e if "동부" in base_loc or "Eastern" in base_loc else tz_w
        now = datetime.now(base_tz)
        offset = st.slider("시간 조절", 0, 23, now.hour)
        target = now.replace(hour=offset, minute=0, second=0)
        c1, c2, c3 = st.columns(3)
        c1.metric("서부 (PT)", target.astimezone(tz_w).strftime('%I:%M %p'))
        c2.metric("동부 (ET)", target.astimezone(tz_e).strftime('%I:%M %p'))
        c3.metric("한국 (KST)", target.astimezone(tz_k).strftime('%I:%M %p'))

        k_h = target.astimezone(tz_k).hour
        if 9 <= k_h < 18:
            st.success("✅ 업무중")
        elif 22 <= k_h or k_h < 7:
            st.error("💤 취침")
        else:
            st.warning("🌙 퇴근")

    elif "Salary" in life_menu or "연봉" in life_menu:
        st.subheader("💸 연봉 실수령액 계산")
        s = st.number_input("연봉 ($)", 80000, step=1000)
        tax = max(0, s - 14600) * (0.18 if s > 100000 else 0.12)
        fica = s * 0.0765
        net = s - tax - fica
        c1, c2 = st.columns(2)
        c1.metric("세전 (Gross)", f"${s:,.0f}")
        c2.metric("예상 세금", f"-${(tax + fica):,.0f}")
        st.success(f"💰 **월 실수령액: ${net / 12:,.0f}**")

    elif "Tip" in life_menu or "팁" in life_menu:
        st.subheader("🍽️ 팁 & 더치페이")
        c1, c2 = st.columns(2)
        b = c1.number_input("음식값 ($)", 50.0)
        t = c2.select_slider("팁 비율 (%)", [15, 18, 20, 25], value=18)
        p = st.number_input("인원 수", 1)
        st.metric("1인당 낼 돈", f"${b * (1 + t / 100) / p:.2f}")

    elif "Pizza" in life_menu or "피자" in life_menu:
        st.subheader("🍕 피자 가성비 비교")
        c1, c2 = st.columns(2)
        s1 = c1.number_input("작은거 (인치)", 12);
        s2 = c2.number_input("큰거 (인치)", 18)
        if (s2 / 2) ** 2 > 2 * (s1 / 2) ** 2:
            st.success("📢 큰 거 1판이 더 큽니다!")
        else:
            st.warning("작은 거 2판이 더 큽니다")

# =================================================
# TAB 4: 치수 변환
# =================================================
with tab_dim:
    if is_kor:
        st.markdown("#### 미터법(mm) ↔ 미국식(ft-in)")
    else:
        st.markdown("#### Metric (mm) ↔ US Customary (ft-in)")
    c1, c2 = st.columns(2)
    with c1:
        st.info("🇰🇷 mm ➡️ 🇺🇸 ft-in")
        mm = st.number_input("밀리미터 (mm)" if is_kor else "mm", value=1200.0, step=10.0)
        st.markdown(f"### **{mm_to_feet_inch_fraction(mm)}**")
        st.caption(f"Exact: {mm / 25.4 / 12:.4f} ft")
    with c2:
        st.success("🇺🇸 ft-in ➡️ 🇰🇷 mm")
        cc1, cc2 = st.columns(2)
        ft = cc1.number_input("피트 (ft)", value=5)
        inch = cc2.number_input("인치 (in)", value=3.5)
        st.markdown(f"### **{(ft * 12 + inch) * 25.4:.1f} mm**")

# =================================================
# TAB 5: 자재/배관
# =================================================
with tab_mat:
    if is_kor:
        mat_opts = ["콘크리트 (루베↔야드)", "철근 (무게 계산)", "💧 배관 (수압/무게)"]
        mat_label = "자재 종류"
    else:
        mat_opts = ["Concrete (m³↔yd³)", "Rebar (Weight)", "💧 Pipe (Hydro Test)"]
        mat_label = "Material Type"
    mat_type = st.radio(mat_label, mat_opts, horizontal=True)
    st.divider()

    if "Concrete" in mat_type or "콘크리트" in mat_type:
        st.subheader("🚛 콘크리트 물량")
        c1, c2 = st.columns(2)
        m3 = c1.number_input("루베 (m³)", 10.0)
        c2.metric("큐빅 야드 (yd³)", f"{m3 * 1.308:.2f}")

    elif "Rebar" in mat_type or "철근" in mat_type:
        st.subheader("🏗️ 철근 무게")
        rb_d = {"#3 (10mm)": 0.376, "#4 (13mm)": 0.668, "#5 (16mm)": 1.043, "#6 (19mm)": 1.502, "#8 (25mm)": 2.670}
        c1, c2 = st.columns(2)
        rb = c1.selectbox("규격", list(rb_d.keys()))
        ln = c2.number_input("총 길이 (ft)", 100.0)
        st.metric("총 무게 (lbs)", f"{ln * rb_d[rb]:.1f} lbs")

    elif "Pipe" in mat_type or "배관" in mat_type:
        st.subheader("💧 배관 용량 (Hydro Test)")
        c1, c2 = st.columns(2)
        d = c1.number_input("직경 (inch)", 4.0, step=0.5)
        l = c2.number_input("길이 (ft)", 100.0, step=10.0)
        vol = (d ** 2) * 0.0408 * l
        w = vol * 8.34
        cc1, cc2 = st.columns(2)
        cc1.metric("물 부피 (Gal)", f"{vol:.1f} gal")
        cc2.metric("물 무게 (Lbs)", f"{w:.1f} lbs")

# =================================================
# TAB 6: 호환성 판독
# =================================================
with tab_comp:
    st.subheader("🚦 호환성 판독")
    sc = st.selectbox("상황", ["🇺🇸 인치 볼트 + 🇰🇷 mm 공구", "🇰🇷 mm 볼트 + 🇺🇸 인치 공구"])
    st.divider()
    if "인치" in sc:
        db = {"5/16\" (7.9mm)": (8, "🟢 완벽 호환"), "3/8\" (9.5mm)": (10, "🔴 헐거움 (Loose)"),
              "1/2\" (12.7mm)": (13, "🔴 절대금지 (Round-off)"), "3/4\" (19.1mm)": (19, "🟢 완벽 호환")}
        s = st.selectbox("볼트 규격", list(db.keys()))
        t, status = db[s]
        c1, c2 = st.columns([1, 2])
        c1.metric("추천 공구 (mm)", f"{t} mm")
        if "🟢" in status:
            c2.success(f"### {status}")
        else:
            c2.error(f"### {status}")
    else:
        db = {"8 mm": ("5/16\"", "🟢 완벽 호환"), "10 mm": ("3/8\"", "🔴 불가"), "13 mm": ("1/2\"", "🔴 불가"),
              "19 mm": ("3/4\"", "🟢 완벽 호환")}
        s = st.selectbox("볼트 규격", list(db.keys()))
        t, status = db[s]
        c1, c2 = st.columns([1, 2])
        c1.metric("추천 공구 (Inch)", t)
        if "🟢" in status:
            c2.success(f"### {status}")
        else:
            c2.error(f"### {status}")

# =================================================
# TAB 7~9: 규격/보고서/피드백
# =================================================
with tab_chart:
    st.subheader("현장 규격표")
    t = st.radio("타입", ["철근 (Rebar)", "전선 (Wire)"], horizontal=True)
    if "철근" in t:
        st.dataframe(pd.DataFrame({"US": ["#4", "#5", "#6"], "KR": ["D13", "D16", "D19"], "mm": [12.7, 15.9, 19.1]}),
                     hide_index=True, use_container_width=True)
    else:
        st.dataframe(
            pd.DataFrame({"AWG": ["14", "12", "10"], "SQ": ["2.0", "3.5", "5.5"], "Use": ["Light", "Outlet", "Motor"]}),
            hide_index=True, use_container_width=True)

with tab_rpt:
    st.subheader("📝 일일 업무 보고")
    c1, c2 = st.columns(2)
    w = c1.selectbox("날씨", ["Sunny", "Cloudy", "Rainy", "Snowy"])
    loc = c2.text_input("위치", "Zone A")
    st.markdown("##### 1. 작업 내용")
    main = st.selectbox("공종", ["Piping", "Electrical", "Concrete"])
    det = st.text_input("상세", "메인 배관 용접")
    ppl = st.number_input("인원", 10)
    st.markdown("##### 2. 이슈 및 계획")
    iss = st.text_input("특이사항", "")
    plan = st.text_input("명일 계획", "작업 계속")

    if st.button("영어 보고서 생성"):
        rpt = f"""**[Daily Report]**\n**Date:** {datetime.now().date()} | **Weather:** {w}\n**Location:** {loc} | **Manpower:** {ppl}\n\n**1. Work Summary:**\n- {main}: {det}\n\n**2. Issues:**\n- {iss if iss else "None"}\n\n**3. Plan:**\n- {plan}"""
        st.success("✅ Created!")
        st.code(rpt)

with tab_feed:
    st.subheader("💡 기능 제안")
    with st.form("feed"):
        name = st.text_input("이름")
        msg = st.text_area("내용")
        if st.form_submit_button("전송 (이메일 앱 연동)"):
            link = f"mailto:shban127@gmail.com?subject=[Feedback] {name}&body={msg}"
            st.markdown(f"👉 [**여기(Click)를 눌러 메일 보내기**]({link})")
