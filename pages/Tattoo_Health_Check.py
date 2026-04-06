import os
import re
import requests
import numpy as np
import tensorflow as tf
import streamlit as st
from PIL import Image
from tattoo_app.ui_global import apply_global_styles
from tattoo_app.db import insert_health_prediction

# --- CONFIG & MODEL LOADER (unchanged) ---
MODEL_FILE_ID = "1d82aVCYL7s09mq3qhgl3i-eZw0oH6xyp"
LOCAL_MODEL_NAME = "inkwell_model (1).keras"

@st.cache_resource
def download_and_load_model():
    if os.path.exists(LOCAL_MODEL_NAME) and os.path.getsize(LOCAL_MODEL_NAME) < 1000000:
        os.remove(LOCAL_MODEL_NAME)
    
    if not os.path.exists(LOCAL_MODEL_NAME):
        try:
            with st.spinner("Connecting to InkWell AI Engine..."):
                session = requests.Session()
                base_url = "https://docs.google.com/uc?export=download"
                response = session.get(base_url, params={'id': MODEL_FILE_ID}, stream=True)
                confirm_token = re.search(r'confirm=([0-9A-Za-z_]+)', response.text).group(1) if "confirm=" in response.text else None
                
                params = {'id': MODEL_FILE_ID}
                if confirm_token: params['confirm'] = confirm_token
                
                response = session.get(base_url, params=params, stream=True)
                with open(LOCAL_MODEL_NAME, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024*1024):
                        if chunk: f.write(chunk)
        except Exception as e:
            st.error(f"Download failed: {e}")
            return None
    
    try:
        return tf.keras.models.load_model(LOCAL_MODEL_NAME, compile=False)
    except Exception as e:
        st.error(f"AI Model Load Error: {e}")
        return None

model = download_and_load_model()
apply_global_styles()

