import streamlit as st

from tattoo_app.ui import identity_sidebar
from tattoo_app.risk_engine import score_risk, dumps_answers, dumps_drivers
from tattoo_app.db import insert_risk_assessment
from tattoo_app.ui_global import apply_global_styles

apply_global_styles()
identity_sidebar()

if not st.session_state.get("client_id"):
    st.warning("Please create profile (or load your Client ID) to begin.")
    st.stop()

# ── ULTRA-COMPACT + HOT PINK VERSION ─────────────────────────────────────────
st.markdown("""
<style>
    /* Very wide + very tight spacing */
    .stApp > div > div > div > div > div > section > div > div:nth-child(1) > div {
        max-width: 1900px !important;
        padding: 0 1.5rem !important;
    }

    .stForm {
        background: linear-gradient(135deg, rgba(18,0,35,0.94), rgba(40,0,70,0.82)) !important;
        border-radius: 18px !important;
        padding: 1rem 2.2rem 1.2rem 2.2rem !important;
        margin: 0.5rem auto !important;
        max-width: 1800px !important;
        border: 1.5px solid #ff66cc !important;
        box-shadow: 0 8px 35px rgba(255,102,204,0.35) !important;
    }

    .checkin-item {
        background: transparent !important;
        border: none !important;
        padding: 0.35rem 0.4rem !important;
        margin: 0.15rem 0 !important;
    }

    /* Glowing labels - hot pink */
    .stRadio > div > label[data-testid="stRadioLabel"] {
        font-size: 1.18rem !important;
        font-weight: 700 !important;
        color: #ffccff !important;
        text-shadow: 
            0 0 8px #ff66cc,
            0 0 16px #ff3399,
            0 0 26px #ff0066 !important;
        margin-bottom: 0.35rem !important;
        animation: softFlicker 6s infinite alternate !important;
    }

    @keyframes softFlicker {
        0%, 100% { text-shadow: 0 0 8px #ff66cc, 0 0 16px #ff3399; }
        50%      { text-shadow: 0 0 13px #ff99ff, 0 0 24px #ff66cc, 0 0 35px #ff3399; }
    }

    /* Very compact bubble pills - hot pink selected */
    .bubble-radio > div {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        justify-content: flex-start !important;
        gap: 0.4rem !important;
        padding: 0.2rem 0 !important;
    }

    .bubble-radio > div > label {
        font-size: 0.94rem !important;
        padding: 0.5rem 0.95rem !important;
        border-radius: 24px !important;
        border: 1px solid #ff99ff55 !important;
        background: rgba(60,0,100,0.38) !important;
        white-space: nowrap !important;
        min-width: 70px !important;
        line-height: 1.15 !important;
    }

    .bubble-radio > div > label[data-checked="true"] {
        background: linear-gradient(45deg, #ff66cc, #ff99ff, #ff3399) !important;
        color: white !important;
        box-shadow: 0 0 16px #ff66cc !important;
        border-color: #ffffff77 !important;
        transform: scale(1.07) !important;
    }

    /* Button - hot pink gradient */
    .stFormSubmitButton > button {
        background: linear-gradient(45deg, #ff3399, #ff66cc, #ff99ff, #ff3399) !important;
        background-size: 400% !important;
        animation: epicShine 4s ease infinite !important;
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        padding: 0.85rem 2.6rem !important;
        border-radius: 50px !important;
        border: 2.5px solid #ffffff44 !important;
        box-shadow: 0 10px 35px rgba(255,102,204,0.6) !important;
        width: 100% !important;
        max-width: 320px !important;
        margin: 1rem auto 0.4rem !important;
    }

    @keyframes epicShine {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    .stFormSubmitButton > button:hover {
        transform: scale(1.08) translateY(-5px) !important;
        box-shadow: 0 22px 60px rgba(255,102,204,0.9) !important;
    }

    /* Result - hot pink score */
    .risk-result {
        padding: 0.9rem !important;
        margin: 0.7rem 0 !important;
        background: rgba(45,0,80,0.45) !important;
        border-radius: 14px !important;
        border: 1.5px solid #ff66cc !important;
    }

    .risk-score {
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        color: #ff66cc !important;
        text-shadow: 0 0 18px #ff3399, 0 0 35px #ff0066 !important;
    }

    .risk-tier {
        font-size: 1.45rem !important;
        color: #ff99ff !important;
        text-shadow: 0 0 12px #ff66cc !important;
    }

    .drivers-list {
        font-size: 1.05rem !important;
        color: #eeddff !important;
        margin-top: 0.6rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("### 🖤 Risk Assessment 🖤")
st.markdown("Very quick → your personal risk score")

with st.form("risk_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="checkin-item bubble-radio">', unsafe_allow_html=True)
        smoking = st.radio("🚬 Smoking", ["None", "Occasional", "Daily"], horizontal=True, key="smoking")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="checkin-item bubble-radio">', unsafe_allow_html=True)
        diabetes = st.radio("🩸 Diabetes?", ["No", "Yes"], horizontal=True, key="diabetes")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="checkin-item bubble-radio">', unsafe_allow_html=True)
        immune_issue = st.radio("🛡️ Immune / serious condition?", ["No", "Yes"], horizontal=True, key="immune")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="checkin-item bubble-radio">', unsafe_allow_html=True)
        work_env = st.radio("🏭 Work env", 
                            ["Office", "Outdoors", "Dust/Chemicals", "Healthcare"], 
                            horizontal=True, key="work")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="checkin-item bubble-radio">', unsafe_allow_html=True)
        pets = st.radio("🐶 Pets risk?", ["No", "Yes"], horizontal=True, key="pets")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="checkin-item bubble-radio">', unsafe_allow_html=True)
        handwashing = st.radio("🧼 Handwashing?", ["Easy", "Limited"], horizontal=True, key="hand")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="checkin-item bubble-radio">', unsafe_allow_html=True)
        exercise = st.radio("🏃 Exercise 7–10d?", ["No", "Light", "Intense"], horizontal=True, key="exercise")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="checkin-item bubble-radio">', unsafe_allow_html=True)
        water_exposure = st.radio("🏊 Swimming / sauna?", ["No", "Yes"], horizontal=True, key="water")
        st.markdown('</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="checkin-item bubble-radio">', unsafe_allow_html=True)
        friction_area = st.radio("👕 Friction?", ["Low", "Medium", "High"], horizontal=True, key="friction")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="checkin-item bubble-radio">', unsafe_allow_html=True)
        eczema = st.radio("🌿 Eczema?", ["None", "Mild/History", "Active"], horizontal=True, key="eczema")
        st.markdown('</div>', unsafe_allow_html=True)

    # Last question - full width
    st.markdown('<div class="checkin-item bubble-radio">', unsafe_allow_html=True)
    product_reaction = st.radio("🧴 Past product reaction?", ["No", "Yes"], horizontal=True, key="reaction")
    st.markdown('</div>', unsafe_allow_html=True)

    submitted = st.form_submit_button("💜 CALCULATE RISK 💜", type="primary")

# ── Result & save ─────────────────────────────────────────────────────────────
if submitted:
    answers = {
        "smoking": smoking,
        "diabetes": diabetes,
        "immune_issue": immune_issue,
        "work_env": work_env,
        "pets": pets,
        "handwashing": handwashing,
        "exercise": exercise,
        "water_exposure": water_exposure,
        "friction_area": friction_area,
        "eczema": eczema,
        "product_reaction": product_reaction
    }

    result = score_risk(answers)

    st.markdown(f"""
    <div class="risk-result">
        <div class="risk-score">{result.score}/100</div>
        <div class="risk-tier">{result.tier}</div>
        <div class="drivers-list">
            <strong>Top drivers:</strong><br>
            {"<br>".join(f"• {d}" for d in result.drivers)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    insert_risk_assessment(
        client_id=st.session_state.client_id,
        answers_json=dumps_answers(answers),
        risk_score=result.score,
        risk_tier=result.tier,
        drivers_json=dumps_drivers(result.drivers),
    )

    st.markdown('<div class="god-success">Risk profile saved! ✨</div>', unsafe_allow_html=True)