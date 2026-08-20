def test_register_and_login(client):
    resp = client.post("/api/auth/register", json={
        "full_name": "Jane Doe", "email": "jane@example.com",
        "password": "Secret123", "role": "SECURITY_ANALYST",
    })
    assert resp.status_code == 201
    assert resp.json()["email"] == "jane@example.com"

    login = client.post("/api/auth/login", data={"username": "jane@example.com", "password": "Secret123"})
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "full_name": "Jane Doe", "email": "jane2@example.com",
        "password": "Secret123", "role": "SECURITY_ANALYST",
    })
    login = client.post("/api/auth/login", data={"username": "jane2@example.com", "password": "WrongPass"})
    assert login.status_code == 401


def test_me_requires_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_with_token(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"
