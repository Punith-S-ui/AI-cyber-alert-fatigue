"""Real TF-IDF + KMeans alert clustering."""
import math
from typing import List, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

LABEL_KEYWORDS = {
    "Brute Force Activity": {"brute", "force", "ssh", "login", "password", "credential"},
    "Network Scanning": {"scan", "port", "probe", "reconnaissance", "sweep"},
    "Malware Activity": {"malware", "virus", "trojan", "ransomware", "payload"},
    "Authentication Threat": {"authentication", "auth", "privilege", "escalation", "suspicious"},
    "Web Attack": {"sql", "injection", "xss", "web", "http", "request"},
    "Data Exfiltration": {"exfiltration", "exfil", "upload", "transfer", "leak", "dns", "tunnel"},
    "Denial of Service": {"ddos", "dos", "flood", "volumetric"},
}


def _label_cluster(top_terms: List[str]) -> str:
    term_set = set(t.lower() for t in top_terms)
    best_label, best_overlap = "General Security Activity", 0
    for label, keywords in LABEL_KEYWORDS.items():
        overlap = len(term_set & keywords)
        if overlap > best_overlap:
            best_overlap = overlap
            best_label = label
    return best_label


def cluster_alerts(alerts: List[Dict], n_clusters: int = None) -> Dict:
    """alerts: list of dicts with 'id' and 'message'.

    Returns {'assignments': {alert_id: cluster_index}, 'clusters': {idx: {'label', 'top_terms', 'count'}}}
    """
    messages = [a["message"] or a.get("alert_type", "") for a in alerts]
    ids = [a["id"] for a in alerts]

    if len(alerts) < 2:
        if alerts:
            return {
                "assignments": {ids[0]: 0},
                "clusters": {0: {"label": "General Security Activity", "top_terms": [], "count": 1}},
            }
        return {"assignments": {}, "clusters": {}}

    if n_clusters is None:
        # Heuristic: roughly sqrt(n/2), bounded between 2 and 10
        n_clusters = max(2, min(10, round(math.sqrt(len(alerts) / 2))))
    n_clusters = min(n_clusters, len(alerts))

    vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
    tfidf_matrix = vectorizer.fit_transform(messages)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(tfidf_matrix)

    feature_names = vectorizer.get_feature_names_out()
    clusters_info = {}
    for cluster_idx in range(n_clusters):
        center = kmeans.cluster_centers_[cluster_idx]
        top_indices = center.argsort()[::-1][:6]
        top_terms = [feature_names[i] for i in top_indices if center[i] > 0]
        count = int((labels == cluster_idx).sum())
        clusters_info[cluster_idx] = {
            "label": _label_cluster(top_terms),
            "top_terms": top_terms,
            "count": count,
        }

    assignments = {ids[i]: int(labels[i]) for i in range(len(ids))}
    return {"assignments": assignments, "clusters": clusters_info}
