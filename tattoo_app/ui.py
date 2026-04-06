import streamlit as st
from tattoo_app.db import upsert_client, upsert_tattoo, fetch_client, fetch_latest_tattoo_for_client

# def identity_sidebar():
#     with st.sidebar:
#         st.header("Already have a client profile?")

#         # --- 1. LOAD EXISTING PROFILE ---
#         with st.expander("Enter your client ID to load profile"):
#             existing_id = st.text_input("ID Example: JaneDoe1234", key="existing_client_id_input")
#             if st.button("Load Profile"):
#                 client = fetch_client(existing_id.strip())
#                 if not client:
#                     st.error("Client ID not found. Check spelling and capitalization.")
#                 else:
#                     st.session_state.client_id = client["client_id"]
#                     st.session_state.first_name = client["first_name"]
#                     st.session_state.last_name = client["last_name"]
#                     st.session_state.email = client.get("email") or ""
#                     st.session_state.phone = client.get("phone") or ""

#                     tat = fetch_latest_tattoo_for_client(client["client_id"])
#                     if tat:
#                         st.session_state.tattoo_id = tat["tattoo_id"]
#                         st.session_state.placement = tat.get("placement") or ""
#                         st.session_state.tattoo_date = tat.get("tattoo_date") or ""

#                     st.success("Profile loaded.")

#         st.divider()

#         # --- 2. CREATE/UPDATE PROFILE FORM ---
#         st.subheader("Profile Details")
#         with st.form("profile_form", clear_on_submit=False):
#             first_name = st.text_input("First name", value=st.session_state.get("first_name", ""))
#             last_name = st.text_input("Last name", value=st.session_state.get("last_name", ""))
#             email = st.text_input("Email", value=st.session_state.get("email", ""))
#             phone = st.text_input("Phone number", value=st.session_state.get("phone", ""))

#             st.write("---")
#             placement = st.text_input("Tattoo placement (e.g., Forearm)", value=st.session_state.get("placement", ""))
#             tattoo_date = st.text_input("Tattoo date (YYYY-MM-DD)", value=st.session_state.get("tattoo_date", ""))

#             submitted = st.form_submit_button("Save Profile & Generate IDs")

#         if submitted:
#             # Validate required fields for ID generation
#             if not (first_name and last_name and phone and placement and tattoo_date):
#                 st.error("Please fill in all fields to generate your unique IDs.")
#             else:
#                 # --- ID GENERATION LOGIC ---
                
#                 # Client ID: FirstName + LastName + Last4 of Phone
#                 clean_fn = first_name.strip().replace(" ", "")
#                 clean_ln = last_name.strip().replace(" ", "")
#                 last_4 = str(phone.strip())[-4:]
#                 st.session_state.client_id = f"{clean_fn}{clean_ln}{last_4}"

#                 # Tattoo ID: Placement + Date
#                 clean_placement = placement.strip().replace(" ", "")
#                 clean_date = tattoo_date.strip()
#                 st.session_state.tattoo_id = f"{clean_placement}{clean_date}"

#                 # Save to DB
#                 upsert_client(
#                     client_id=st.session_state.client_id,
#                     first_name=first_name.strip(),
#                     last_name=last_name.strip(),
#                     email=email.strip() or None,
#                     phone=phone.strip() or None,
#                 )

#                 upsert_tattoo(
#                     tattoo_id=st.session_state.tattoo_id,
#                     client_id=st.session_state.client_id,
#                     placement=placement.strip() or None,
#                     tattoo_date=tattoo_date.strip() or None,
#                 )

#                 # Store other details in session
#                 st.session_state.first_name = first_name.strip()
#                 st.session_state.last_name = last_name.strip()
#                 st.session_state.email = email.strip()
#                 st.session_state.phone = phone.strip()
#                 st.session_state.placement = placement.strip()
#                 st.session_state.tattoo_date = tattoo_date.strip()

#                 st.success(f"Profile Active! ID: **{st.session_state.client_id}**")

#         # --- 3. SESSION FOOTER ---
#         if st.session_state.get("client_id"):
#             st.info(f"👤 **{st.session_state.client_id}**")
#             st.caption(f"📍 Tattoo ID: {st.session_state.get('tattoo_id')}")

