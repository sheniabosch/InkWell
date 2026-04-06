import streamlit as st
from tattoo_app.db import _read_sheet, upsert_client

st.title("🔗 Google Sheets Connection Test")

# Test 1: Reading
st.subheader("Step 1: Testing Read")
try:
    df = _read_sheet("clients")
    st.write("Successfully connected! Here are your current client headers:")
    st.write(df.columns.tolist())
except Exception as e:
    st.error(f"Read failed: {e}")

# Test 2: Writing
st.subheader("Step 2: Testing Write")
if st.button("Send Test Data"):
    try:
        upsert_client("TEST_ID", "Test", "User", "test@example.com", "555-0000")
        st.success("Write successful! Check your Google Sheet for 'Test User'.")
    except Exception as e:
        st.error(f"Write failed: {e}")