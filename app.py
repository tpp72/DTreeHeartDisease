# ============================================================
# 🫀 Heart Disease Predictor — Streamlit Web App
# ใช้โมเดล Decision Tree จากไฟล์ heart_disease_model.pkl
# รองรับการสลับธีม Dark / Light
#
# วิธีรัน:  streamlit run app.py
# (วางไฟล์ heart_disease_model.pkl ไว้โฟลเดอร์เดียวกับ app.py)
# ============================================================

import pickle
import pandas as pd
import streamlit as st

# ------------------------------------------------------------
# ตั้งค่าหน้าเว็บ
# ------------------------------------------------------------
st.set_page_config(
    page_title="Heart Disease Predictor",
    page_icon="🫀",
    layout="wide",
)

# ------------------------------------------------------------
# โหลดโมเดล (cache ไว้เพื่อไม่ต้องโหลดซ้ำทุกครั้ง)
# ------------------------------------------------------------
@st.cache_resource
def load_model():
    with open("heart_disease_model.pkl", "rb") as f:
        return pickle.load(f)

try:
    model = load_model()
    model_ok = True
except FileNotFoundError:
    model_ok = False

# ------------------------------------------------------------
# สถานะธีม (Dark / Light)
# ------------------------------------------------------------
if "dark" not in st.session_state:
    st.session_state.dark = False

with st.sidebar:
    st.markdown("### ⚙️ การตั้งค่า")
    st.session_state.dark = st.toggle(
        "🌙 โหมดกลางคืน (Dark theme)",
        value=st.session_state.dark,
    )
    st.divider()
    st.markdown("### 🌳 เกี่ยวกับโมเดล")
    st.markdown(
        "- อัลกอริทึม: **Decision Tree**\n"
        "- ข้อมูลฝึก: Heart4.csv (918 ราย)\n"
        "- ความแม่นยำ (Test): **~78.8%**"
    )
    st.caption("ผลการทำนายเป็นเพียงเครื่องมือช่วยเบื้องต้น ไม่ใช่การวินิจฉัยทางการแพทย์")

dark = st.session_state.dark

# ------------------------------------------------------------
# ชุดสีของแต่ละธีม
# ------------------------------------------------------------
if dark:
    C = dict(bg="#0E1621", surface="#17222E", surface2="#1E2C3A",
             ink="#E9F0F5", muted="#93A5B3", accent="#FF5C77",
             teal="#2BC5C4", border="#26384A", shadow="rgba(0,0,0,.45)")
else:
    C = dict(bg="#F6F8FA", surface="#FFFFFF", surface2="#EEF3F6",
             ink="#1B2A38", muted="#5F7183", accent="#E23E57",
             teal="#12888A", border="#DFE7EC", shadow="rgba(27,42,56,.08)")

# ------------------------------------------------------------
# CSS ปรับแต่งหน้าตา + ฟอนต์ไทย (Prompt / Sarabun)
# ------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@500;600;700&family=Sarabun:wght@400;500;600&display=swap');

html, body, .stApp {{
    background-color: {C['bg']} !important;
    color: {C['ink']};
    font-family: 'Sarabun', sans-serif;
}}
h1, h2, h3, h4 {{ font-family: 'Prompt', sans-serif !important; color: {C['ink']} !important; }}
p, label, span, div {{ color: {C['ink']}; }}
[data-testid="stSidebar"] {{
    background-color: {C['surface']} !important;
    border-right: 1px solid {C['border']};
}}
[data-testid="stSidebar"] * {{ color: {C['ink']} !important; font-family:'Sarabun',sans-serif; }}

/* ส่วนหัวแบบการ์ด + เส้นชีพจร */
.hero {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 18px;
    padding: 28px 32px 10px 32px;
    box-shadow: 0 8px 24px {C['shadow']};
    margin-bottom: 8px;
}}
.hero h1 {{ margin: 0; font-size: 2rem; letter-spacing: .3px; }}
.hero p  {{ color: {C['muted']}; margin: 6px 0 0 0; }}

