from typing import List, Dict
from pydantic import BaseModel


class SummaryOut(BaseModel):
    total_alerts: int
    critical_alerts: int
    high_alerts: int
    anomalies: int
    active_incidents: int
    alert_fatigue_reduction_pct: float


class SeverityBucket(BaseModel):
    severity: str
    count: int


class CategoryBucket(BaseModel):
    category: str
    count: int


class TimelinePoint(BaseModel):
    date: str
    count: int


class FatigueOut(BaseModel):
    total_alerts: int
    duplicate_alerts: int
    unique_alerts: int
    clustered_groups: int
    final_incidents: int
    alert_reduction_pct: float
    estimated_workload_reduction_pct: float
    funnel: List[Dict]
