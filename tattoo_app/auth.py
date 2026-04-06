import os
import streamlit as st

def _get_secret(name: str) -> str:
    # Prefer Streamlit secrets, fallback to env (.env)
    if hasattr(st, "secrets") and name in st.secrets:
        return str(st.secrets[name])
    return os.getenv(name, "")

def require_artist() -> bool:
    with st.sidebar:
        st.subheader("Role")
        role = st.selectbox("View as", ["Client", "Artist"], key="role_select")

        if role == "Artist":
            expected = _get_secret("ARTIST_PASSWORD").strip()

            # If you didn't configure a password, never allow access.
            if not expected:
                st.error("ARTIST_PASSWORD is not set. Add ARTIST_PASSWORD to your .env.")
                st.session_state.is_artist = False
                return False

            pwd = st.text_input("Artist password", type="password")
            ok = (pwd.strip() == expected)

            st.session_state.is_artist = bool(ok)
            if not ok:
                st.error("Artist access requires a password.")
            return ok

        st.session_state.is_artist = False
        return False