/* เส้น ECG เคลื่อนไหว (ลายเซ็นของหน้านี้) */
.ecg {{ width:100%; height:56px; margin-top:6px; }}
.ecg path {{
    fill:none; stroke:{C['accent']}; stroke-width:2.5;
    stroke-dasharray: 640; stroke-dashoffset: 640;
    animation: beat 3.2s linear infinite;
}}
@keyframes beat {{ to {{ stroke-dashoffset: 0; }} }}
@media (prefers-reduced-motion: reduce) {{ .ecg path {{ animation: none; stroke-dashoffset: 0; }} }}

/* การ์ดกลุ่มข้อมูล */
.card-label {{
    font-family:'Prompt',sans-serif; font-weight:600; font-size:.95rem;
    color:{C['teal']}; text-transform:uppercase; letter-spacing:.12em;
    border-bottom: 2px solid {C['teal']}; display:inline-block;
    padding-bottom:4px; margin: 10px 0 4px 0;
}}

/* ช่องกรอกข้อมูล */
[data-testid="stNumberInput"] input, [data-baseweb="select"] > div {{
    background-color: {C['surface']} !important;
    color: {C['ink']} !important;
    border-color: {C['border']} !important;
}}
[data-baseweb="popover"] li {{ background-color:{C['surface']} !important; color:{C['ink']} !important; }}

/* ปุ่มทำนาย */
.stButton > button {{
    background: {C['accent']}; color: #fff !important;
    font-family:'Prompt',sans-serif; font-weight:600; font-size:1.05rem;
    border: none; border-radius: 12px; padding: .7rem 2.4rem;
    box-shadow: 0 6px 18px {C['shadow']};
    transition: transform .12s ease, filter .12s ease;
}}
.stButton > button:hover {{ transform: translateY(-2px); filter: brightness(1.06); }}

/* การ์ดผลลัพธ์ */
.result {{
    border-radius: 18px; padding: 26px 30px; margin-top: 10px;
    border: 1px solid {C['border']};
    background: {C['surface']};
    box-shadow: 0 10px 28px {C['shadow']};
}}
.result .big {{ font-family:'Prompt',sans-serif; font-size:1.6rem; font-weight:700; }}
.risk-high .big  {{ color: {C['accent']}; }}
.risk-low  .big  {{ color: {C['teal']}; }}

/* แถบความน่าจะเป็น */
.bar-wrap {{ background:{C['surface2']}; border-radius:99px; height:16px; margin-top:14px; overflow:hidden; }}
.bar-fill {{ height:100%; border-radius:99px;
    background: linear-gradient(90deg, {C['teal']}, {C['accent']});
    transition: width .6s ease; }}
.bar-num {{ font-family:'Prompt',sans-serif; font-weight:600; color:{C['muted']}; font-size:.9rem; margin-top:6px; }}

footer, #MainMenu {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# ส่วนหัว (Hero) พร้อมเส้น ECG เคลื่อนไหว
# ------------------------------------------------------------
st.markdown("""
<div class="hero">
  <h1>🫀 ระบบทำนายความเสี่ยงโรคหัวใจ</h1>
  <p>กรอกข้อมูลผู้ป่วย แล้วให้โมเดล Decision Tree ประเมินความเสี่ยงการเป็นโรคหัวใจ</p>
  <svg class="ecg" viewBox="0 0 600 60" preserveAspectRatio="none">
    <path d="M0,30 L80,30 L95,30 L103,12 L112,48 L120,30 L200,30 L215,30 L223,8 L232,52 L240,30
             L320,30 L335,30 L343,14 L352,46 L360,30 L440,30 L455,30 L463,10 L472,50 L480,30 L600,30"/>
  </svg>
</div>
""", unsafe_allow_html=True)

if not model_ok:
    st.error("ไม่พบไฟล์ **heart_disease_model.pkl** — กรุณาวางไฟล์โมเดลไว้ในโฟลเดอร์เดียวกับ app.py แล้วรีเฟรชหน้า")
    st.stop()

# ------------------------------------------------------------
# แบบฟอร์มกรอกข้อมูลผู้ป่วย (3 กลุ่ม)
# ------------------------------------------------------------
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown('<div class="card-label">ข้อมูลทั่วไป</div>', unsafe_allow_html=True)
    age = st.number_input("อายุ (ปี)", 20, 100, 50)
    sex = st.selectbox("เพศ", options=[1, 0],
                       format_func=lambda v: "ชาย" if v == 1 else "หญิง")
    chest = st.selectbox("อาการเจ็บหน้าอก (ChestPainType)",
                         options=[1, 2, 3, 4],
                         format_func=lambda v: {
                             1: "แบบที่ 1 — Typical Angina",
                             2: "แบบที่ 2 — Atypical Angina",
                             3: "แบบที่ 3 — Non-Anginal Pain",
                             4: "แบบที่ 4 — Asymptomatic"}[v])

