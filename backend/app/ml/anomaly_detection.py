"""Real Isolation Forest anomaly detection over engineered alert features."""
from collections import Counter
from typing import List, Dict

import numpy as np
from sklearn.ensemble import IsolationForest

SEVERITY_WEIGHT = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
CRITICALITY_WEIGHT = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}


def _build_features(alerts: List[Dict]) -> np.ndarray:
    src_counter = Counter(a["source_ip"] for a in alerts)
    category_counter = Counter(a["category"] for a in alerts)

    # sort by time to compute inter-arrival gaps per source IP
    by_source: Dict[str, List[Dict]] = {}
    for a in alerts:
        by_source.setdefault(a["source_ip"], []).append(a)
    for ip, group in by_source.items():
        group.sort(key=lambda x: x["timestamp"])

    gap_lookup = {}
    for ip, group in by_source.items():
        for i, a in enumerate(group):
            if i == 0:
                gap_lookup[a["id"]] = 9999.0
            else:
                gap = (a["timestamp"] - group[i - 1]["timestamp"]).total_seconds()
                gap_lookup[a["id"]] = gap

    rows = []
    for a in alerts:
        severity_val = SEVERITY_WEIGHT.get(a["severity"], 1)
        source_freq = src_counter[a["source_ip"]]
        category_rarity = 1.0 / category_counter[a["category"]]
        hour_of_day = a["timestamp"].hour
        inter_arrival = min(gap_lookup.get(a["id"], 9999.0), 9999.0)
        rows.append([severity_val, source_freq, category_rarity, hour_of_day, inter_arrival])

    return np.array(rows, dtype=float)


def detect_anomalies(alerts: List[Dict], contamination: float = 0.08) -> Dict[int, Dict]:
    """Returns {alert_id: {'status': 'NORMAL'|'ANOMALY', 'score': float}}"""
    if len(alerts) < 5:
        return {a["id"]: {"status": "NORMAL", "score": 0.0} for a in alerts}

    X = _build_features(alerts)

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
    )
    model.fit(X)
    raw_scores = model.decision_function(X)  # higher = more normal
    predictions = model.predict(X)  # -1 = anomaly, 1 = normal

    # normalize score to 0-1 "anomaly score" (1 = most anomalous)
    min_s, max_s = raw_scores.min(), raw_scores.max()
    span = (max_s - min_s) or 1e-9

    results = {}
    for i, a in enumerate(alerts):
        normalized = 1 - ((raw_scores[i] - min_s) / span)  # invert: low decision_function -> high anomaly
        results[a["id"]] = {
            "status": "ANOMALY" if predictions[i] == -1 else "NORMAL",
            "score": round(float(normalized), 4),
        }
    return results
