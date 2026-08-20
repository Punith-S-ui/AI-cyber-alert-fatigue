import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class IncidentStatus(str, enum.Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    alert_count = Column(Integer, default=0)
    priority = Column(String(16), default="LOW")
    risk_score = Column(Float, default=0.0)
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.OPEN)
    created_at = Column(DateTime, default=datetime.utcnow)

    alerts = relationship("Alert", back_populates="incident")
