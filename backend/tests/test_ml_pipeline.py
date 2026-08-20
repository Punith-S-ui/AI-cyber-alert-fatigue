from datetime import datetime, timedelta

from app.ml.preprocessing import preprocess_records
from app.ml.deduplication import detect_duplicates
from app.ml.clustering import cluster_alerts
from app.ml.anomaly_detection import detect_anomalies
from app.ml.priority import compute_priority
from app.ml.explanations import generate_explanation
from app.ml.severity_model import SeverityModelService
from app.ml.training_data import generate_training_dataframe


def test_preprocessing_drops_invalid_rows():
    raw = [
        {"source_ip": "10.0.0.1", "destination_ip": "10.0.0.2", "alert_type": "Port Scan",
         "message": "scan", "timestamp": "2026-01-01 10:00:00"},
        {"source_ip": "bad-ip", "destination_ip": "10.0.0.2", "alert_type": "Port Scan", "message": "scan"},
        {"source_ip": "10.0.0.1", "destination_ip": "10.0.0.2", "alert_type": "", "message": "scan"},
    ]
    clean, errors = preprocess_records(raw)
    # only the first row (valid IPs, all required fields, parseable timestamp) survives
    assert len(clean) == 1
    # one error for the bad IP row, one for the missing-alert_type row
    assert len(errors) == 2
    assert any("invalid IP" in e for e in errors)
    assert any("missing required field" in e for e in errors)


def test_severity_normalization():
    raw = [{"source_ip": "10.0.0.1", "destination_ip": "10.0.0.2", "alert_type": "Port Scan",
            "message": "scan", "severity": "warning"}]
    clean, _ = preprocess_records(raw)
    assert clean[0]["severity"] == "MEDIUM"


def test_deduplication_flags_near_identical_alerts():
    now = datetime.utcnow()
    alerts = [
        {"id": 1, "timestamp": now, "source_ip": "1.1.1.1", "destination_ip": "2.2.2.2",
         "alert_type": "Port Scan", "message": "TCP port scan detected from 1.1.1.1"},
        {"id": 2, "timestamp": now + timedelta(minutes=1), "source_ip": "1.1.1.1", "destination_ip": "2.2.2.2",
         "alert_type": "Port Scan", "message": "TCP port scan detected from 1.1.1.1"},
        {"id": 3, "timestamp": now + timedelta(hours=5), "source_ip": "9.9.9.9", "destination_ip": "8.8.8.8",
         "alert_type": "Malware Detection", "message": "Totally unrelated malware alert"},
    ]
    result = detect_duplicates(alerts)
    assert result["total"] == 3
    assert 2 in result["duplicate_ids"]
    assert 1 not in result["duplicate_ids"]
    assert result["duplicates"] >= 1


def test_clustering_assigns_all_alerts():
    now = datetime.utcnow()
    alerts = [{"id": i, "message": f"SSH brute force login attempt {i%3}"} for i in range(10)]
    result = cluster_alerts(alerts)
    assert len(result["assignments"]) == 10
    assert len(result["clusters"]) >= 1


def test_anomaly_detection_returns_status_for_each_alert():
    now = datetime.utcnow()
    alerts = []
    for i in range(20):
        alerts.append({
            "id": i, "timestamp": now + timedelta(minutes=i), "source_ip": f"1.1.1.{i % 4}",
            "severity": "LOW", "category": "Network Scanning",
        })
    result = detect_anomalies(alerts)
    assert len(result) == 20
    for r in result.values():
        assert r["status"] in {"NORMAL", "ANOMALY"}


def test_priority_score_bounds():
    result = compute_priority("CRITICAL", "ANOMALY", "HIGH", "Data Exfiltration", 20)
    assert 0 <= result["priority_score"] <= 100
    assert result["priority_level"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def test_explanation_uses_alert_features():
    alert = {"predicted_severity": "HIGH", "priority_level": "HIGH", "category": "Malware Activity", "source_ip": "1.1.1.1"}
    breakdown = {"severity_points": 40, "anomaly_points": 10, "asset_criticality_points": 15, "category_risk_points": 10}
    text = generate_explanation(alert, breakdown, source_ip_frequency=8)
    assert "HIGH" in text
    assert len(text) > 20


def test_random_forest_trains_and_predicts(tmp_path, monkeypatch):
    monkeypatch.setattr("app.ml.severity_model.MODEL_PATH", str(tmp_path / "model.joblib"))
    service = SeverityModelService()
    df = generate_training_dataframe(n_samples=500)
    result = service.train(df)
    assert 0 <= result["accuracy"] <= 1
    assert service.is_trained()

    prediction = service.predict({
        "category": "Data Exfiltration", "protocol": "HTTPS", "asset_criticality": "HIGH",
        "source_port": 443, "destination_port": 22, "timestamp": df.iloc[0]["timestamp"],
    }, source_ip_frequency=5)
    assert prediction["predicted_severity"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
