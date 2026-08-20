"""CRUD + ingestion helpers for alerts."""
import csv
import io
import json
from datetime import datetime
from typing import List, Dict, Tuple

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.ml.preprocessing import preprocess_records


def parse_upload_file(filename: str, content: bytes) -> List[Dict]:
    if filename.lower().endswith(".csv"):
        text = content.decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        return [dict(row) for row in reader]
    elif filename.lower().endswith(".json"):
        text = content.decode("utf-8", errors="replace")
        data = json.loads(text)
        if isinstance(data, dict):
            data = data.get("alerts", [data])
        return data
    else:
        raise ValueError("Unsupported file type. Only .csv and .json are allowed.")


def ingest_records(db: Session, raw_records: List[Dict], created_by: int = None) -> Tuple[int, int, List[str]]:
    clean_records, errors = preprocess_records(raw_records)

    for rec in clean_records:
        alert = Alert(
            timestamp=rec["timestamp"],
            source_ip=rec["source_ip"],
            destination_ip=rec["destination_ip"],
            source_port=rec["source_port"],
            destination_port=rec["destination_port"],
            protocol=rec["protocol"],
            alert_type=rec["alert_type"],
            category=rec["category"],
            message=rec["message"],
            severity=rec["severity"],
            source=rec["source"],
            asset_criticality=rec["asset_criticality"],
            status="NEW",
            created_by=created_by,
            created_at=datetime.utcnow(),
        )
        db.add(alert)

    db.commit()
    return len(raw_records), len(clean_records), errors
