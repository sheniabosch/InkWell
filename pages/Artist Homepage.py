import streamlit as st
import pandas as pd
import json
from datetime import datetime

# ≈≈≈ DRAG QUEEN UNICORN EXTRAVAGANZA THEME ≈≈≈ (pink-purple only edition)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700;800&family=Jost:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">

<style>
    .stApp {
        background: linear-gradient(135deg, #0a001f 0%, #1a0033 50%, #2d0066 100%);
        background-attachment: fixed;
        color: #f0e0ff;
        font-family: 'Figtree', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Jost', sans-serif !important;
        background: linear-gradient(90deg, #ff69f4, #ff2e9c, #b366ff, #9f7aea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 20px rgba(255, 105, 244, 0.7), 0 0 40px rgba(179, 102, 255, 0.5);
        letter-spacing: 1.8px;
        font-weight: 800;
    }

    .stMarkdown > h1 {
        font-size: 3.5rem !important;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    [data-testid="stMetricValue"] {
        font-family: 'Jost', sans-serif !important;
        font-size: 2.2rem !important;
        font-weight: 900 !important;
        background: linear-gradient(90deg, #ff69f4, #ffb3ff, #d946ef);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 25px #ff69f4, 0 0 50px #b366ff;
    }
    [data-testid="stMetricLabel"] {
        color: #e0b0ff !important;
        font-family: 'Figtree', sans-serif;
        font-weight: 600;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #1a0033, #0d001f) !important;
        border-right: 1px solid #ff69f4;
        box-shadow: 0 0 30px rgba(255, 105, 244, 0.4);
    }
    .stSidebar .stMarkdown, .stSidebar .stTextInput > label, .stSidebar .stSlider > label {
        color: #ffccff !important;
        font-family: 'Figtree', sans-serif;
    }

    .stButton > button {
        font-family: 'Jost', sans-serif !important;
        font-weight: 700 !important;
        border: 2px solid transparent;
        border-radius: 12px;
        background: linear-gradient(#1a0033, #1a0033) padding-box,
                    linear-gradient(90deg, #ff69f4, #b366ff, #ff2e9c) border-box;
        color: #ffffff !important;
        padding: 0.8rem 1.5rem !important;
        transition: all 0.4s ease;
        box-shadow: 0 0 20px rgba(255, 105, 244, 0.6);
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 0 40px #ff69f4, 0 0 60px #d946ef !important;
        background: linear-gradient(90deg, #ff2e9c, #ff69f4) !important;
        color: #000 !important;
    }

    button[kind="primary"] {
        background: linear-gradient(90deg, #ff2e9c, #ff69f4, #d946ef) !important;
        box-shadow: 0 0 30px #ff69f4 !important;
    }

    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255, 105, 244, 0.5);
        box-shadow: 0 8px 32px rgba(179, 102, 255, 0.3);
        background: rgba(20, 0, 50, 0.6);
        backdrop-filter: blur(10px);
    }

    hr, .stDivider > div {
        border-top: 1px solid #ff69f4;
        box-shadow: 0 0 15px #d946ef;
    }

    .streamlit-expanderHeader {
        font-family: 'Jost', sans-serif;
        font-weight: 700;
        background: linear-gradient(90deg, rgba(255,105,244,0.2), rgba(182,102,255,0.2));
        border: 1px solid #ff69f4;
        border-radius: 12px;
        color: #ffccff !important;
        text-shadow: 0 0 10px #ff69f4;
    }
</style>
""", unsafe_allow_html=True)

from tattoo_app.auth import require_artist
from tattoo_app.db import (
    fetch_artist_dashboard_rows,
    fetch_open_alert_counts,
    fetch_open_alerts_for_tattoo,
    ack_alert,
    resolve_alert,
    _read_sheet
)

# --- HEADER ---
st.title("✨ InkWell Artist Portal ✨")

# --- AUTH ---
if not require_artist():
    st.info("Please enter credentials in the sidebar.")
    st.stop()

# --- DATA MERGING LOGIC ---
def get_enhanced_dashboard_data():
    rows = fetch_artist_dashboard_rows()
    df_main = pd.DataFrame(rows)
    if df_main.empty: return df_main

    df_preds = _read_sheet("health_predictions")
    
    if not df_preds.empty:
        if 'health_prediction_created_at' in df_preds.columns:
            df_preds = df_preds.sort_values('health_prediction_created_at', ascending=False)
        
        df_preds = df_preds.drop_duplicates(subset=['tattoo_id'])
        
        df_main = df_main.merge(
            df_preds[['tattoo_id', 'health_prediction', 'prediction_score']], 
            on='tattoo_id', 
            how='left',
            suffixes=('', '_new')
        )
        
        if 'health_prediction_new' in df_main.columns:
            df_main['health_prediction'] = df_main['health_prediction_new'].fillna(df_main['health_prediction'])
            df_main['prediction_score'] = df_main['prediction_score_new'].fillna(df_main['prediction_score'])
            df_main.drop(columns=['health_prediction_new', 'prediction_score_new'], inplace=True)

    df_main["client"] = (df_main["first_name"].fillna("") + " " + df_main["last_name"].fillna("")).str.strip()
    df_main["risk_score"] = pd.to_numeric(df_main["risk_score"], errors='coerce').fillna(0).astype(int)
    df_main["prediction_score"] = pd.to_numeric(df_main["prediction_score"], errors='coerce').fillna(0.0)
    df_main["health_prediction"] = df_main["health_prediction"].fillna("No recent notes")
    
    return df_main

df = get_enhanced_dashboard_data()

if df.empty:
    st.warning("No client data found.")
    st.stop()

# --- TOP METRICS ---
counts = fetch_open_alert_counts()
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Critical Alerts", counts.get("Critical", 0))
with m2:
    st.metric("High Risk Clients", len(df[df["risk_tier"] == "High"]))
with m3:
    issues = df[df["health_prediction"].str.contains("Medical|Monitor|Seek|Check", na=False, case=False)]
    st.metric("Critical Predictions", len(issues))
with m4:
    st.metric("Total Inked Clients", len(df))

st.divider()

# --- CLIENTS NEEDING ATTENTION ---
st.subheader("✨ Clients Needing Your Attention ✨")

triage_cols = ["client", "placement", "risk_tier", "risk_score", "health_prediction", "prediction_score"]

def is_priority(row):
    hp = str(row["health_prediction"]).lower()
    return (
        row["risk_tier"] == "High" or
        row["risk_score"] >= 70 or
        "seek medical" in hp or
        "monitor" in hp or
        "check" in hp or
        "medical" in hp
    )

priority_df = df[df.apply(is_priority, axis=1)].copy()

if priority_df.empty:
    st.success("All clients are looking good right now — time to create some magic! 🌟")
else:
    def style_rows(row):
        styles = [''] * len(triage_cols)
        hp = str(row["health_prediction"])
        # Pink-purple only palette
        if "Seek Medical" in hp or "Critical" in str(row.get("risk_tier", "")):
            styles[triage_cols.index("health_prediction")] = 'color: #ff2e9c; font-weight: 900; text-shadow: 0 0 12px #ff2e9c;'
        elif "Monitor" in hp or "Check" in hp:
            styles[triage_cols.index("health_prediction")] = 'color: #d946ef; font-weight: 700; text-shadow: 0 0 10px #d946ef;'
        if row["risk_tier"] == "High":
            styles[triage_cols.index("risk_tier")] = 'color: #b366ff; font-weight: 900; text-shadow: 0 0 12px #b366ff;'
        return styles

    priority_display = priority_df.copy()
    priority_display["prediction_score"] = priority_display["prediction_score"].apply(lambda x: f"{x:.1%}")

    st.dataframe(
        priority_display[triage_cols].style.apply(style_rows, axis=1),
        use_container_width=True,
        hide_index=True
    )

# --- CLIENT HEALING LOG ---
st.divider()
st.subheader("✨ Client Healing Log ✨")

with st.sidebar:
    st.markdown("### Dashboard Controls")
    search_query = st.text_input("Search Client Name")
    min_score = st.slider("Filter by Attention Score", 0, 100, 0)
    
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df["client"].str.contains(search_query, case=False)]
    filtered_df = filtered_df[filtered_df["risk_score"] >= min_score]

if filtered_df.empty:
    st.info("No records matching current filters.")
else:
    selected_client_label = st.selectbox(
        "Dive Deeper: Select a Client", 
        filtered_df["client"].tolist()
    )
    
    client_row = filtered_df[filtered_df["client"] == selected_client_label].iloc[0]
    tattoo_id = client_row["tattoo_id"]

    if not tattoo_id:
        st.error("No valid Tattoo ID for this client.")
    else:
        # Client contact info
        st.markdown(f"### {client_row['client']}")
        
        email = client_row.get("email", None)
        phone = client_row.get("phone", None)
        
        contact_info = []
        if email and pd.notna(email):
            contact_info.append(f"📧 **Email:** {email}")
        if phone and pd.notna(phone):
            contact_info.append(f"📱 **Phone:** {phone}")
        
        if contact_info:
            st.markdown("\n".join(contact_info))
        else:
            st.caption("No contact info saved for this client yet.")
        
        st.divider()

        alerts = fetch_open_alerts_for_tattoo(tattoo_id)
        
        if not alerts:
            st.success(f"No open healing notes for {client_row['client']} right now. ✨")
        else:
            for alert in alerts:
                with st.expander(f"⚠️ {alert['level']} Healing Note: {client_row['client']}", expanded=True):
                    st.write(f"**Level:** {alert['level']}")
                    st.write(f"**Flagged:** {alert.get('created_at', 'N/A')}")
                    
                    reasons = alert.get("reasons_json", "[]")
                    if isinstance(reasons, str):
                        try: reasons = json.loads(reasons)
                        except: reasons = [reasons]
                    
                    st.write("**Notes:**")
                    for r in reasons:
                        st.markdown(f"- <span style='color: #ff69f4; font-weight: bold; text-shadow: 0 0 8px #ff69f4;'>{r}</span>", unsafe_allow_html=True)
                    
                    st.divider()
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("I've Seen This", key=f"ack_{alert['alert_id']}"):
                            ack_alert(alert["alert_id"])
                            st.rerun()
                    with c2:
                        if st.button("All Good Now", key=f"res_{alert['alert_id']}", type="primary"):
                            resolve_alert(alert["alert_id"])
                            st.rerun()