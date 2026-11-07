from fastapi.testclient import TestClient

from demo_app import faults
from demo_app.alert_sink import app as sink_app
from demo_app.payments import app as payments_app


def test_fault_can_be_set_and_cleared():
    client = TestClient(payments_app)
    resp = client.post("/admin/faults", json={"name": "slow_payments", "params": {"delay_ms": 10}})
    assert resp.status_code == 200
    assert faults.get("slow_payments") == {"delay_ms": 10}
    client.delete("/admin/faults")
    assert faults.get("slow_payments") is None


def test_alert_sink_accepts_alertmanager_payload():
    client = TestClient(sink_app)
    payload = {
        "alerts": [
            {
                "status": "firing",
                "labels": {"alertname": "HighErrorRate", "service": "payments"},
                "annotations": {"summary": "test"},
            }
        ]
    }
    resp = client.post("/alerts", json=payload)
    assert resp.status_code == 200
    assert resp.json()["received"] == 1
