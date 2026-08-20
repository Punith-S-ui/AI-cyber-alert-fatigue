import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("APP_SECRET_KEY", "test-secret-key")


@pytest.fixture(scope="function")
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")

    # Force a fresh settings/engine bound to the temp db for isolation
    import importlib
    from app.core import config as config_module
    importlib.reload(config_module)
    config_module.settings.DATABASE_URL = f"sqlite:///{db_file}"

    from app.database import database as database_module
    importlib.reload(database_module)

    from app import main as main_module
    importlib.reload(main_module)

    with TestClient(main_module.app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    client.post("/api/auth/register", json={
        "full_name": "Test User", "email": "test@example.com",
        "password": "TestPass123", "role": "SECURITY_ANALYST",
    })
    resp = client.post("/api/auth/login", data={"username": "test@example.com", "password": "TestPass123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
