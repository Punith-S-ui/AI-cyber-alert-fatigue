import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class SeverityLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, enum.Enum):
    NEW = "NEW"
    PROCESSED = "PROCESSED"
    IGNORED = "IGNORED"


class AnomalyStatus(str, enum.Enum):
    NORMAL = "NORMAL"
    ANOMALY = "ANOMALY"
    UNSCORED = "UNSCORED"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    source_ip = Column(String(64), index=True)
    destination_ip = Column(String(64), index=True)
    source_port = Column(Integer, nullable=True)
    destination_port = Column(Integer, nullable=True)
    protocol = Column(String(16), nullable=True)

    alert_type = Column(String(128), index=True)
    category = Column(String(64), index=True)
    message = Column(Text)

    severity = Column(Enum(SeverityLevel), default=SeverityLevel.LOW)
    source = Column(String(64), default="DEMO DATA")
    asset_criticality = Column(String(16), default="MEDIUM")  # LOW/MEDIUM/HIGH

    status = Column(Enum(AlertStatus), default=AlertStatus.NEW)

    # ML-derived fields
    anomaly_status = Column(Enum(AnomalyStatus), default=AnomalyStatus.UNSCORED)
    anomaly_score = Column(Float, nullable=True)
    predicted_severity = Column(Enum(SeverityLevel), nullable=True)
    priority_score = Column(Float, nullable=True)
    priority_level = Column(String(16), nullable=True)

    is_duplicate = Column(Integer, default=0)  # 0/1 flag
    duplicate_of_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)

    cluster_id = Column(Integer, ForeignKey("alert_clusters.id"), nullable=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)

    ai_explanation = Column(Text, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    created_by_user = relationship("User", back_populates="alerts")
    cluster = relationship("AlertCluster", back_populates="alerts")
    incident = relationship("Incident", back_populates="alerts")
