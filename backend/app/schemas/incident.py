from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class IncidentOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    alert_count: int
    priority: str
    risk_score: float
    first_seen: Optional[datetime]
    last_seen: Optional[datetime]
    status: str

    class Config:
        from_attributes = True


class IncidentStatusUpdate(BaseModel):
    status: str
