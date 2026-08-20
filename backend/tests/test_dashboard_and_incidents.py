import io


def _upload_sample(client, headers):
    csv_content = "timestamp,source_ip,destination_ip,alert_type,category,message,severity,asset_criticality\n"
    rows = []
    for i in range(12):
        rows.append(
            f"2026-01-01 10:{i:02d}:00,10.0.0.5,10.0.0.10,SSH Brute Force,Authentication Threat,"
            f"Failed SSH login attempt number {i},HIGH,HIGH"
        )
    csv_content += "\n".join(rows)
    files = {"file": ("alerts.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    return client.post("/api/alerts/upload", files=files, headers=headers)


def test_full_pipeline_and_dashboard(client, auth_headers):
    resp = _upload_sample(client, auth_headers)
    assert resp.status_code == 200
    assert resp.json()["rows_valid"] == 12

    process_resp = client.post("/api/analysis/process", headers=auth_headers)
    assert process_resp.status_code == 200
    body = process_resp.json()
    assert body["status"] == "SUCCESS"
    assert body["total_alerts"] == 12

    summary = client.get("/api/dashboard/summary", headers=auth_headers)
    assert summary.status_code == 200
    assert summary.json()["total_alerts"] == 12

    fatigue = client.get("/api/dashboard/fatigue", headers=auth_headers)
    assert fatigue.status_code == 200
    assert "alert_reduction_pct" in fatigue.json()

    incidents = client.get("/api/incidents", headers=auth_headers)
    assert incidents.status_code == 200


def test_incident_status_update(client, auth_headers):
    _upload_sample(client, auth_headers)
    client.post("/api/analysis/process", headers=auth_headers)
    incidents = client.get("/api/incidents", headers=auth_headers).json()
    if incidents:
        incident_id = incidents[0]["id"]
        resp = client.put(f"/api/incidents/{incident_id}/status", json={"status": "INVESTIGATING"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "INVESTIGATING"
