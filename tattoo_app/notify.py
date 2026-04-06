from __future__ import annotations

import os
import json
from typing import Optional

import streamlit as st
import requests

from tattoo_app.db import notification_already_sent, insert_notification_log


def _get_secret(name: str) -> Optional[str]:
    if hasattr(st, "secrets") and name in st.secrets:
        return str(st.secrets[name])
    return os.getenv(name)


def format_alert_message(level: str, reasons_json: str, client_name: str | None, placement: str | None) -> str:
    try:
        reasons = json.loads(reasons_json)
    except Exception:
        reasons = [reasons_json]

    who = client_name or "Client"
    where = f" ({placement})" if placement else ""
    reasons_text = "; ".join(reasons[:6]) if isinstance(reasons, list) else str(reasons)

    return f"[Tattoo Aftercare Alert] {level} for {who}{where}. Reasons: {reasons_text}"


def send_email_sendgrid(alert_id: int, subject: str, body: str) -> None:
    api_key = _get_secret("SENDGRID_API_KEY")
    from_email = _get_secret("SENDGRID_FROM_EMAIL")
    to_email = _get_secret("ARTIST_TO_EMAIL")

    # 🚨 NEVER insert NULL into DB
    if not to_email:
        insert_notification_log(alert_id, "email", "unknown", "failed", error="ARTIST_TO_EMAIL missing")
        return

    if notification_already_sent(alert_id, "email", to_email):
        return

    if not api_key:
        insert_notification_log(alert_id, "email", to_email, "failed", error="SENDGRID_API_KEY missing")
        return

    if not from_email:
        insert_notification_log(alert_id, "email", to_email, "failed", error="SENDGRID_FROM_EMAIL missing")
        return

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers=headers,
            json=payload,
            timeout=20,
        )

        if response.status_code in (200, 201, 202):
            insert_notification_log(
                alert_id,
                "email",
                to_email,
                "sent",
                provider_message_id=f"sendgrid:{response.status_code}",
            )
            return

        # Log SendGrid error body
        error_text = (response.text or "")[:4000]
        insert_notification_log(
            alert_id,
            "email",
            to_email,
            "failed",
            error=f"SendGrid {response.status_code}: {error_text}",
        )

    except Exception as e:
        insert_notification_log(alert_id, "email", to_email, "failed", error=str(e))


def notify_artist_for_alert(
    alert_id: int,
    level: str,
    reasons_json: str,
    client_name: str | None = None,
    placement: str | None = None,
) -> None:
    text = format_alert_message(level, reasons_json, client_name, placement)

    # Email only
    if level in ("High", "Critical"):
        send_email_sendgrid(
            alert_id,
            subject=f"Tattoo aftercare alert: {level}",
            body=text,
        )