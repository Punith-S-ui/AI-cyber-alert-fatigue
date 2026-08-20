from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.incident import Incident
from app.models.user import User
from app.schemas.incident import IncidentOut, IncidentStatusUpdate
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

VALID_STATUSES = {"OPEN", "INVESTIGATING", "RESOLVED"}


@router.get("", response_model=list[IncidentOut])
def list_incidents(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Incident).order_by(Incident.risk_score.desc()).all()


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.put("/{incident_id}/status", response_model=IncidentOut)
def update_status(incident_id: int, payload: IncidentStatusUpdate, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    new_status = payload.status.upper()
    if new_status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail=f"status must be one of {VALID_STATUSES}")
    incident.status = new_status
    db.commit()
    db.refresh(incident)
    return incident
