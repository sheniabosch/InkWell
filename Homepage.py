from pathlib import Path
from dotenv import load_dotenv
from tattoo_app.ui_global import apply_global_styles

apply_global_styles()
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

import os
import streamlit as st

# from tattoo_app.db import init_db
from tattoo_app.ui import identity_sidebar

st.set_page_config(page_title="InkWell", layout="wide")
# init_db()

st.title("Tattoo Aftercare Assistant")
# st.caption("Sign in or create profile using the sidebar on the left to get started.")

identity_sidebar()

st.info("Start by Signing In or Creating a Profile using the sidebar on the left.", icon="ℹ️")

# import streamlit as st
# from streamlit_gsheets import GSheetsConnection
# import pandas as pd

# # Connect using the secrets we just set
# conn = st.connection("gsheets", type=GSheetsConnection)

# # Read data – adjust these to your real values
# df = conn.read(
#     spreadsheet="https://docs.google.com/spreadsheets/d/1wSuK0ueT3yPp4M2FBTtIa49h07kOrV5lNONfT2Jm3Qw/edit?gid=1377746673#gid=1377746673",  # Your exact Google Sheet name (or paste the full URL: https://docs.google.com/spreadsheets/d/abc123.../edit)
#     worksheet=0,                     # 0 = first tab, or use tab name like "appointments"
#     ttl="5m"                         # Refresh data every 5 minutes automatically
# )


# Display data in Streamlit app, uncomment below to see the dataframe from Google Sheets
# st.title("Tattoo App Dashboard from Google Sheets")
# st.subheader("Current Data")
# st.dataframe(df)  # Displays the table

# st.write(f"Rows loaded: {len(df)}")