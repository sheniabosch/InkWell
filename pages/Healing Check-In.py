import json
import streamlit as st

from tattoo_app.ui import identity_sidebar
from tattoo_app.alerts import decide_alert_from_checkins
from tattoo_app.notify import notify_artist_for_alert
from tattoo_app.db import (
    insert_daily_checkin,
    fetch_recent_checkins,
    fetch_open_alerts_for_tattoo,
    insert_alert,
    fetch_latest_checkin,
)
from tattoo_app.ui_global import apply_global_styles

apply_global_styles()
identity_sidebar()

if not st.session_state.get("client_id"):
    st.warning("Please create profile (or load your Client ID) to begin.")
    st.stop()

# ── CLEANED UP STYLES: No glowing separators, glowing labels instead ────────
st.markdown("""
<style>
    /* Wide layout, minimal scroll */
    .stApp > div > div > div > div > div > section > div > div:nth-child(1) > div {
        max-width: 1700px !important;
        padding: 0 2.5rem !important;
    }

    .stForm {
        background: linear-gradient(135deg, rgba(18,0,35,0.9), rgba(40,0,70,0.75)) !important;
        border-radius: 22px !important;
        padding: 1.8rem 2.8rem !important;
        border: 2px solid rgba(255,120,220,0.5) !important;
        box-shadow: 0 12px 45px rgba(140,0,220,0.45) !important;
        max-width: 1600px !important;
        margin: 1rem auto !important;
    }

    /* Removed borders/separators on containers — clean & minimal */
    .checkin-item {
        background: transparent !important;
        border: none !important;
        padding: 0.8rem 0.6rem !important;
        margin: 0.4rem 0 !important;
        box-shadow: none !important;
    }

    /* GLOWING LABELS (the element names) */
    .stRadio > div > label[data-testid="stRadioLabel"],
    .stNumberInput > label,
    .stTextArea > label {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #ffccff !important;
        text-shadow: 
            0 0 8px #ff66cc,
            0 0 16px #ff33cc,
            0 0 24px #cc00aa !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 0.6rem !important;
        display: block !important;
        animation: softFlicker 6s ease-in-out infinite alternate !important;
    }

    @keyframes softFlicker {
        0%, 100% { opacity: 1; text-shadow: 0 0 8px #ff66cc, 0 0 16px #ff33cc; }
        50%      { opacity: 0.92; text-shadow: 0 0 12px #ff99ff, 0 0 22px #ff66cc, 0 0 32px #cc33aa; }
    }

    /* Compact pain/itch scales */
    .scale-radio > div {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-evenly !important;
        gap: 0.5rem !important;
        padding: 0.4rem !important;
    }

    .scale-radio > div > label {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        padding: 0.7rem 0.9rem !important;
        border-radius: 22px !important;
        border: 1.2px solid rgba(255,140,220,0.45) !important;
        min-width: 40px !important;
        text-align: center !important;
        background: rgba(60,0,100,0.3) !important;
        transition: all 0.3s ease !important;
    }

    .scale-radio > div > label[data-checked="true"] {
        background: linear-gradient(45deg, #ff66cc, #cc99ff) !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        box-shadow: 0 0 22px rgba(255,120,220,0.85) !important;
        transform: scale(1.12) !important;
    }

    /* Symptom compact pills */
    .symptom-radio > div {
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important;
        flex-wrap: wrap !important;
        gap: 0.6rem !important;
        padding: 0.4rem !important;
    }

    .symptom-radio > div > label {
        font-size: 1.05rem !important;
        padding: 0.7rem 1.1rem !important;
        border-radius: 26px !important;
        border: 1.2px solid rgba(220,120,255,0.5) !important;
        white-space: nowrap !important;
        background: rgba(60,0,100,0.3) !important;
    }

    .symptom-radio > div > label[data-checked="true"] {
        background: linear-gradient(45deg, #ff66cc, #cc88ff) !important;
        color: white !important;
        box-shadow: 0 0 18px rgba(255,120,220,0.75) !important;
        transform: scale(1.06) !important;
    }

    /* Yes/No tight */
    .yn-radio > div {
        display: flex !important;
        justify-content: center !important;
        gap: 1.5rem !important;
        flex-wrap: wrap !important;
    }

    .yn-radio > div > label {
        font-size: 1.12rem !important;
        padding: 0.8rem 1.6rem !important;
        border-radius: 28px !important;
        border: 1.5px solid rgba(220,120,255,0.6) !important;
        background: rgba(60,0,100,0.3) !important;
    }

    .yn-radio > div > label[data-checked="true"] {
        background: linear-gradient(45deg, #ff66cc, #cc88ff) !important;
        box-shadow: 0 0 24px rgba(255,120,220,0.85) !important;
    }

    /* Day compact */
    .day-input input {
        background: linear-gradient(90deg, #330066, #550088) !important;
        border: 2px solid #cc88ff !important;
        border-radius: 12px !important;
        font-size: 1.45rem !important;
        height: 2.9rem !important;
        width: 150px !important;
        text-align: center !important;
        color: #ffddff !important;
        box-shadow: inset 0 0 10px rgba(200,100,255,0.4) !important;
    }

    /* Notes at bottom */
    .stTextArea textarea {
        height: 100px !important;
        border: 1.8px solid rgba(220,120,255,0.65) !important;
        border-radius: 14px !important;
        background: rgba(30,0,55,0.8) !important;
        font-size: 1.15rem !important;
        padding: 0.9rem !important;
        box-shadow: inset 0 0 14px rgba(180,80,255,0.4) !important;
    }

    /* Epic save button */
    .stFormSubmitButton > button {
        background: linear-gradient(45deg, #ff33cc, #cc44ff, #ff66cc, #aa33ff) !important;
        background-size: 400% 400% !important;
        animation: epicShine 4s ease infinite !important;
        font-size: 1.55rem !important;
        font-weight: 800 !important;
        padding: 1.1rem 3.5rem !important;
        border-radius: 50px !important;
        border: 3px solid #ffffff55 !important;
        box-shadow: 0 14px 45px rgba(255,80,220,0.65) !important;
        width: 100% !important;
        max-width: 380px !important;
        margin: 1.8rem auto 0.5rem !important;
    }

    @keyframes epicShine {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    .stFormSubmitButton > button:hover {
        transform: scale(1.09) translateY(-6px) !important;
        box-shadow: 0 28px 70px rgba(255,80,220,0.95) !important;
    }

    /* God-tier success */
    .god-success {
        background: linear-gradient(135deg, #6600aa, #9900cc, #cc33ff, #ff66cc) !important;
        color: white !important;
        padding: 1.8rem !important;
        border-radius: 20px !important;
        text-align: center !important;
        font-size: 2.1rem !important;
        font-weight: 900 !important;
        margin: 1.5rem auto !important;
        max-width: 1600px !important;
        box-shadow: 0 22px 85px rgba(255,120,220,0.95) !important;
        animation: godPulse 2.8s ease-in-out infinite !important;
    }

    .god-success::before {
        content: "✨ CHECK-IN SAVED ✨" !important;
        display: block !important;
        font-size: 2.3rem !important;
        margin-bottom: 0.6rem !important;
    }

    @keyframes godPulse {
        0%, 100% { box-shadow: 0 22px 85px rgba(255,120,220,0.95); }
        50% { box-shadow: 0 32px 110px rgba(255,160,255,1); }
    }

    .alert-god {
        background: linear-gradient(135deg, #550066, #880099, #aa33cc) !important;
        border: 2.5px solid #ff88dd !important;
        box-shadow: 0 0 55px rgba(255,120,220,0.8) !important;
    }

    /* 2-col grid */
    .checkin-row {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)) !important;
        gap: 0.9rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("### 🖤 Daily Healing Check-in 🖤")

tattoo_id = st.session_state.tattoo_id
latest = fetch_latest_checkin(tattoo_id)
if latest:
    st.info(f"**Last check-in:** {latest['created_at']} (Day {latest['day_index']})")

with st.form("checkin_form", clear_on_submit=True):
    st.markdown('<div class="checkin-row">', unsafe_allow_html=True)

    # Day
    st.markdown('<div class="checkin-item day-input">', unsafe_allow_html=True)
    day_index = st.number_input("Day since tattoo (0 = today)", 0, 60, 0, key="day_index")
    st.markdown('</div>', unsafe_allow_html=True)

    # Pain
    st.markdown('<div class="checkin-item scale-radio">', unsafe_allow_html=True)
    pain = st.radio("💥 Pain (0–10)", [0,2,4,6,8,10], horizontal=True, index=1, key="pain")
    st.markdown('</div>', unsafe_allow_html=True)

    # Itch
    st.markdown('<div class="checkin-item scale-radio">', unsafe_allow_html=True)
    itch = st.radio("🧠 Itch (0–10)", [0,2,4,6,8,10], horizontal=True, index=1, key="itch")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="checkin-row">', unsafe_allow_html=True)

    st.markdown('<div class="checkin-item symptom-radio">', unsafe_allow_html=True)
    redness_level = st.radio("🔴 Redness", ["None","Mild","Mod","Spread"], horizontal=True, index=1, key="red")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="checkin-item symptom-radio">', unsafe_allow_html=True)
    swelling_level = st.radio("💧 Swelling", ["None","Mild","Mod","Severe"], horizontal=True, index=0, key="swell")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="checkin-item symptom-radio">', unsafe_allow_html=True)
    discharge_level = st.radio("💉 Discharge", ["None","Clear","Cloudy","Yellow"], horizontal=True, index=0, key="disch")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Binary cluster
    st.markdown('<div class="checkin-item">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        warmth = st.radio("🔥 Warmth to touch?", ["No","Yes"], horizontal=True, index=0, key="warm")
    with col2:
        odor = st.radio("👃 Odor?", ["No","Yes"], horizontal=True, index=0, key="odor")
    with col3:
        fever = st.radio("🌡️ Fever/chills?", ["No","Yes"], horizontal=True, index=0, key="fever")
    st.markdown('</div>', unsafe_allow_html=True)

    # Notes last
    st.markdown('<div class="checkin-item">', unsafe_allow_html=True)
    notes = st.text_area("📝 Notes (optional)", height=100)
    st.markdown('</div>', unsafe_allow_html=True)

    submitted = st.form_submit_button("💜 SAVE CHECK-IN 💜", type="primary")

# ── Save logic unchanged ─────────────────────────────────────────────────────
if submitted:
    insert_daily_checkin(
        tattoo_id=tattoo_id,
        day_index=int(day_index),
        pain=int(pain),
        redness_level=["None","Mild","Mod","Spread"].index(redness_level),
        swelling_level=["None","Mild","Mod","Severe"].index(swelling_level),
        warmth=1 if warmth == "Yes" else 0,
        itch=int(itch),
        discharge_level=["None","Clear","Cloudy","Yellow"].index(discharge_level),
        odor=1 if odor == "Yes" else 0,
        fever=1 if fever == "Yes" else 0,
        notes=notes or None,
    )

    recent = fetch_recent_checkins(tattoo_id, limit=3)
    decision = decide_alert_from_checkins(recent)

    if decision.level:
        open_alerts = fetch_open_alerts_for_tattoo(tattoo_id)
        if decision.level not in {a["level"] for a in open_alerts}:
            alert_id = insert_alert(tattoo_id, decision.level, decision.reasons)
            client_name = f"{st.session_state.get('first_name','')} {st.session_state.get('last_name','')}".strip()
            placement = st.session_state.get("placement")

            st.markdown(f'<div class="god-success alert-god">'
                        f'<h2>⚡ ALERT LEVEL {decision.level} ⚡</h2>'
                        f'<p>{" • ".join(decision.reasons)}</p>'
                        f'</div>', unsafe_allow_html=True)

            try:
                notify_artist_for_alert(
                    alert_id=alert_id,
                    level=decision.level,
                    reasons_json=json.dumps(decision.reasons, ensure_ascii=False),
                    client_name=client_name,
                    placement=placement,
                )
                st.warning("Artist has been notified.")
            except Exception as e:
                st.error(f"Notification failed: {e}")
    else:
        st.markdown('<div class="god-success">Healing looks good! ✨ </div>', unsafe_allow_html=True)
