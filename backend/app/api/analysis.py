from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.analysis import AnalysisRun
from app.core.dependencies import get_current_user
from app.services.analysis_service import run_full_analysis

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/process")
def process(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    run = run_full_analysis(db)
    return {
        "run_id": run.id,
        "status": run.status,
        "total_alerts": run.total_alerts,
        "duplicate_alerts": run.duplicate_alerts,
        "unique_alerts": run.unique_alerts,
        "clusters_created": run.clusters_created,
        "anomalies_found": run.anomalies_found,
        "incidents_created": run.incidents_created,
        "alert_reduction_pct": run.alert_reduction_pct,
        "log": run.log,
    }


@router.get("/status")
def status_endpoint(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    run = db.query(AnalysisRun).order_by(AnalysisRun.id.desc()).first()
    if not run:
        return {"status": "NEVER_RUN"}
    return {
        "run_id": run.id,
        "status": run.status,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
        "total_alerts": run.total_alerts,
        "duplicate_alerts": run.duplicate_alerts,
        "anomalies_found": run.anomalies_found,
        "incidents_created": run.incidents_created,
        "alert_reduction_pct": run.alert_reduction_pct,
    }
