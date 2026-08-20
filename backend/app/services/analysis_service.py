"""Orchestrates the full AI/ML processing pipeline over unprocessed alerts."""
from collections import Counter
from datetime import datetime
from typing import Dict

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.cluster import AlertCluster
from app.models.analysis import AnalysisRun
from app.ml.deduplication import detect_duplicates
from app.ml.clustering import cluster_alerts
from app.ml.anomaly_detection import detect_anomalies
from app.ml.severity_model import severity_model_service, build_feature_row
from app.ml.priority import compute_priority
from app.ml.explanations import generate_explanation
from app.services.incident_service import correlate_incidents


def _alert_to_dict(a: Alert) -> Dict:
    return {
        "id": a.id,
        "timestamp": a.timestamp,
        "source_ip": a.source_ip,
        "destination_ip": a.destination_ip,
        "source_port": a.source_port,
        "destination_port": a.destination_port,
        "protocol": a.protocol,
        "alert_type": a.alert_type,
        "category": a.category,
        "message": a.message,
        "severity": a.severity.value if hasattr(a.severity, "value") else a.severity,
        "asset_criticality": a.asset_criticality,
    }


def run_full_analysis(db: Session) -> AnalysisRun:
    run = AnalysisRun(started_at=datetime.utcnow(), status="RUNNING")
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        alerts = db.query(Alert).all()
        if not alerts:
            run.status = "SUCCESS"
            run.finished_at = datetime.utcnow()
            run.log = "No alerts found to process."
            db.commit()
            return run

        alert_dicts = [_alert_to_dict(a) for a in alerts]
        alert_lookup = {a.id: a for a in alerts}

        # 1. Deduplication
        dedup_result = detect_duplicates(alert_dicts)
        for a in alerts:
            a.is_duplicate = 1 if a.id in dedup_result["duplicate_ids"] else 0
            a.duplicate_of_id = dedup_result["duplicate_of"].get(a.id)

        # 2. Clustering (TF-IDF + KMeans) over non-duplicate alerts
        non_dupe_dicts = [d for d in alert_dicts if d["id"] not in dedup_result["duplicate_ids"]]
        cluster_result = cluster_alerts(non_dupe_dicts)

        # clear old cluster rows, recreate fresh ones for this run
        db.query(AlertCluster).delete()
        db.flush()
        cluster_id_map = {}
        for idx, info in cluster_result["clusters"].items():
            cluster_row = AlertCluster(
                label=info["label"],
                top_terms=", ".join(info["top_terms"]),
                alert_count=info["count"],
            )
            db.add(cluster_row)
            db.flush()
            cluster_id_map[idx] = cluster_row.id

        for alert_id, cluster_idx in cluster_result["assignments"].items():
            alert_lookup[alert_id].cluster_id = cluster_id_map[cluster_idx]

        # 3. Anomaly detection (Isolation Forest) over full alert set
        anomaly_result = detect_anomalies(alert_dicts)
        for alert_id, res in anomaly_result.items():
            alert_lookup[alert_id].anomaly_status = res["status"]
            alert_lookup[alert_id].anomaly_score = res["score"]

        # source IP frequency for priority/severity features
        src_freq = Counter(d["source_ip"] for d in alert_dicts)

        # 4. Severity prediction (Random Forest) - train if needed
        if not severity_model_service.is_trained():
            from app.ml.training_data import generate_training_dataframe
            severity_model_service.train(generate_training_dataframe())

        for d in alert_dicts:
            alert = alert_lookup[d["id"]]
            freq = src_freq[d["source_ip"]]
            try:
                pred = severity_model_service.predict(d, source_ip_frequency=freq)
                predicted_severity = pred["predicted_severity"]
            except RuntimeError:
                predicted_severity = d["severity"]
            alert.predicted_severity = predicted_severity

            # 5. Priority score
            anomaly_status = alert.anomaly_status.value if hasattr(alert.anomaly_status, "value") else alert.anomaly_status
            priority = compute_priority(
                predicted_severity=predicted_severity,
                anomaly_status=anomaly_status,
                asset_criticality=d["asset_criticality"],
                category=d["category"],
                source_ip_frequency=freq,
            )
            alert.priority_score = priority["priority_score"]
            alert.priority_level = priority["priority_level"]

            # 6. AI explanation
            explain_dict = dict(d)
            explain_dict["predicted_severity"] = predicted_severity
            explain_dict["priority_level"] = priority["priority_level"]
            alert.ai_explanation = generate_explanation(explain_dict, priority["breakdown"], freq)

            alert.status = "PROCESSED"

        db.commit()

        # 7. Incident correlation
        incidents_created = correlate_incidents(db, list(alert_lookup.values()))

        total = len(alerts)
        duplicates = dedup_result["duplicates"]
        final_actionable = incidents_created + len([
            a for a in alert_lookup.values()
            if not a.is_duplicate and a.incident_id is None
        ])
        reduction_pct = round(((total - final_actionable) / total) * 100, 2) if total else 0.0

        run.status = "SUCCESS"
        run.finished_at = datetime.utcnow()
        run.total_alerts = total
        run.duplicate_alerts = duplicates
        run.unique_alerts = dedup_result["unique"]
        run.clusters_created = len(cluster_result["clusters"])
        run.anomalies_found = sum(1 for r in anomaly_result.values() if r["status"] == "ANOMALY")
        run.incidents_created = incidents_created
        run.alert_reduction_pct = reduction_pct
        run.log = "Pipeline completed successfully: preprocessing -> deduplication -> clustering -> anomaly detection -> severity prediction -> priority scoring -> correlation."
        db.commit()
        return run

    except Exception as exc:
        db.rollback()
        run.status = "FAILED"
        run.finished_at = datetime.utcnow()
        run.log = f"Pipeline failed: {exc}"
        db.add(run)
        db.commit()
        raise
