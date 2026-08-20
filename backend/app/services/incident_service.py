"""Correlates related alerts into incidents."""
from collections import defaultdict
from datetime import timedelta
from typing import List, Dict

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.incident import Incident

CORRELATION_WINDOW_MINUTES = 30


def correlate_incidents(db: Session, alerts: List[Alert]) -> int:
    """Groups non-duplicate alerts sharing source_ip + destination_ip + category
    + cluster_id within a time window into Incident records. Returns count created.
    """
    candidates = [a for a in alerts if not a.is_duplicate]
    candidates.sort(key=lambda a: a.timestamp)

    groups: Dict[tuple, List[Alert]] = defaultdict(list)
    for a in candidates:
        key = (a.source_ip, a.destination_ip, a.category, a.cluster_id)
        groups[key].append(a)

    created = 0
    for key, group in groups.items():
        if len(group) < 2:
            continue

        # split into time-windowed sub-groups
        sub_groups: List[List[Alert]] = []
        current: List[Alert] = []
        for a in group:
            if not current:
                current = [a]
                continue
            if (a.timestamp - current[-1].timestamp) <= timedelta(minutes=CORRELATION_WINDOW_MINUTES):
                current.append(a)
            else:
                sub_groups.append(current)
                current = [a]
        if current:
            sub_groups.append(current)

        for sg in sub_groups:
            if len(sg) < 2:
                continue
            source_ip, dest_ip, category, cluster_id = key
            priorities = [a.priority_score or 0 for a in sg]
            risk_score = round(sum(priorities) / len(priorities), 2) if priorities else 0
            max_priority_level = max(
                (a.priority_level or "LOW" for a in sg),
                key=lambda lvl: {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}.get(lvl, 0),
            )
            incident = Incident(
                title=f"{category or 'Security'} activity from {source_ip} to {dest_ip}",
                description=(
                    f"{len(sg)} correlated alerts of category '{category}' detected between "
                    f"{source_ip} and {dest_ip} within a {CORRELATION_WINDOW_MINUTES}-minute window."
                ),
                alert_count=len(sg),
                priority=max_priority_level,
                risk_score=risk_score,
                first_seen=sg[0].timestamp,
                last_seen=sg[-1].timestamp,
                status="OPEN",
            )
            db.add(incident)
            db.flush()  # get incident.id
            for a in sg:
                a.incident_id = incident.id
            created += 1

    db.commit()
    return created
