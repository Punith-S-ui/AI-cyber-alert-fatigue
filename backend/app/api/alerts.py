from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.alert import Alert
from app.models.user import User
from app.schemas.alert import AlertCreate, AlertOut, AlertListResponse, UploadResult
from app.core.dependencies import get_current_user
from app.services.alert_service import parse_upload_file, ingest_records

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

ALLOWED_EXTENSIONS = (".csv", ".json")


@router.post("", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
def create_alert(payload: AlertCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _, clean, errors = ingest_records(db, [payload.model_dump()], created_by=user.id)
    if clean == 0:
        raise HTTPException(status_code=422, detail=f"Alert could not be validated: {errors}")
    alert = db.query(Alert).order_by(Alert.id.desc()).first()
    return alert


@router.post("/upload", response_model=UploadResult)
async def upload_alerts(file: UploadFile = File(...), db: Session = Depends(get_db),
                         user: User = Depends(get_current_user)):
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Unsupported file type. Only .csv and .json are allowed.")

    content = await file.read()
    try:
        raw_records = parse_upload_file(file.filename, content)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse file: {exc}")

    if not raw_records:
        raise HTTPException(status_code=400, detail="The uploaded file contained no records.")

    total, clean, errors = ingest_records(db, raw_records, created_by=user.id)
    return UploadResult(
        filename=file.filename,
        rows_received=total,
        rows_valid=clean,
        rows_rejected=total - clean,
        errors=errors[:50],
    )


@router.get("", response_model=AlertListResponse)
def list_alerts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    severity: Optional[str] = None,
    category: Optional[str] = None,
    anomaly_status: Optional[str] = None,
    priority_level: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
):
    q = db.query(Alert)
    if severity:
        q = q.filter(Alert.severity == severity.upper())
    if category:
        q = q.filter(Alert.category == category)
    if anomaly_status:
        q = q.filter(Alert.anomaly_status == anomaly_status.upper())
    if priority_level:
        q = q.filter(Alert.priority_level == priority_level.upper())
    if search:
        like = f"%{search}%"
        q = q.filter(Alert.message.ilike(like) | Alert.source_ip.ilike(like) | Alert.destination_ip.ilike(like))

    total = q.count()
    items = q.order_by(Alert.timestamp.desc()).offset(offset).limit(limit).all()
    return AlertListResponse(total=total, items=items)


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(alert_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
    return None
