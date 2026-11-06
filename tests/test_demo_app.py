from fastapi.testclient import TestClient

from demo_app.payments import app


def test_health():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_charge_approves_and_sets_request_id():
    client = TestClient(app)
    resp = client.post("/charge", json={"order_id": 1, "amount": 10.0})
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"
    assert resp.headers["x-request-id"]


def test_metrics_exposed():
    client = TestClient(app)
    client.post("/charge", json={"order_id": 2, "amount": 5.0})
    resp = client.get("/metrics")
    assert "http_requests_total" in resp.text
