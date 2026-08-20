import io


def test_create_alert(client, auth_headers):
    payload = {
        "source_ip": "10.0.0.5", "destination_ip": "10.0.0.10",
        "alert_type": "Port Scan", "message": "Test scan message",
        "severity": "MEDIUM",
    }
    resp = client.post("/api/alerts", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["alert_type"] == "Port Scan"


def test_create_alert_invalid_ip(client, auth_headers):
    payload = {
        "source_ip": "not-an-ip", "destination_ip": "10.0.0.10",
        "alert_type": "Port Scan", "message": "Test scan message",
    }
    resp = client.post("/api/alerts", json=payload, headers=auth_headers)
    assert resp.status_code == 422


def test_csv_upload(client, auth_headers):
    csv_content = (
        "timestamp,source_ip,destination_ip,alert_type,category,message,severity,asset_criticality\n"
        "2026-01-01 10:00:00,10.0.0.5,10.0.0.10,SSH Brute Force,Authentication Threat,"
        "Multiple failed logins,HIGH,HIGH\n"
        "2026-01-01 10:05:00,10.0.0.6,10.0.0.11,Port Scan,Network Scanning,"
        "Port scan detected,LOW,MEDIUM\n"
    )
    files = {"file": ("alerts.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    resp = client.post("/api/alerts/upload", files=files, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["rows_valid"] == 2


def test_upload_rejects_bad_extension(client, auth_headers):
    files = {"file": ("alerts.txt", io.BytesIO(b"hello"), "text/plain")}
    resp = client.post("/api/alerts/upload", files=files, headers=auth_headers)
    assert resp.status_code == 400


def test_list_alerts_requires_auth(client):
    resp = client.get("/api/alerts")
    assert resp.status_code == 401
