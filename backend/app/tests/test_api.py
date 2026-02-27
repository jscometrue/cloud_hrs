from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "JSCORP HR"


def test_list_employees() -> None:
    resp = client.get("/api/employees")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "emp_no" in data[0]


def test_list_pay_runs_and_results() -> None:
    runs = client.get("/api/payroll/runs")
    assert runs.status_code == 200
    runs_data = runs.json()
    assert isinstance(runs_data, list)
    if runs_data:
        run_id = runs_data[0]["id"]
        results = client.get(f"/api/payroll/runs/{run_id}/results")
        assert results.status_code == 200
        results_data = results.json()
        assert isinstance(results_data, list)

