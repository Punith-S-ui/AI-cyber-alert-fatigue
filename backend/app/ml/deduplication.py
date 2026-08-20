"""Real duplicate-alert detection.

Two alerts are considered duplicates when they share the same alert_type,
source_ip and destination_ip, occur inside the same time window, AND have
a high text similarity between their messages (TF-IDF cosine similarity).
No result here is hardcoded - it is computed from the actual alert set.
"""
from datetime import timedelta
from typing import List, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

TIME_WINDOW_MINUTES = 10
SIMILARITY_THRESHOLD = 0.75


def detect_duplicates(alerts: List[Dict]) -> Dict:
    """alerts: list of dicts with keys id, timestamp, source_ip, destination_ip,
    alert_type, message (already sorted or not - we sort internally).

    Returns a dict: {
        'duplicate_ids': set of alert ids flagged as duplicates,
        'duplicate_of': {dup_id: original_id},
        'total': int, 'duplicates': int, 'unique': int, 'duplicate_pct': float
    }
    """
    if not alerts:
        return {"duplicate_ids": set(), "duplicate_of": {}, "total": 0,
                "duplicates": 0, "unique": 0, "duplicate_pct": 0.0}

    sorted_alerts = sorted(alerts, key=lambda a: a["timestamp"])

    # Group candidates by (alert_type, source_ip, destination_ip)
    groups: Dict[tuple, List[Dict]] = {}
    for a in sorted_alerts:
        key = (a["alert_type"], a["source_ip"], a["destination_ip"])
        groups.setdefault(key, []).append(a)

    duplicate_ids = set()
    duplicate_of = {}

    for key, group in groups.items():
        if len(group) < 2:
            continue

        messages = [g["message"] or "" for g in group]
        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf = vectorizer.fit_transform(messages)
            sim_matrix = cosine_similarity(tfidf)
        except ValueError:
            # e.g. all-empty messages; fall back to exact-match similarity
            sim_matrix = [[1.0 if messages[i] == messages[j] else 0.0
                           for j in range(len(messages))] for i in range(len(messages))]

        for i in range(len(group)):
            if group[i]["id"] in duplicate_ids:
                continue
            for j in range(i + 1, len(group)):
                if group[j]["id"] in duplicate_ids:
                    continue
                time_gap = abs((group[j]["timestamp"] - group[i]["timestamp"]).total_seconds())
                if time_gap > TIME_WINDOW_MINUTES * 60:
                    continue
                if sim_matrix[i][j] >= SIMILARITY_THRESHOLD:
                    duplicate_ids.add(group[j]["id"])
                    duplicate_of[group[j]["id"]] = group[i]["id"]

    total = len(alerts)
    duplicates = len(duplicate_ids)
    unique = total - duplicates
    duplicate_pct = round((duplicates / total) * 100, 2) if total else 0.0

    return {
        "duplicate_ids": duplicate_ids,
        "duplicate_of": duplicate_of,
        "total": total,
        "duplicates": duplicates,
        "unique": unique,
        "duplicate_pct": duplicate_pct,
    }