with col2:
    st.markdown('<div class="card-label">ผลตรวจร่างกาย</div>', unsafe_allow_html=True)
    bp   = st.number_input("ความดันโลหิตขณะพัก (RestingBP, mmHg)", 0, 250, 130)
    chol = st.number_input("คอเลสเตอรอล (Cholesterol, mg/dl)", 0, 700, 220)
    fbs  = st.selectbox("น้ำตาลในเลือดหลังอดอาหาร > 120 mg/dl (FastingBS)",
                        options=[0, 1],
                        format_func=lambda v: "ไม่ใช่ (0)" if v == 0 else "ใช่ (1)")
    ecg  = st.selectbox("ผลคลื่นไฟฟ้าหัวใจขณะพัก (RestingECG)",
                        options=[1, 2, 3],
                        format_func=lambda v: {
                            1: "แบบที่ 1 — Normal",
                            2: "แบบที่ 2 — ST-T Abnormality",
                            3: "แบบที่ 3 — LVH"}[v])

with col3:
    st.markdown('<div class="card-label">ผลทดสอบสมรรถภาพหัวใจ</div>', unsafe_allow_html=True)
    maxhr   = st.number_input("อัตราการเต้นหัวใจสูงสุด (MaxHR)", 50, 220, 140)
    angina  = st.selectbox("เจ็บหน้าอกขณะออกกำลังกาย (ExerciseAngina)",
                           options=[0, 1],
                           format_func=lambda v: "ไม่มี (0)" if v == 0 else "มี (1)")
    oldpeak = st.number_input("ค่า ST Depression (Oldpeak)", -3.0, 7.0, 1.0, step=0.1)
    slope   = st.selectbox("ความชันของ ST Segment (ST_Slope)",
                           options=[1, 2, 3],
                           format_func=lambda v: {
                               1: "แบบที่ 1 — Down",
                               2: "แบบที่ 2 — Flat",
                               3: "แบบที่ 3 — Up"}[v])

st.write("")
center = st.columns([1, 1, 1])[1]
with center:
    predict_clicked = st.button("🔍 ทำนายความเสี่ยง", use_container_width=True)

# ------------------------------------------------------------
# ทำนายผลและแสดงการ์ดผลลัพธ์
# ------------------------------------------------------------
if predict_clicked:
    X_new = pd.DataFrame([{
        "Age": age, "Sex": sex, "ChestPainType": chest,
        "RestingBP": bp, "Cholesterol": chol, "FastingBS": fbs,
        "RestingECG": ecg, "MaxHR": maxhr, "ExerciseAngina": angina,
        "Oldpeak": oldpeak, "ST_Slope": slope,
    }])

    pred = int(model.predict(X_new)[0])
    prob_disease = float(model.predict_proba(X_new)[0][1]) * 100

    if pred == 1:
        css, icon, title = "risk-high", "⚠️", "มีความเสี่ยงเป็นโรคหัวใจ"
        desc = "โมเดลประเมินว่าผู้ป่วยรายนี้มีแนวโน้มเป็นโรคหัวใจ ควรพบแพทย์เพื่อตรวจวินิจฉัยเพิ่มเติม"
    else:
        css, icon, title = "risk-low", "✅", "ความเสี่ยงต่ำ ไม่พบแนวโน้มโรคหัวใจ"
        desc = "โมเดลประเมินว่าผู้ป่วยรายนี้มีแนวโน้มไม่เป็นโรคหัวใจ อย่างไรก็ตามควรดูแลสุขภาพอย่างสม่ำเสมอ"

    st.markdown(f"""
    <div class="result {css}">
        <div class="big">{icon} {title}</div>
        <p style="margin:8px 0 0 0;">{desc}</p>
        <div class="bar-wrap"><div class="bar-fill" style="width:{prob_disease:.1f}%"></div></div>
        <div class="bar-num">ความน่าจะเป็นของการเป็นโรคหัวใจ: {prob_disease:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)