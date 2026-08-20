"""Generates a realistic, labeled cybersecurity training dataset for the
Random Forest severity classifier.

Methodology (documented in README): labels are assigned using domain rules
that mirror how a SOC analyst would triage severity - category risk,
asset criticality, and port sensitivity all push severity up or down, with
some random jitter added so the model has to learn genuine decision
boundaries rather than a lookup table. This is a synthetic but structurally
realistic dataset because no public labeled SOC alert-severity dataset with
these exact fields is bundled with the project.
"""
import random
from datetime import datetime, timedelta

import pandas as pd

from app.ml.severity_model import CATEGORY_LIST, PROTOCOL_LIST, CRITICALITY_LIST

SENSITIVE_PORTS = {22, 23, 3389, 445, 1433, 3306, 5432, 21}

random.seed(42)


def _severity_for(category, criticality, port, hour):
    score = 0
    score += {"Data Exfiltration": 4, "Malware Activity": 3, "Denial of Service": 3,
              "Web Attack": 2, "Authentication Threat": 2, "Network Scanning": 1,
              "Uncategorized": 0}.get(category, 0)
    score += {"HIGH": 3, "MEDIUM": 1, "LOW": 0}.get(criticality, 0)
    if port in SENSITIVE_PORTS:
        score += 2
    if hour < 6 or hour > 22:
        score += 1
    score += random.choice([-1, 0, 0, 0, 1])  # jitter

    if score >= 7:
        return "CRITICAL"
    elif score >= 5:
        return "HIGH"
    elif score >= 2:
        return "MEDIUM"
    return "LOW"


def generate_training_dataframe(n_samples: int = 4000) -> pd.DataFrame:
    rows = []
    base_time = datetime(2026, 1, 1)
    for _ in range(n_samples):
        category = random.choice(CATEGORY_LIST)
        protocol = random.choice(PROTOCOL_LIST)
        criticality = random.choice(CRITICALITY_LIST)
        source_port = random.choice(list(SENSITIVE_PORTS) + [random.randint(1024, 65000) for _ in range(5)])
        destination_port = random.choice(list(SENSITIVE_PORTS) + [random.randint(1024, 65000) for _ in range(5)])
        hour = random.randint(0, 23)
        timestamp = base_time + timedelta(hours=hour, minutes=random.randint(0, 59))
        source_ip_frequency = random.choice([1, 1, 2, 3, 5, 8, 12, 20])

        severity = _severity_for(category, criticality, destination_port, hour)

        rows.append({
            "category": category,
            "protocol": protocol,
            "asset_criticality": criticality,
            "source_port": source_port,
            "destination_port": destination_port,
            "timestamp": timestamp,
            "source_ip_frequency": source_ip_frequency,
            "severity": severity,
        })

    return pd.DataFrame(rows)
