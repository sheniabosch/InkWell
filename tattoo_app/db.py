import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import json
from typing import Any

# Establish Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# --- HELPER FUNCTIONS ---

def _read_sheet(sheet_name: str) -> pd.DataFrame:
    """Reads a specific tab and returns a DataFrame."""
    return conn.read(worksheet=sheet_name, ttl=0) # ttl=0 ensures fresh data

def _append_row(sheet_name: str, data_dict: dict):
    """Adds a new row to the specified sheet."""
    df = _read_sheet(sheet_name)
    if 'created_at' not in data_dict:
        data_dict['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_row = pd.DataFrame([data_dict])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    conn.update(worksheet=sheet_name, data=updated_df)

def _update_row(sheet_name: str, id_col: str, id_val: str, updated_fields: dict):
    """Updates an existing row based on an ID."""
    df = _read_sheet(sheet_name)
    if id_val in df[id_col].values:
        for key, val in updated_fields.items():
            df.loc[df[id_col] == id_val, key] = val
        conn.update(worksheet=sheet_name, data=df)
    else:
        # If it doesn't exist, append it (Upsert logic)
        updated_fields[id_col] = id_val
        _append_row(sheet_name, updated_fields)

# --- APP FUNCTIONS ---

def upsert_client(client_id: str, first_name: str, last_name: str, email: str, phone: str):
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone
    }
    _update_row("clients", "client_id", client_id, data)

def upsert_tattoo(tattoo_id: str, client_id: str, placement: str, tattoo_date: str):
    data = {
        "client_id": client_id,
        "placement": placement,
        "tattoo_date": tattoo_date
    }
    _update_row("tattoos", "tattoo_id", tattoo_id, data)

def insert_risk_assessment(client_id: str, answers_json: str, risk_score: int, risk_tier: str, drivers_json: str):
    data = {
        "client_id": client_id,
        "answers_json": answers_json,
        "risk_score": risk_score,
        "risk_tier": risk_tier,
        "drivers_json": drivers_json
    }
    _append_row("risk_assessments", data)

def insert_daily_checkin(tattoo_id: str, day_index: int, pain: int, redness_level: int, **kwargs):
    data = {"tattoo_id": tattoo_id, "day_index": day_index, "pain": pain, "redness_level": redness_level}
    data.update(kwargs)
    _append_row("daily_checkins", data)

# --- FETCHING FUNCTIONS ---

def fetch_client(client_id: str):
    df = _read_sheet("clients")
    res = df[df['client_id'] == client_id]
    return res.iloc[0].to_dict() if not res.empty else None

def fetch_latest_risk(client_id: str):
    df = _read_sheet("risk_assessments")
    res = df[df['client_id'] == client_id].sort_values('created_at', ascending=False)
    return res.iloc[0].to_dict() if not res.empty else None

def fetch_latest_tattoo_for_client(client_id: str):
    df = _read_sheet("tattoos")
    res = df[df['client_id'] == client_id].sort_values('created_at', ascending=False)
    return res.iloc[0].to_dict() if not res.empty else None

# --- ALERT LOGIC ---

def insert_alert(tattoo_id: str, level: str, reasons: list):
    # New Format: TattooID-Level-Timestamp (e.g., Forearm2023-10-25-CRITICAL-1430)
    timestamp = datetime.now().strftime("%H%M")
    new_id = f"{tattoo_id}-{level.upper()}-{timestamp}"
    
    data = {
        "alert_id": new_id,
        "tattoo_id": tattoo_id,
        "level": level,
        "reasons_json": json.dumps(reasons),
        "status": "open"
    }
    _append_row("alerts", data)
    return new_id

def ack_alert(alert_id: int):
    _update_row("alerts", "alert_id", alert_id, {"status": "ack"})

