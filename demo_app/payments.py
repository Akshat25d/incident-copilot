import logging
import os
import random
import time

from fastapi import Request
from pydantic import BaseModel

from demo_app import faults
from demo_app.common import create_app, log

app = create_app()
app.include_router(faults.router)

BAD_DEPLOY = os.getenv("FAULT_BAD_DEPLOY", "0") == "1"
LEAK_CHUNK_MB = 4
LEAK_MAX_CHUNKS = 75
MERCHANT_CONFIG: dict[int, dict] = {}
_receipt_cache: list[bytearray] = []


class ChargeRequest(BaseModel):
    order_id: int
    amount: float


def merchant_tier(order_id: int) -> str:
    return MERCHANT_CONFIG[order_id]["tier"]


def cache_receipt(request_id: str) -> None:
    if len(_receipt_cache) < LEAK_MAX_CHUNKS:
        chunk = bytearray(LEAK_CHUNK_MB * 1024 * 1024)
        for i in range(0, len(chunk), 4096):
            chunk[i] = 1
        _receipt_cache.append(chunk)
        if len(_receipt_cache) % 10 == 0:
            log(
                logging.WARNING,
                "receipt cache size",
                request_id=request_id,
                entries=len(_receipt_cache),
                approx_mb=len(_receipt_cache) * LEAK_CHUNK_MB,
            )


@app.post("/charge")
def charge(body: ChargeRequest, request: Request) -> dict:
    request_id = request.state.request_id
    slow = faults.get("slow_payments")
    if slow is not None:
        time.sleep(slow.get("delay_ms", 3000) / 1000)
    else:
        time.sleep(random.uniform(0.02, 0.08))
    if faults.get("memory_leak") is not None:
        cache_receipt(request_id)
    if BAD_DEPLOY and random.random() < 0.6:
        merchant_tier(body.order_id)
    log(
        logging.INFO,
        "charge approved",
        request_id=request_id,
        order_id=body.order_id,
        amount=body.amount,
    )
    return {"order_id": body.order_id, "status": "approved"}
