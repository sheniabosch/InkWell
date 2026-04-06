from __future__ import annotations
from dataclasses import dataclass
import json

@dataclass
class RiskResult:
    score: int
    tier: str
    drivers: list[str]

def clamp(x: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, x))

def score_risk(answers: dict) -> RiskResult:
    # Baseline health (0–30)
    baseline = 0
    drivers = []

    if answers.get("immune_issue") == "Yes":
        baseline += 15; drivers.append("Immune/medical risk factor")
    if answers.get("diabetes") == "Yes":
        baseline += 10; drivers.append("Diabetes/slow healing risk")
    if answers.get("smoking") == "Daily":
        baseline += 8; drivers.append("Daily smoking/vaping")
    elif answers.get("smoking") == "Occasional":
        baseline += 4

    # Exposure (0–25)
    exposure = 0
    env = answers.get("work_env")
    if env in {"Outdoors", "Dust/Chemicals", "Healthcare/Childcare"}:
        exposure += 10; drivers.append("Higher exposure environment")
    if answers.get("pets") == "Yes":
        exposure += 5; drivers.append("Pets (scratch/lick risk)")
    if answers.get("handwashing") == "Limited":
        exposure += 8; drivers.append("Limited handwashing access")

    # Activity & moisture (0–25)
    activity = 0
    if answers.get("exercise") == "Intense":
        activity += 12; drivers.append("Intense exercise early")
    elif answers.get("exercise") == "Light":
        activity += 4
    if answers.get("water_exposure") == "Yes":
        activity += 10; drivers.append("Planned water exposure")
    friction = answers.get("friction_area")
    if friction == "High":
        activity += 8; drivers.append("High-friction placement")
    elif friction == "Medium":
        activity += 4

    # Skin sensitivity (0–20)
    sensitivity = 0
    if answers.get("eczema") == "Active":
        sensitivity += 12; drivers.append("Active eczema/dermatitis")
    elif answers.get("eczema") == "Mild/History":
        sensitivity += 6
    if answers.get("product_reaction") == "Yes":
        sensitivity += 8; drivers.append("History of product reactions")

    total = clamp(baseline + exposure + activity + sensitivity)

    if total >= 60:
        tier = "High"
    elif total >= 30:
        tier = "Medium"
    else:
        tier = "Low"

    # Keep top 3 drivers
    drivers = drivers[:3] if drivers else ["No major risk drivers selected"]
    return RiskResult(score=total, tier=tier, drivers=drivers)

def dumps_answers(answers: dict) -> str:
    return json.dumps(answers, ensure_ascii=False)

def dumps_drivers(drivers: list[str]) -> str:
    return json.dumps(drivers, ensure_ascii=False)
