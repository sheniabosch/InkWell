import base64
import streamlit as st

def apply_global_styles():
    """
    INKWELL · Updated Gothic Unicorn Drag Queen Energy
    Slim top banner + very dark purple-black bg + subtle falling glitter
    Fonts: Figtree (headings), Jost (body)
    """
    
    # ──────────────────────────────────────────────────────────────
    # EMBED YOUR LOCAL BANNER DIRECTLY
    # ──────────────────────────────────────────────────────────────
    banner_path = "/Users/sheniabosch/Library/CloudStorage/GoogleDrive-sheniabosch@gmail.com/My Drive/InkWell/design_elements/inkwellbanner_logo.png"
    
    try:
        with open(banner_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        banner_url = f"data:image/png;base64,{encoded}"
    except FileNotFoundError:
        banner_url = "https://via.placeholder.com/1400x120/330066/ffffff?text=✨+INKWELL+✨+(banner+missing)"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500;600;700;800&family=Figtree:wght@400;500;600;700;800;900&display=swap');

        /* Very dark purple-black background */
        .stApp {{
            background: linear-gradient(135deg, #0a000f, #12001a, #1a0026, #220033);
            background-size: 300% 300%;
            animation: deepPulse 25s ease infinite;
            color: #e6d9ff;
            min-height: 100vh;
            font-family: 'Jost', sans-serif;
            position: relative;
            overflow: hidden;
        }}

        @keyframes deepPulse {{
            0%   {{ background-position: 0% 50%; }}
            50%  {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        /* Subtle falling glitter particles */
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background: 
                radial-gradient(circle at 15% 25%, rgba(255,80,220,0.7) 1.2px, transparent 2.5px),
                radial-gradient(circle at 45% 60%, rgba(180,60,255,0.6) 1px, transparent 2px),
                radial-gradient(circle at 75% 40%, rgba(255,140,220,0.65) 1.4px, transparent 2.8px),
                radial-gradient(circle at 30% 80%, rgba(220,100,255,0.55) 1px, transparent 2px);
            background-size: 180px 220px, 240px 280px, 200px 260px, 220px 300px;
            opacity: 0.35;
            animation: glitterDrift 120s linear infinite;
            z-index: -1;
        }}

        @keyframes glitterDrift {{
            0%   {{ background-position: 0 0, 0 0, 0 0, 0 0; transform: translateY(0); }}
            100% {{ background-position: 100px 400px, -80px 500px, 120px 450px, -60px 520px; transform: translateY(400px); }}
        }}

        /* Slim fixed banner at the top */
        .inkwell-banner {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 999;
            text-align: center;
            padding: 8px 0;
            background: linear-gradient(90deg, #2a004d, #4d0099, #7a00cc, #4d0099, #2a004d);
            background-size: 300% 300%;
            animation: bannerGlow 18s ease infinite;
            box-shadow: 0 6px 20px rgba(100,0,180,0.6);
            border-bottom: 2px solid rgba(255,80,220,0.4);
        }}

        .inkwell-banner img {{
            max-height: 100px;
            width: auto;
            max-width: 92%;
            border-radius: 12px;
            filter: drop-shadow(0 0 20px #ff33cc) brightness(1.1);
            border: 1px solid rgba(255,140,220,0.5);
        }}

        @keyframes bannerGlow {{
            0%   {{ background-position: 0% 50%; }}
            50%  {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        /* Add top padding so content isn't hidden under fixed banner */
        .stApp > div:first-child {{
            padding-top: 140px !important;
        }}

        /* Headings — Figtree */
        h1, h2, h3 {{
            font-family: 'Figtree', sans-serif;
            font-weight: 700;
            color: #ff66cc !important;
            text-shadow: 
                0 0 12px #ff33cc,
                0 0 24px #ff00cc,
                0 0 40px #cc00aa;
            letter-spacing: 1.5px;
        }}

        h1 {{ font-size: 3.8rem !important; margin: 0.5rem 0; }}
        h2 {{ font-size: 2.8rem !important; }}
        h3 {{ font-size: 2.1rem !important; }}

        /* Body text */
        p, div, span, label, li, .stMarkdown {{
            font-family: 'Jost', sans-serif;
            color: #e8d9ff;
            text-shadow: 0 0 4px rgba(255,80,220,0.3);
        }}

        /* Sidebar — darker velvet */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0f001a, #1f0033);
            border-right: 3px solid #cc66ff88;
            box-shadow: -10px 0 40px #9900ff44;
        }}

        /* Buttons — still diva but toned down a bit */
        .stButton > button {{
            background: linear-gradient(45deg, #cc33aa, #ff66cc, #cc33ff, #ff66ff);
            background-size: 300% 300%;
            animation: shineFlow 10s ease infinite;
            color: white !important;
            font-family: 'Jost', sans-serif;
            font-weight: 700;
            font-size: 1.15rem;
            letter-spacing: 1px;
            border: 2px solid #ff99dd;
            border-radius: 40px;
            padding: 0.8rem 2.2rem;
            box-shadow: 0 10px 30px rgba(200,0,180,0.5);
            transition: all 0.3s ease;
        }}

        @keyframes shineFlow {{
            0%   {{ background-position: 0% 50%; }}
            50%  {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        .stButton > button:hover {{
            transform: translateY(-4px) scale(1.08);
            box-shadow: 0 20px 50px rgba(220,50,200,0.8);
            border-color: #ffffff99;
        }}

        /* Hide Streamlit junk */
        #MainMenu, footer, header > div:first-child {{ visibility: hidden !important; }}
        footer {{ display: none !important; }}

    </style>

    <!-- Slim fixed banner -->
    <div class="inkwell-banner">
        <img src="{banner_url}" alt="Inkwell Banner">
    </div>
    """, unsafe_allow_html=True)


# ———————————————————————————————
# CALL IT AT THE VERY TOP OF YOUR APP
# ———————————————————————————————
# apply_global_styles()