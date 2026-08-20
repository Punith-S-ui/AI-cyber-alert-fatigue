"""Real preprocessing pipeline for raw alert records (dict/DataFrame rows).

Handles: missing values, text normalization, timestamp normalization,
IP validation, severity normalization, invalid record removal, and logs
every problem it encounters so callers can report it back to the user.
"""
import ipaddress
import logging
import re
from datetime import datetime
from typing import List, Dict, Tuple

logger = logging.getLogger("preprocessing")

VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_CRITICALITY = {"LOW", "MEDIUM", "HIGH"}

REQUIRED_FIELDS = ["source_ip", "destination_ip", "alert_type", "message"]

TIMESTAMP_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%SZ",
    "%m/%d/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
]


def _is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(str(value).strip())
        return True
    except ValueError:
        return False


def _normalize_timestamp(value) -> Tuple[datetime, bool]:
    """Returns (timestamp, was_defaulted)."""
    if value is None or str(value).strip() == "" or str(value).lower() == "nan":
        return datetime.utcnow(), True
    if isinstance(value, datetime):
        return value, False
    text = str(value).strip()
    for fmt in TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(text, fmt), False
        except ValueError:
            continue
    try:
        # Fall back to fromisoformat which handles most ISO variants
        return datetime.fromisoformat(text.replace("Z", "")), False
    except Exception:
        return datetime.utcnow(), True


def _normalize_text(value: str) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _normalize_severity(value) -> str:
    if value is None or str(value).strip() == "":
        return "LOW"
    text = str(value).strip().upper()
    if text in VALID_SEVERITIES:
        return text
    # common numeric or alternate encodings
    mapping = {"1": "LOW", "2": "MEDIUM", "3": "HIGH", "4": "CRITICAL",
               "INFO": "LOW", "WARNING": "MEDIUM", "ERROR": "HIGH", "SEVERE": "CRITICAL"}
    return mapping.get(text, "LOW")


def _normalize_criticality(value) -> str:
    if value is None or str(value).strip() == "":
        return "MEDIUM"
    text = str(value).strip().upper()
    return text if text in VALID_CRITICALITY else "MEDIUM"


def preprocess_records(raw_records: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """Cleans a list of raw alert dicts.

    Returns (clean_records, error_log). Invalid records (missing required
    fields or unparseable IPs) are dropped and logged rather than raising,
    so a bad row in a large CSV doesn't kill the whole upload.
    """
    clean_records: List[Dict] = []
    errors: List[str] = []

    for idx, row in enumerate(raw_records):
        row_num = idx + 1
        missing = [f for f in REQUIRED_FIELDS if row.get(f) in (None, "", "nan")]
        if missing:
            msg = f"Row {row_num}: missing required field(s) {missing} — record skipped."
            errors.append(msg)
            logger.warning(msg)
            continue

        src_ip = str(row["source_ip"]).strip()
        dst_ip = str(row["destination_ip"]).strip()

        if not _is_valid_ip(src_ip) or not _is_valid_ip(dst_ip):
            msg = f"Row {row_num}: invalid IP address (src={src_ip}, dst={dst_ip}) — record skipped."
            errors.append(msg)
            logger.warning(msg)
            continue

        ts, defaulted = _normalize_timestamp(row.get("timestamp"))
        if defaulted:
            errors.append(f"Row {row_num}: timestamp missing/unparseable — defaulted to current time.")

        cleaned = {
            "timestamp": ts,
            "source_ip": src_ip,
            "destination_ip": dst_ip,
            "source_port": _safe_int(row.get("source_port")),
            "destination_port": _safe_int(row.get("destination_port")),
            "protocol": _normalize_text(row.get("protocol") or "TCP").upper(),
            "alert_type": _normalize_text(row.get("alert_type")),
            "category": _normalize_text(row.get("category") or _infer_category(row.get("alert_type"))),
            "message": _normalize_text(row.get("message")),
            "severity": _normalize_severity(row.get("severity")),
            "source": _normalize_text(row.get("source") or "UPLOAD"),
            "asset_criticality": _normalize_criticality(row.get("asset_criticality")),
        }
        clean_records.append(cleaned)

    return clean_records, errors


def _safe_int(value):
    try:
        if value is None or str(value).strip() == "" or str(value).lower() == "nan":
            return None
        return int(float(value))
    except (ValueError, TypeError):
        return None


CATEGORY_MAP = {
    "ssh brute force": "Authentication Threat",
    "brute force": "Authentication Threat",
    "suspicious login": "Authentication Threat",
    "privilege escalation": "Authentication Threat",
    "port scan": "Network Scanning",
    "ddos activity": "Network Scanning",
    "dns tunneling": "Network Scanning",
    "sql injection attempt": "Web Attack",
    "malware detection": "Malware Activity",
    "ransomware activity": "Malware Activity",
    "data exfiltration": "Data Exfiltration",
}


def _infer_category(alert_type: str) -> str:
    if not alert_type:
        return "Uncategorized"
    return CATEGORY_MAP.get(str(alert_type).strip().lower(), "Uncategorized")
