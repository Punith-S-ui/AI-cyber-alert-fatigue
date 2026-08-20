from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.alert import Alert
from app.models.incident import Incident
from app.models.analysis import AnalysisRun
from app.models.user import User
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    total = db.query(Alert).count()
    critical = db.query(Alert).filter(Alert.priority_level == "CRITICAL").count()
    high = db.query(Alert).filter(Alert.priority_level == "HIGH").count()
    anomalies = db.query(Alert).filter(Alert.anomaly_status == "ANOMALY").count()
    active_incidents = db.query(Incident).filter(Incident.status != "RESOLVED").count()

    last_run = db.query(AnalysisRun).filter(AnalysisRun.status == "SUCCESS").order_by(AnalysisRun.id.desc()).first()
    reduction = last_run.alert_reduction_pct if last_run else 0.0

    return {
        "total_alerts": total,
        "critical_alerts": critical,
        "high_alerts": high,
        "anomalies": anomalies,
        "active_incidents": active_incidents,
        "alert_fatigue_reduction_pct": reduction,
    }


@router.get("/severity")
def severity_distribution(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Alert.severity).all()
    counts = Counter(r[0].value if hasattr(r[0], "value") else r[0] for r in rows)
    return [{"severity": k, "count": v} for k, v in counts.items()]


@router.get("/categories")
def category_distribution(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Alert.category).all()
    counts = Counter(r[0] or "Uncategorized" for r in rows)
    return [{"category": k, "count": v} for k, v in counts.most_common(15)]


@router.get("/timeline")
def timeline(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Alert.timestamp).all()
    counts = Counter(r[0].strftime("%Y-%m-%d") for r in rows if r[0])
    ordered = sorted(counts.items())
    return [{"date": d, "count": c} for d, c in ordered]


@router.get("/fatigue")
def fatigue(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    last_run = db.query(AnalysisRun).filter(AnalysisRun.status == "SUCCESS").order_by(AnalysisRun.id.desc()).first()
    if not last_run:
        return {
            "total_alerts": db.query(Alert).count(),
            "duplicate_alerts": 0, "unique_alerts": db.query(Alert).count(),
            "clustered_groups": 0, "final_incidents": 0,
            "alert_reduction_pct": 0.0, "estimated_workload_reduction_pct": 0.0,
            "funnel": [],
        }

    final_actionable = last_run.incidents_created + (
        last_run.unique_alerts - db.query(Alert).filter(Alert.incident_id.isnot(None)).count()
    )
    final_actionable = max(final_actionable, 0)

    funnel = [
        {"stage": "Total Alerts Ingested", "count": last_run.total_alerts},
        {"stage": "After Deduplication", "count": last_run.unique_alerts},
        {"stage": "After Clustering", "count": last_run.clusters_created},
        {"stage": "Final Actionable Incidents", "count": last_run.incidents_created},
    ]

    return {
        "total_alerts": last_run.total_alerts,
        "duplicate_alerts": last_run.duplicate_alerts,
        "unique_alerts": last_run.unique_alerts,
        "clustered_groups": last_run.clusters_created,
        "final_incidents": last_run.incidents_created,
        "alert_reduction_pct": last_run.alert_reduction_pct,
        "estimated_workload_reduction_pct": last_run.alert_reduction_pct,
        "funnel": funnel,
    }


@router.get("/top-sources")
def top_sources(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Alert.source_ip).all()
    counts = Counter(r[0] for r in rows)
    return [{"source_ip": k, "count": v} for k, v in counts.most_common(10)]


@router.get("/anomaly-distribution")
def anomaly_distribution(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Alert.anomaly_status).all()
    counts = Counter(r[0].value if hasattr(r[0], "value") else r[0] for r in rows)
    return [{"status": k, "count": v} for k, v in counts.items()]
