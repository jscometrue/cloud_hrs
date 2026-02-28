from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "JSCORP HR"


def test_login_admin() -> None:
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"


def test_login_sample_accounts() -> None:
    for username in ("sample1", "sample2", "sample3"):
        resp = client.post("/api/auth/login", json={"username": username, "password": "sample123"})
        assert resp.status_code == 200, f"{username}: {resp.text}"
        data = resp.json()
        assert "access_token" in data


def test_list_employees() -> None:
    login = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/employees", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "emp_no" in data[0]


def test_list_pay_runs_and_results() -> None:
    login = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    runs = client.get("/api/payroll/runs", headers=headers)
    assert runs.status_code == 200
    runs_data = runs.json()
    assert isinstance(runs_data, list)
    if runs_data:
        run_id = runs_data[0]["id"]
        results = client.get(f"/api/payroll/runs/{run_id}/results", headers=headers)
        assert results.status_code == 200
        results_data = results.json()
        assert isinstance(results_data, list)

