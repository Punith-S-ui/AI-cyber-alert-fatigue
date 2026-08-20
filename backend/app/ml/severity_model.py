"""Random Forest severity classifier.

Trains on a labeled cybersecurity dataset, persists to disk with joblib,
and loads from disk for prediction rather than retraining on every request.
"""
import os
from typing import List, Dict

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

from app.core.config import settings

MODEL_PATH = os.path.join(settings.ML_MODELS_DIR, "severity_rf_model.joblib")
ENCODERS_PATH = os.path.join(settings.ML_MODELS_DIR, "severity_encoders.joblib")

CATEGORY_LIST = [
    "Authentication Threat", "Network Scanning", "Malware Activity",
    "Web Attack", "Data Exfiltration", "Denial of Service", "Uncategorized",
]
PROTOCOL_LIST = ["TCP", "UDP", "ICMP", "HTTP", "HTTPS", "DNS"]
CRITICALITY_LIST = ["LOW", "MEDIUM", "HIGH"]
SEVERITY_CLASSES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

FEATURE_COLUMNS = [
    "category_enc", "protocol_enc", "asset_criticality_enc",
    "source_port", "destination_port", "hour_of_day", "source_ip_frequency",
]


def _encode(value, choices):
    return choices.index(value) if value in choices else len(choices)


def build_feature_row(record: Dict, source_ip_frequency: int = 1) -> List[float]:
    ts = record.get("timestamp")
    hour = ts.hour if hasattr(ts, "hour") else 0
    return [
        _encode(record.get("category"), CATEGORY_LIST),
        _encode(record.get("protocol"), PROTOCOL_LIST),
        _encode(record.get("asset_criticality"), CRITICALITY_LIST),
        record.get("source_port") or 0,
        record.get("destination_port") or 0,
        hour,
        source_ip_frequency,
    ]


class SeverityModelService:
    def __init__(self):
        self.model: RandomForestClassifier | None = None
        self._load()

    def _load(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)

    def is_trained(self) -> bool:
        return self.model is not None

    def train(self, training_df: pd.DataFrame) -> Dict:
        """training_df must have columns: category, protocol, asset_criticality,
        source_port, destination_port, timestamp, source_ip_frequency, severity
        """
        rows = []
        for _, r in training_df.iterrows():
            rows.append(build_feature_row(r.to_dict(), r.get("source_ip_frequency", 1)))
        X = np.array(rows)
        y = training_df["severity"].astype(str).values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        clf = RandomForestClassifier(
            n_estimators=300, max_depth=12, random_state=42, class_weight="balanced"
        )
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, zero_division=0)

        joblib.dump(clf, MODEL_PATH)
        self.model = clf

        return {"accuracy": round(float(acc), 4), "report": report, "n_train": len(X_train), "n_test": len(X_test)}

    def predict(self, record: Dict, source_ip_frequency: int = 1) -> Dict:
        if self.model is None:
            raise RuntimeError("Severity model has not been trained yet. Call /api/ml/train first.")
        row = np.array([build_feature_row(record, source_ip_frequency)])
        pred = self.model.predict(row)[0]
        proba = self.model.predict_proba(row)[0]
        classes = list(self.model.classes_)
        confidence = float(max(proba))
        return {"predicted_severity": pred, "confidence": round(confidence, 4)}


severity_model_service = SeverityModelService()