def resolve_alert(alert_id: int):
    _update_row("alerts", "alert_id", alert_id, {
        "status": "resolved", 
        "resolved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# --- DASHBOARD LOGIC (THE "SQL JOIN" REPLACEMENT) ---

def fetch_artist_dashboard_rows():
    clients = _read_sheet("clients")
    tattoos = _read_sheet("tattoos")
    risks = _read_sheet("risk_assessments").sort_values('created_at').groupby('client_id').last().reset_index()
    checkins = _read_sheet("daily_checkins").sort_values('created_at').groupby('tattoo_id').last().reset_index()

    # Merge dataframes (Simulating the SQL JOIN)
    merged = clients.merge(tattoos, on="client_id", how="left")
    merged = merged.merge(risks, on="client_id", how="left", suffixes=('', '_risk'))
    merged = merged.merge(checkins, on="tattoo_id", how="left", suffixes=('', '_checkin'))
    
    return merged.to_dict(orient="records")
def notification_already_sent(alert_id: int, channel: str, to_address: str) -> bool:
    """Checks if a notification has already been sent to avoid duplicates."""
    df = _read_sheet("notifications")
    if df.empty:
        return False
    
    # Filter for matching alert, channel, address, and 'sent' status
    match = df[
        (df['alert_id'].astype(str) == str(alert_id)) & 
        (df['channel'] == channel) & 
        (df['to_address'] == to_address) & 
        (df['status'] == 'sent')
    ]
    return not match.empty

def insert_notification_log(
    alert_id: int,
    channel: str,
    to_address: str,
    status: str,
    provider_message_id: str = None,
    error: str = None,
) -> None:
    """Logs a notification attempt to the notifications tab."""
    data = {
        "alert_id": alert_id,
        "channel": channel,
        "to_address": to_address,
        "status": status,
        "provider_message_id": provider_message_id,
        "error": error
    }
    _append_row("notifications", data)

def fetch_recent_checkins(tattoo_id: str, limit: int = 3) -> list[dict]:
    """Fetches the last X checkins for a specific tattoo."""
    df = _read_sheet("daily_checkins")
    res = df[df['tattoo_id'] == tattoo_id].sort_values('created_at', ascending=False)
    return res.head(limit).to_dict(orient="records")

def fetch_open_alert_counts() -> dict[str, int]:
    """Counts open alerts grouped by level (Watch/High/Critical)."""
    df = _read_sheet("alerts")
    if df.empty:
        return {}
    open_alerts = df[df['status'] == 'open']
    counts = open_alerts['level'].value_counts().to_dict()
    return counts

def fetch_open_alerts_for_tattoo(tattoo_id: str) -> list[dict]:
    """Fetches all alerts for a specific tattoo that are currently 'open'."""
    df = _read_sheet("alerts")
    if df.empty:
        return []
    
    # Filter for the tattoo and ensure the status is exactly 'open'
    mask = (df['tattoo_id'].astype(str) == str(tattoo_id)) & (df['status'] == 'open')
    res = df[mask].sort_values('created_at', ascending=False)
    
    return res.to_dict(orient="records")

def fetch_latest_checkin(tattoo_id: str) -> dict[str, Any] | None:
    """Gets the single most recent check-in for a specific tattoo."""
    df = _read_sheet("daily_checkins")
    if df.empty:
        return None
    
    # Filter by tattoo_id and sort by time
    res = df[df['tattoo_id'].astype(str) == str(tattoo_id)].sort_values('created_at', ascending=False)
    
    # Return the first row as a dictionary if it exists
    return res.iloc[0].to_dict() if not res.empty else None

from datetime import datetime

def insert_health_prediction(tattoo_id: str, prediction_score: float, label: str) -> None:
    """Saves a CNN model prediction result to the health_predictions sheet."""
    data = {
        "tattoo_id": tattoo_id,
        "prediction_score": float(prediction_score),
        "health_prediction": label,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    _append_row("health_predictions", data)

def fetch_latest_prediction(tattoo_id: str) -> dict | None:
    """Fetches the most recent AI health prediction for a specific tattoo."""
    df = _read_sheet("health_predictions")
    if df.empty:
        return None
    
    # Filter by tattoo_id and get the most recent entry
    res = df[df['tattoo_id'].astype(str) == str(tattoo_id)].sort_values('created_at', ascending=False)
    
    return res.iloc[0].to_dict() if not res.empty else None