# --- FABULOUS STYLING OVERDRIVE ---
st.markdown("""
<style>
    /* Deep velvet black-purple base with glitter dust */
    .stApp {
        background: linear-gradient(135deg, #0a0014, #1a0033, #2d004d, #3f0066) !important;
        background-size: 300% 300% !important;
        animation: slowFlow 30s ease infinite !important;
        color: #ffddff !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .stApp::before {
        content: "" !important;
        position: fixed !important;
        inset: 0 !important;
        background: 
            radial-gradient(circle at 10% 20%, rgba(255,102,204,0.08) 1px, transparent 2px),
            radial-gradient(circle at 80% 70%, rgba(204,102,255,0.07) 1.5px, transparent 3px),
            radial-gradient(circle at 40% 90%, rgba(255,153,204,0.09) 1px, transparent 2px) !important;
        background-size: 180px 220px, 240px 280px, 200px 260px !important;
        pointer-events: none !important;
        animation: glitterDrift 140s linear infinite !important;
        opacity: 0.35 !important;
        z-index: -1 !important;
    }

    @keyframes slowFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes glitterDrift {
        0% { transform: translateY(0); }
        100% { transform: translateY(400px); }
    }

    /* Title - massive, glowing, dripping diva energy */
    .inkwell-title {
        font-family: 'Figtree', sans-serif !important;
        font-weight: 900 !important;
        font-size: 4.2rem !important;
        background: linear-gradient(90deg, #ff66cc, #ff99ff, #cc99ff, #ff66cc) !important;
        background-size: 300% !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-shadow: 0 0 30px #ff66cc, 0 0 60px #ff3399, 0 0 90px #cc0066 !important;
        text-align: center !important;
        margin: 0.8rem 0 1.8rem 0 !important;
        letter-spacing: 3px !important;
        animation: titlePulse 8s ease-in-out infinite alternate !important;
    }

    @keyframes titlePulse {
        0% { transform: scale(1); text-shadow: 0 0 30px #ff66cc; }
        100% { transform: scale(1.03); text-shadow: 0 0 50px #ff99ff, 0 0 80px #ff3399; }
    }

    /* Result card - ultimate diva moment */
    .result-card {
        background: linear-gradient(135deg, rgba(40,0,80,0.6), rgba(80,0,140,0.5)) !important;
        border: 3px solid #ff66cc !important;
        border-radius: 24px !important;
        padding: 2.2rem 1.8rem !important;
        text-align: center !important;
        box-shadow: 0 0 50px rgba(255,102,204,0.7), inset 0 0 25px rgba(255,102,204,0.3) !important;
        margin: 2rem 0 !important;
        position: relative !important;
        overflow: hidden !important;
        animation: cardGlow 4s ease-in-out infinite alternate !important;
    }

    .result-card::before {
        content: "✨" !important;
        position: absolute !important;
        top: -20px !important;
        right: 20px !important;
        font-size: 4rem !important;
        opacity: 0.6 !important;
        animation: sparkleFloat 5s ease-in-out infinite !important;
    }

    @keyframes cardGlow {
        0% { box-shadow: 0 0 50px rgba(255,102,204,0.7); }
        100% { box-shadow: 0 0 80px rgba(255,102,204,1); }
    }

    @keyframes sparkleFloat {
        0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.6; }
        50% { transform: translateY(-40px) rotate(20deg); opacity: 1; }
    }

    .result-label {
        font-size: 3rem !important;
        font-weight: 900 !important;
        margin: 0 0 1rem 0 !important;
        text-shadow: 0 0 25px currentColor !important;
    }

    .result-desc {
        font-size: 1.35rem !important;
        color: #ffddff !important;
        text-shadow: 0 0 8px #ff66cc !important;
        margin: 1.2rem 0 !important;
    }

    .confidence {
        font-size: 1.25rem !important;
        color: #ff99ff !important;
        text-shadow: 0 0 12px #ff66cc !important;
        font-weight: 600 !important;
    }

    /* Uploaded image - chrome pink border + inner glow */
    .uploaded-img-container {
        border: 4px solid #ff66cc !important;
        border-radius: 20px !important;
        overflow: hidden !important;
        box-shadow: 0 0 40px rgba(255,102,204,0.6), inset 0 0 30px rgba(255,102,204,0.3) !important;
        margin: 1.5rem auto !important;
        max-width: 580px !important;
        position: relative !important;
    }

    .uploaded-img-container::after {
        content: "" !important;
        position: absolute !important;
        inset: 0 !important;
        background: linear-gradient(45deg, transparent, rgba(255,102,204,0.15), transparent) !important;
        pointer-events: none !important;
        animation: shineOverlay 8s linear infinite !important;
    }

    @keyframes shineOverlay {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    /* File uploader - glowing portal */
    .stFileUploader > div > div > div {
        background: rgba(60,0,100,0.5) !important;
        border: 3px dashed #ff66cc !important;
        border-radius: 16px !important;
        color: #ffddff !important;
        padding: 2rem !important;
        box-shadow: 0 0 30px rgba(255,102,204,0.4) !important;
        transition: all 0.4s ease !important;
    }

    .stFileUploader > div > div > div:hover {
        border-color: #ff99ff !important;
        box-shadow: 0 0 45px rgba(255,102,204,0.7) !important;
        transform: scale(1.02) !important;
    }

    /* Sync button - maximum diva */
    .stButton > button {
        background: linear-gradient(45deg, #ff3399, #ff66cc, #ff99ff, #cc66ff) !important;
        background-size: 400% 400% !important;
        animation: divineShine 6s ease infinite !important;
        color: white !important;
        font-size: 1.45rem !important;
        font-weight: 900 !important;
        padding: 1rem 3rem !important;
        border-radius: 60px !important;
        border: 3px solid #ffffff66 !important;
        box-shadow: 0 15px 45px rgba(255,102,204,0.7) !important;
        margin: 2rem auto !important;
        display: block !important;
    }

    @keyframes divineShine {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stButton > button:hover {
        transform: scale(1.12) translateY(-6px) !important;
        box-shadow: 0 30px 80px rgba(255,102,204,1) !important;
        border-color: #ffffff !important;
    }

    /* Messages */
    .stInfo, .stSuccess, .stError {
        background: rgba(80,0,140,0.55) !important;
        border: 2px solid #ff66cc !important;
        color: #ffddff !important;
        box-shadow: 0 0 25px rgba(255,102,204,0.5) !important;
        border-radius: 14px !important;
        padding: 1.2rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="inkwell-title">Tattoo Health Checker</h1>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload your tattoo photo", type=["jpg", "jpeg", "png"])

# Session state init (unchanged)
if "current_pred" not in st.session_state:
    st.session_state.current_pred = None
if "last_uploaded" not in st.session_state:
    st.session_state.last_uploaded = None

if uploaded_file:
    if st.session_state.current_pred is None or st.session_state.last_uploaded != uploaded_file.name:
        try:
            with st.spinner("Roxy's AI is scanning your ink... 💉✨"):
                img = Image.open(uploaded_file).convert('RGB').resize((224, 224))
                img_array = np.array(img) / 255.0
                img_array = np.expand_dims(img_array, axis=0).astype(np.float32)

                if model is None:
                    st.error("❌ Model is not loaded properly.")
                    st.stop()
                
                predictions = model(img_array, training=False)
                raw_score = float(np.squeeze(predictions))
                
                if raw_score < 0.4:
                    label, color = "Healthy Tattoo", "#00FF88"
                    desc = "Your tattoo looks healthy! Keep up with your aftercare routine."
                elif raw_score < 0.7:
                    label, color = "Monitor Closely", "#FFFF99"
                    desc = "There are some minor signs of irritation. Keep it clean and watch it."
                else:
                    label, color = "Seek Medical Advice", "#ff3399"
                    desc = "Your tattoo shows signs of potential issues. Please consult a professional."

                st.session_state.current_pred = {
                    "label": label,
                    "desc": desc,
                    "color": color,
                    "raw_score": raw_score,
                    "display_score": raw_score if raw_score > 0.5 else 1 - raw_score
                }
                st.session_state.display_img = img
                st.session_state.last_uploaded = uploaded_file.name
        
        except Exception as e:
            st.error(f"❌ Prediction error: {e}")
            st.session_state.current_pred = None

    if st.session_state.current_pred:
        p = st.session_state.current_pred
        
        st.divider()
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="uploaded-img-container">', unsafe_allow_html=True)
            st.image(st.session_state.display_img, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="result-card">
                <h2 class="result-label" style="color: {p['color']}; text-shadow: 0 0 15px {p['color']}88;">{p['label']}</h2>
                <p class="result-desc">{p['desc']}</p>
                <p class="confidence">AI Confidence: {p['display_score']:.1%}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚀 Sync Result with Roxy"):
                if st.session_state.get("tattoo_id"):
                    insert_health_prediction(
                        st.session_state.tattoo_id, 
                        p['raw_score'], 
                        p['label']
                    )
                    st.success("✅ Synced! Roxy is now up to date.")
                else:
                    st.warning("Tattoo ID not found. Are you logged in?")

else:
    st.session_state.current_pred = None
    st.info("Upload a photo to see the AI in action.")