"""Explainable 0-100 priority score for a processed alert."""
from typing import Dict

SEVERITY_POINTS = {"LOW": 10, "MEDIUM": 25, "HIGH": 40, "CRITICAL": 55}
CRITICALITY_POINTS = {"LOW": 3, "MEDIUM": 8, "HIGH": 15}
CATEGORY_RISK_POINTS = {
    "Data Exfiltration": 12,
    "Malware Activity": 10,
    "Denial of Service": 8,
    "Web Attack": 7,
    "Authentication Threat": 6,
    "Network Scanning": 4,
    "Uncategorized": 2,
}
ANOMALY_POINTS = 10
FREQUENCY_POINTS_CAP = 8


def compute_priority(predicted_severity: str, anomaly_status: str, asset_criticality: str,
                      category: str, source_ip_frequency: int) -> Dict:
    severity_pts = SEVERITY_POINTS.get(predicted_severity, 10)
    criticality_pts = CRITICALITY_POINTS.get(asset_criticality, 8)
    category_pts = CATEGORY_RISK_POINTS.get(category, 2)
    anomaly_pts = ANOMALY_POINTS if anomaly_status == "ANOMALY" else 0
    frequency_pts = min(FREQUENCY_POINTS_CAP, source_ip_frequency // 3)

    raw_score = severity_pts + criticality_pts + category_pts + anomaly_pts + frequency_pts
    score = max(0, min(100, raw_score))

    if score >= 75:
        level = "CRITICAL"
    elif score >= 50:
        level = "HIGH"
    elif score >= 25:
        level = "MEDIUM"
    else:
        level = "LOW"

    breakdown = {
        "severity_points": severity_pts,
        "asset_criticality_points": criticality_pts,
        "category_risk_points": category_pts,
        "anomaly_points": anomaly_pts,
        "frequency_points": frequency_pts,
    }

    return {"priority_score": score, "priority_level": level, "breakdown": breakdown}
