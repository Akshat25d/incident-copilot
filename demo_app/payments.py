import logging
import random
import time

from fastapi import Request
from pydantic import BaseModel

from demo_app.common import create_app, log

app = create_app()


class ChargeRequest(BaseModel):
    order_id: int
    amount: float


@app.post("/charge")
def charge(body: ChargeRequest, request: Request) -> dict:
    time.sleep(random.uniform(0.02, 0.08))
    log(
        logging.INFO,
        "charge approved",
        request_id=request.state.request_id,
        order_id=body.order_id,
        amount=body.amount,
    )
    return {"order_id": body.order_id, "status": "approved"}