def identity_sidebar():
    # Inject custom sidebar styles (visuals only)
    st.markdown("""
    <style>
        /* Sidebar base - deep velvet darkness */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f0015, #180022, #220033) !important;
            border-right: 3px solid rgba(204, 68, 255, 0.35) !important;
            box-shadow: -12px 0 35px rgba(120, 0, 200, 0.4) !important;
        }

        /* Soft overall text glow */
        [data-testid="stSidebar"] * {
            text-shadow: 0 0 5px rgba(200, 60, 220, 0.3) !important;
        }

        /* Removed the glowing bar / block background - no more extra div glow */

        /* Expander - bigger, dramatic, with subtle shimmer border */
        [data-testid="stSidebar"] .stExpander summary {
            font-size: 1.4rem !important;
            font-weight: 700 !important;
            color: #ff70cc !important;
            text-shadow: 0 0 15px #ff33aa, 0 0 26px #cc0099 !important;
            padding: 1.1rem 1.3rem !important;
            background: rgba(35, 0, 70, 0.4) !important;
            border-radius: 14px !important;
            border: 1.5px solid rgba(220, 90, 255, 0.45) !important;
            box-shadow: 0 0 18px rgba(180, 40, 240, 0.4) !important;
            animation: subtleShimmer 8s ease-in-out infinite alternate !important;
        }

        @keyframes subtleShimmer {
            0%   { border-color: rgba(220, 90, 255, 0.45); box-shadow: 0 0 18px rgba(180, 40, 240, 0.4); }
            100% { border-color: rgba(255, 140, 220, 0.7);  box-shadow: 0 0 28px rgba(220, 80, 255, 0.65); }
        }

        /* Interactive elements - larger & more dramatic */
        [data-testid="stSidebar"] .stTextInput > div > div > input,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] button {
            font-size: 1.22rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.7px !important;
            color: #e8d9ff !important;
        }

        /* Form submit button - diva energy */
        [data-testid="stSidebar"] .stForm [kind="primary"] {
            background: linear-gradient(45deg, #cc33aa, #ff55cc, #aa33ff, #ff66ff) !important;
            background-size: 400% 400% !important;
            animation: buttonPulse 7s ease infinite !important;
            font-size: 1.35rem !important;
            font-weight: 800 !important;
            padding: 1rem 2.4rem !important;
            border-radius: 50px !important;
            box-shadow: 0 14px 40px rgba(180, 0, 200, 0.65) !important;
            border: 2px solid #ff99dd !important;
            transition: all 0.35s ease !important;
        }

        [data-testid="stSidebar"] .stForm [kind="primary"]:hover {
            transform: scale(1.08) translateY(-3px) !important;
            box-shadow: 0 24px 55px rgba(220, 50, 220, 0.85) !important;
            border-color: #ffffff !important;
        }

        @keyframes buttonPulse {
            0%   { background-position: 0% 50%; }
            50%  { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Headers - keep dramatic glow */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2 {
            font-size: 1.5rem !important;
            margin: 0.7rem 0 1.3rem !important;
            color: #ff80cc !important;
            text-shadow: 0 0 18px #ff33aa, 0 0 32px #cc0099, 0 0 50px #990066 !important;
            font-weight: 800 !important;
            letter-spacing: 1.4px !important;
        }

        [data-testid="stSidebar"] h3 {
            font-size: 1.65rem !important;
            color: #cc66ff !important;
            text-shadow: 0 0 14px #aa33ff, 0 0 26px #8833cc !important;
            margin: 2rem 0 1.2rem !important;
        }

        /* Success message - floating sparkle accent */
        [data-testid="stSidebar"] .stSuccess {
            background: linear-gradient(135deg, rgba(80, 20, 140, 0.6), rgba(140, 40, 220, 0.5)) !important;
            border: 1.5px solid rgba(220, 100, 255, 0.6) !important;
            color: #f8f0ff !important;
            box-shadow: 0 0 30px rgba(180, 60, 255, 0.55) !important;
            position: relative !important;
            overflow: hidden !important;
        }

        [data-testid="stSidebar"] .stSuccess::before {
            content: "✨" !important;
            position: absolute !important;
            top: -10px !important;
            right: 10px !important;
            font-size: 1.8rem !important;
            opacity: 0.7 !important;
            animation: sparkleFloat 4s ease-in-out infinite !important;
        }

        @keyframes sparkleFloat {
            0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.7; }
            50%      { transform: translateY(-15px) rotate(15deg); opacity: 1; }
        }

        /* Info messages */
        [data-testid="stSidebar"] .stInfo {
            background: rgba(60, 0, 120, 0.5) !important;
            border: 1px solid rgba(180, 60, 255, 0.55) !important;
            color: #f0e0ff !important;
            box-shadow: 0 0 22px rgba(140, 0, 220, 0.45) !important;
        }

        /* Divider */
        [data-testid="stSidebar"] hr {
            border-color: rgba(200, 80, 255, 0.4) !important;
            margin: 2rem 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("Already have a client profile?")

        # --- 1. LOAD EXISTING PROFILE ---
        with st.expander("Enter your client ID to load profile"):
            existing_id = st.text_input("ID Example: JaneDoe1234", key="existing_client_id_input")
            if st.button("Load Profile"):
                client = fetch_client(existing_id.strip())
                if not client:
                    st.error("Client ID not found. Check spelling and capitalization.")
                else:
                    st.session_state.client_id = client["client_id"]
                    st.session_state.first_name = client["first_name"]
                    st.session_state.last_name = client["last_name"]
                    st.session_state.email = client.get("email") or ""
                    st.session_state.phone = client.get("phone") or ""

                    tat = fetch_latest_tattoo_for_client(client["client_id"])
                    if tat:
                        st.session_state.tattoo_id = tat["tattoo_id"]
                        st.session_state.placement = tat.get("placement") or ""
                        st.session_state.tattoo_date = tat.get("tattoo_date") or ""

                    st.success("Profile loaded.")

        st.divider()

        # --- 2. CREATE/UPDATE PROFILE FORM ---
        st.subheader("Profile Details")
        with st.form("profile_form", clear_on_submit=False):
            first_name = st.text_input("First name", value=st.session_state.get("first_name", ""))
            last_name = st.text_input("Last name", value=st.session_state.get("last_name", ""))
            email = st.text_input("Email", value=st.session_state.get("email", ""))
            phone = st.text_input("Phone number", value=st.session_state.get("phone", ""))

            st.write("---")
            placement = st.text_input("Tattoo placement (e.g., Forearm)", value=st.session_state.get("placement", ""))
            tattoo_date = st.text_input("Tattoo date (YYYY-MM-DD)", value=st.session_state.get("tattoo_date", ""))

            submitted = st.form_submit_button("Save Profile & Generate IDs")

        if submitted:
            # Validate required fields for ID generation
            if not (first_name and last_name and phone and placement and tattoo_date):
                st.error("Please fill in all fields to generate your unique IDs.")
            else:
                # --- ID GENERATION LOGIC ---
                
                # Client ID: FirstName + LastName + Last4 of Phone
                clean_fn = first_name.strip().replace(" ", "")
                clean_ln = last_name.strip().replace(" ", "")
                last_4 = str(phone.strip())[-4:]
                st.session_state.client_id = f"{clean_fn}{clean_ln}{last_4}"

                # Tattoo ID: Placement + Date
                clean_placement = placement.strip().replace(" ", "")
                clean_date = tattoo_date.strip()
                st.session_state.tattoo_id = f"{clean_placement}{clean_date}"

                # Save to DB
                upsert_client(
                    client_id=st.session_state.client_id,
                    first_name=first_name.strip(),
                    last_name=last_name.strip(),
                    email=email.strip() or None,
                    phone=phone.strip() or None,
                )

                upsert_tattoo(
                    tattoo_id=st.session_state.tattoo_id,
                    client_id=st.session_state.client_id,
                    placement=placement.strip() or None,
                    tattoo_date=tattoo_date.strip() or None,
                )

                # Store other details in session
                st.session_state.first_name = first_name.strip()
                st.session_state.last_name = last_name.strip()
                st.session_state.email = email.strip()
                st.session_state.phone = phone.strip()
                st.session_state.placement = placement.strip()
                st.session_state.tattoo_date = tattoo_date.strip()

                st.success(f"Profile Active! ID: **{st.session_state.client_id}**")

        # --- 3. SESSION FOOTER ---
        if st.session_state.get("client_id"):
            st.info(f"👤 **{st.session_state.client_id}**")
            st.caption(f"📍 Tattoo ID: {st.session_state.get('tattoo_id')}")