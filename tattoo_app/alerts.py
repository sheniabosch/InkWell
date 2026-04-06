from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

AlertLevel = Literal["Watch", "High", "Critical"]

@dataclass
class AlertDecision:
    level: AlertLevel | None
    reasons: list[str]

def _level_rank(level: AlertLevel) -> int:
    return {"Watch": 1, "High": 2, "Critical": 3}[level]

def decide_alert_from_checkins(recent: list[dict]) -> AlertDecision:
    """
    recent: list of checkins ordered newest-first (len 1..3)
    Uses rules + trends to produce an alert decision.
    """
    if not recent:
        return AlertDecision(level=None, reasons=[])

    newest = recent[0]
    reasons: list[str] = []
    level: AlertLevel | None = None

    # --- Critical rules (immediate attention) ---
    if newest.get("fever", 0) == 1:
        level = "Critical"
        reasons.append("Fever/chills reported")

    # discharge_level: 0 none, 1 clear, 2 cloudy, 3 yellow/green
    if newest.get("discharge_level", 0) >= 3 and newest.get("pain", 0) >= 6:
        level = "Critical"
        reasons.append("Yellow/green discharge with high pain")

    if newest.get("redness_level", 0) >= 3 and newest.get("warmth", 0) == 1:
        level = "Critical"
        reasons.append("Spreading redness with warmth")

    # --- High rules ---
    if level is None:
        if newest.get("odor", 0) == 1:
            level = "High"
            reasons.append("Odor reported")

        if newest.get("pain", 0) >= 7:
            level = "High"
            reasons.append("High pain level")

        if newest.get("redness_level", 0) >= 2 and newest.get("swelling_level", 0) >= 2:
            level = "High"
            reasons.append("Redness and swelling both moderate+")

    # --- Trend detection (needs >= 2 checkins) ---
    if len(recent) >= 2:
        prev = recent[1]
        pain_delta = (newest.get("pain", 0) - prev.get("pain", 0))
        red_delta = (newest.get("redness_level", 0) - prev.get("redness_level", 0))
        swell_delta = (newest.get("swelling_level", 0) - prev.get("swelling_level", 0))

        if pain_delta >= 3:
            reasons.append(f"Pain increased by {pain_delta} since last check-in")
            level = max(level or "Watch", "High", key=_level_rank)

        if red_delta >= 1 and newest.get("redness_level", 0) >= 2:
            reasons.append("Redness worsening")
            level = max(level or "Watch", "High", key=_level_rank)

        if swell_delta >= 1 and newest.get("swelling_level", 0) >= 2:
            reasons.append("Swelling worsening")
            level = max(level or "Watch", "High", key=_level_rank)

    # --- Longer trend (needs >= 3 checkins): worsening 2 days in a row ---
    if len(recent) >= 3:
        mid = recent[1]
        old = recent[2]
        if newest.get("redness_level", 0) > mid.get("redness_level", 0) > old.get("redness_level", 0):
            reasons.append("Redness increased two check-ins in a row")
            level = max(level or "Watch", "High", key=_level_rank)

    # --- Watch-level triggers if nothing else ---
    if level is None:
        if newest.get("itch", 0) >= 8:
            level = "Watch"
            reasons.append("High itch level (risk of scratching)")
        elif newest.get("redness_level", 0) == 1 and newest.get("warmth", 0) == 1:
            level = "Watch"
            reasons.append("Mild redness with warmth")

    return AlertDecision(level=level, reasons=reasons[:5])
