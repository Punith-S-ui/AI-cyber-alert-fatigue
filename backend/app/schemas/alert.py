from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import ipaddress


class AlertCreate(BaseModel):
    timestamp: Optional[datetime] = None
    source_ip: str
    destination_ip: str
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: Optional[str] = "TCP"
    alert_type: str
    category: Optional[str] = None
    message: str
    severity: Optional[str] = "LOW"
    source: Optional[str] = "MANUAL"
    asset_criticality: Optional[str] = "MEDIUM"

    @field_validator("source_ip", "destination_ip")
    @classmethod
    def validate_ip(cls, v):
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError(f"Invalid IP address: {v}")
        return v

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v):
        if v is None:
            return "LOW"
        v = v.upper().strip()
        if v not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
            raise ValueError("severity must be one of LOW, MEDIUM, HIGH, CRITICAL")
        return v


class AlertOut(BaseModel):
    id: int
    timestamp: datetime
    source_ip: str
    destination_ip: str
    source_port: Optional[int]
    destination_port: Optional[int]
    protocol: Optional[str]
    alert_type: str
    category: Optional[str]
    message: str
    severity: str
    source: Optional[str]
    asset_criticality: Optional[str]
    status: str
    anomaly_status: Optional[str]
    anomaly_score: Optional[float]
    predicted_severity: Optional[str]
    priority_score: Optional[float]
    priority_level: Optional[str]
    is_duplicate: Optional[int]
    cluster_id: Optional[int]
    incident_id: Optional[int]
    ai_explanation: Optional[str]

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    total: int
    items: list[AlertOut]


class UploadResult(BaseModel):
    filename: str
    rows_received: int
    rows_valid: int
    rows_rejected: int
    errors: list[str] = []
