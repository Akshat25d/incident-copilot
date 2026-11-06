import logging
import os

import httpx
from fastapi import HTTPException, Request
from pydantic import BaseModel

from demo_app.common import create_app, log

ORDERS_URL = os.getenv("ORDERS_URL", "http://orders:8001")

app = create_app()
client = httpx.Client(timeout=5.0)


class CheckoutRequest(BaseModel):
    user_id: int
    item: str
    amount: float


@app.post("/checkout")
def checkout(body: CheckoutRequest, request: Request) -> dict:
    request_id = request.state.request_id
    try:
        resp = client.post(
            f"{ORDERS_URL}/orders",
            json=body.model_dump(),
            headers={"x-request-id": request_id},
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        log(logging.ERROR, "orders call failed", request_id=request_id, error=str(exc))
        raise HTTPException(status_code=502, detail="orders service failed") from exc
    return resp.json()
