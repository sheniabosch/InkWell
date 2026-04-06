import os
import re
import requests
import json
import base64
import numpy as np
import tensorflow as tf
import keras
import streamlit as st
from pathlib import Path

# Project specific imports
from src.model_loader import initialise_llm, get_embedding_model
from src.engine import get_chat_engine
from tattoo_app.db import fetch_latest_risk, fetch_latest_checkin, fetch_latest_prediction
from tattoo_app.ui import identity_sidebar
from tattoo_app.ui_global import apply_global_styles

# --- CONFIG & ASSETS ---
ROXY_IMAGE_DRIVE_ID = "1H_VVCmn22610YyJ9eALBvt_VbKDCDiBw"

@st.cache_data
def get_image_base64_from_drive(file_id):
    try:
        url = f"https://docs.google.com/uc?export=download&id={file_id}"
        session = requests.Session()
        response = session.get(url, stream=True)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode("utf-8")
        return None
    except: return None

roxy_img_b64 = get_image_base64_from_drive(ROXY_IMAGE_DRIVE_ID)
apply_global_styles()

# --- STYLING UPDATES: Tightened message spacing & fixed overlap ---
st.markdown("""
<style>
    /* Hide top bar/header */
    header, div[data-testid="stHeader"], .stApp header {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    .stApp {
        background-color: #0e0e1e !important;
    }

    /* Roxy fixed very top-right */
    .fixed-roxy {
        position: fixed !important;
        top: 20px !important;
        right: 30px !important;
        z-index: 9999 !important;
        text-align: center !important;
        padding: 20px 15px !important;
    }

    .roxy-avatar {
        width: 260px !important;
        height: 260px !important;
        border-radius: 50% !important;
        border: 4px solid #ff66cc !important;
        box-shadow: 0 0 40px rgba(255,102,204,0.7) !important;
        object-fit: cover !important;
        margin-bottom: 12px !important;
    }

    .roxy-name {
        font-family: 'Figtree', sans-serif !important;
        font-weight: 900 !important;
        font-size: 2.3rem !important;
        background: linear-gradient(90deg, #ff66cc, #ff99ff, #cc99ff) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-shadow: 0 0 16px rgba(255,102,204,0.8) !important;
    }

    /* Sticky status banners */
    .status-container {
        position: sticky !important;
        top: 0 !important;
        z-index: 999 !important;
        background: rgba(14,14,30,0.95) !important;
        padding: 1rem 2rem !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.6) !important;
        border-bottom: 1px solid #ff66cc44 !important;
    }

    .status-card {
        background: rgba(255,102,204,0.1) !important;
        border: 1.5px solid #ff66cc88 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        text-align: center !important;
    }

    /* TIGHTEN MESSAGE SPACING */
    /* Target the vertical block that holds chat messages to reduce the gap between elements */
    div[data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }

    section[data-testid="stChatMessage"] {
        max-width: 65% !important;
        margin-right: 360px !important;
        margin-bottom: -10px !important; /* Pull messages closer together */
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }

    /* Add space only at the very bottom of the scrolling area */
    div[data-testid="stVerticalBlock"] > div:last-child {
        margin-bottom: 150px !important;
    }

    /* Chat input - sticky bottom, centered */
    div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 0 !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 65% !important;
        max-width: 850px !important;
        z-index: 1000 !important;
        background: #0e0e1e !important;
        padding: 1.5rem 1.2rem !important;
        box-shadow: 0 -15px 30px rgba(0,0,0,0.9) !important;
        border-top: 1.5px solid #ff66cc66 !important;
        border-radius: 20px 20px 0 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Fixed top-right Roxy
st.markdown(f"""
<div class="fixed-roxy">
    <img src="data:image/png;base64,{roxy_img_b64}" class="roxy-avatar" alt="Roxy">
    <div class="roxy-name">Roxy</div>
</div>
""", unsafe_allow_html=True)

# Data fetching
def get_clean_status():
    risk = fetch_latest_risk(st.session_state.client_id)
    checkin = fetch_latest_checkin(st.session_state.tattoo_id)
    pred = fetch_latest_prediction(st.session_state.tattoo_id)
    
    return {
        "risk": {
            "val": risk.get('risk_tier', 'N/A') if risk else "No Profile",
            "sub": f"Score: {risk.get('risk_score', 0)}" if risk else "Run Assessment",
        },
        "healing": {
            "val": f"Day {checkin.get('day_index', 0)}" if checkin else "No Check-in",
            "sub": f"Pain: {checkin.get('pain', 0)}/10" if checkin else "Start Today",
        },
        "ai": {
            "val": pred.get('health_prediction', 'Pending') if pred else "No Scan",
            "sub": f"Conf: {pred.get('prediction_score', 0):.0%}" if pred else "Scan Tattoo",
        }
    }

identity_sidebar()
if not st.session_state.get("client_id"):
    st.warning("Please identify yourself to enable Roxy's brain.")
    st.stop()

status = get_clean_status()

# Sticky status banners
st.markdown('<div class="status-container">', unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center; color:#ffccff; margin-bottom:15px;'>🖤 Roxy's Quick Status Check 🖤</h3>", unsafe_allow_html=True)

cols = st.columns(3)
with cols[0]:
    st.markdown(f"""<div class="status-card"><div class="status-label" style="color:#cc99ff; font-size:0.8rem;">RISK TIER</div><div class="status-value">{status['risk']['val']}</div><div class="status-label" style="color:#cc99ff; font-size:0.7rem;">{status['risk']['sub']}</div></div>""", unsafe_allow_html=True)
with cols[1]:
    st.markdown(f"""<div class="status-card"><div class="status-label" style="color:#cc99ff; font-size:0.8rem;">HEALING DAY</div><div class="status-value">{status['healing']['val']}</div><div class="status-label" style="color:#cc99ff; font-size:0.7rem;">{status['healing']['sub']}</div></div>""", unsafe_allow_html=True)
with cols[2]:
    st.markdown(f"""<div class="status-card"><div class="status-label" style="color:#cc99ff; font-size:0.8rem;">AI SCAN</div><div class="status-value">{status['ai']['val']}</div><div class="status-label" style="color:#cc99ff; font-size:0.7rem;">{status['ai']['sub']}</div></div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Chat engine
@st.cache_resource
def load_chat_engine():
    return get_chat_engine(llm=initialise_llm(), embed_model=get_embedding_model())

chat_engine = load_chat_engine()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hey sugar! I've checked your latest stats. How are we feeling today? 💉✨"}]

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask Roxy anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    context_str = f"Risk: {status['risk']['val']}, Healing: {status['healing']['val']}, AI Scan: {status['ai']['val']}"
    SYSTEM_INSTRUCTIONS = f"You are Roxy, a sassy pin-up nurse. Context: {context_str}. Short, snappy, safe answers."
    full_query = f"{SYSTEM_INSTRUCTIONS}\n\nUser Question: {prompt}"

    with st.chat_message("assistant"):
        with st.spinner("Roxy is thinking... ✨"):
            response = chat_engine.chat(full_query)
            st.markdown(str(response))
        st.session_state.messages.append({"role": "assistant", "content": str(response)})

# Final bottom spacer
st.markdown("<div style='height: 140px;'></div>", unsafe_allow_html=True)