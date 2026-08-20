"""Idempotent seed script: creates demo users and >= 500 realistic DEMO DATA
alerts (with intentional duplicates, near-duplicates, anomalies and a spread
of severities), then runs the full AI/ML pipeline so the dashboard has
real, visible results immediately after setup.

Safe to run multiple times - it checks for existing data before inserting.
"""
import random
from datetime import datetime, timedelta

from app.database.init_db import init_db
from app.database.database import SessionLocal
from app.models.user import User, UserRole
from app.models.alert import Alert
from app.core.security import hash_password
from app.services.analysis_service import run_full_analysis

random.seed(7)

ALERT_TYPES = {
    "SSH Brute Force": "Authentication Threat",
    "Port Scan": "Network Scanning",
    "SQL Injection Attempt": "Web Attack",
    "Malware Detection": "Malware Activity",
    "Suspicious Login": "Authentication Threat",
    "Privilege Escalation": "Authentication Threat",
    "Data Exfiltration": "Data Exfiltration",
    "DDoS Activity": "Denial of Service",
    "DNS Tunneling": "Data Exfiltration",
    "Ransomware Activity": "Malware Activity",
}

MESSAGE_TEMPLATES = {
    "SSH Brute Force": "Multiple failed SSH login attempts detected from {src} targeting {dst}",
    "Port Scan": "TCP port scan detected originating from {src} against {dst}",
    "SQL Injection Attempt": "Malicious SQL payload detected in HTTP request from {src} to {dst}",
    "Malware Detection": "Known malware signature detected on host {dst}, source {src}",
    "Suspicious Login": "Login from unusual geographic location for account originating at {src}",
    "Privilege Escalation": "Unexpected privilege escalation attempt detected on host {dst} from {src}",
    "Data Exfiltration": "Large outbound data transfer detected from {src} to external host {dst}",
    "DDoS Activity": "High volume traffic flood detected targeting {dst} from {src}",
    "DNS Tunneling": "Anomalous DNS query pattern suggesting tunneling from {src} to {dst}",
    "Ransomware Activity": "Rapid file encryption behavior detected on host {dst}, source {src}",
}

INTERNAL_IPS = [f"10.0.{a}.{b}" for a in range(1, 6) for b in (5, 12, 25, 40, 77, 101, 150, 200)]
EXTERNAL_IPS = [f"203.0.{a}.{b}" for a in range(1, 15) for b in (10, 22, 33, 44, 55)]
NOISY_SOURCES = random.sample(EXTERNAL_IPS, 6)  # a handful of IPs that spam alerts (drives clustering/dedup)

CRITICALITY_CHOICES = ["LOW", "MEDIUM", "HIGH"]
PROTOCOLS = ["TCP", "UDP", "ICMP", "HTTP", "HTTPS", "DNS"]


def random_ip(noisy_bias=0.35):
    if random.random() < noisy_bias:
        return random.choice(NOISY_SOURCES)
    return random.choice(EXTERNAL_IPS)


def build_alert(base_time: datetime) -> dict:
    alert_type = random.choice(list(ALERT_TYPES.keys()))
    category = ALERT_TYPES[alert_type]
    src = random_ip()
    dst = random.choice(INTERNAL_IPS)
    offset_minutes = random.randint(0, 60 * 24 * 14)  # spread over 14 days
    ts = base_time + timedelta(minutes=offset_minutes)

    severity = random.choices(
        ["LOW", "MEDIUM", "HIGH", "CRITICAL"], weights=[35, 35, 20, 10]
    )[0]

    return {
        "timestamp": ts,
        "source_ip": src,
        "destination_ip": dst,
        "source_port": random.choice([22, 80, 443, 3389, 1433, random.randint(1024, 65000)]),
        "destination_port": random.choice([22, 80, 443, 3389, 1433, random.randint(1024, 65000)]),
        "protocol": random.choice(PROTOCOLS),
        "alert_type": alert_type,
        "category": category,
        "message": MESSAGE_TEMPLATES[alert_type].format(src=src, dst=dst),
        "severity": severity,
        "source": "DEMO DATA",
        "asset_criticality": random.choice(CRITICALITY_CHOICES),
        "status": "NEW",
    }


def seed_users(db):
    demo_users = [
        {"full_name": "Alice Admin", "email": "admin@demo.local", "password": "Admin@123", "role": UserRole.ADMIN},
        {"full_name": "Sam Analyst", "email": "analyst@demo.local", "password": "Analyst@123", "role": UserRole.SECURITY_ANALYST},
    ]
    for u in demo_users:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if existing:
            continue
        db.add(User(
            full_name=u["full_name"],
            email=u["email"],
            hashed_password=hash_password(u["password"]),
            role=u["role"],
        ))
    db.commit()


def seed_alerts(db, target_count=520):
    existing = db.query(Alert).count()
    if existing >= target_count:
        print(f"Alerts already seeded ({existing} rows). Skipping alert generation.")
        return

    base_time = datetime.utcnow() - timedelta(days=14)
    to_create = target_count - existing

    generated = []
    # ~15% deliberate near-duplicate bursts so deduplication has real work to do
    while len(generated) < to_create:
        alert = build_alert(base_time)
        generated.append(alert)
        if random.random() < 0.15:
            burst_size = random.randint(1, 3)
            for _ in range(burst_size):
                if len(generated) >= to_create:
                    break
                dup = dict(alert)
                dup["timestamp"] = alert["timestamp"] + timedelta(minutes=random.randint(1, 8))
                generated.append(dup)

    generated = generated[:to_create]

    for rec in generated:
        db.add(Alert(**rec))
    db.commit()
    print(f"Seeded {len(generated)} demo alerts.")


def main():
    init_db()
    db = SessionLocal()
    try:
        seed_users(db)
        seed_alerts(db)
        print("Running full AI/ML analysis pipeline on seeded data...")
        run = run_full_analysis(db)
        print(f"Analysis run #{run.id} finished with status: {run.status}")
        print(f"Total alerts: {run.total_alerts} | Duplicates: {run.duplicate_alerts} | "
              f"Clusters: {run.clusters_created} | Anomalies: {run.anomalies_found} | "
              f"Incidents: {run.incidents_created} | Reduction: {run.alert_reduction_pct}%")
    finally:
        db.close()


if __name__ == "__main__":
    main()
