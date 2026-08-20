from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Text

from app.database.database import Base


class AnalysisRun(Base):
    """Records each time the AI/ML processing pipeline is executed."""
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(32), default="RUNNING")  # RUNNING / SUCCESS / FAILED

    total_alerts = Column(Integer, default=0)
    duplicate_alerts = Column(Integer, default=0)
    unique_alerts = Column(Integer, default=0)
    clusters_created = Column(Integer, default=0)
    anomalies_found = Column(Integer, default=0)
    incidents_created = Column(Integer, default=0)
    alert_reduction_pct = Column(Float, default=0.0)

    log = Column(Text, nullable=True)
