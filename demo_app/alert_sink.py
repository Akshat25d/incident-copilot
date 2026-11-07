import logging

from fastapi import Request

from demo_app.common import create_app, log

app = create_app()


@app.post("/alerts")
async def receive(request: Request) -> dict:
    payload = await request.json()
    alerts = payload.get("alerts", [])
    for alert in alerts:
        labels = alert.get("labels", {})
        log(
            logging.INFO,
            "alert received",
            status=alert.get("status"),
            alertname=labels.get("alertname"),
            target=labels.get("service") or labels.get("job"),
            severity=labels.get("severity"),
            summary=alert.get("annotations", {}).get("summary"),
        )
    return {"received": len(alerts)}
