from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database.database import Base


class AlertCluster(Base):
    __tablename__ = "alert_clusters"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(128))
    top_terms = Column(String(255), nullable=True)
    alert_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    alerts = relationship("Alert", back_populates="cluster")
