"""Generates a dynamic, per-alert natural-language explanation from actual features."""
from typing import Dict


def generate_explanation(alert: Dict, priority_breakdown: Dict, source_ip_frequency: int) -> str:
    severity = alert.get("predicted_severity", "LOW")
    level = alert.get("priority_level", "LOW")
    reasons = []

    if priority_breakdown.get("severity_points", 0) >= 40:
        reasons.append(f"the AI model predicted a {severity.lower()} severity level")
    if priority_breakdown.get("anomaly_points", 0) > 0:
        reasons.append("the source activity was flagged as statistically anomalous")
    if priority_breakdown.get("asset_criticality_points", 0) >= 15:
        reasons.append("the affected asset has high business criticality")
    if priority_breakdown.get("category_risk_points", 0) >= 8:
        reasons.append(f"the alert category ({alert.get('category', 'Uncategorized')}) is high-risk")
    if source_ip_frequency >= 6:
        reasons.append(f"the source IP {alert.get('source_ip')} generated {source_ip_frequency} alerts in this batch, indicating elevated activity")

    if not reasons:
        reasons.append("no strong risk indicators were present in the alert features")

    if len(reasons) == 1:
        reason_text = reasons[0]
    else:
        reason_text = ", ".join(reasons[:-1]) + f", and {reasons[-1]}"

    return f"This alert was prioritized as {level} because {reason_text}."
