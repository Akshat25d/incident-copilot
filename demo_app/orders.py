import logging
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import HTTPException, Request
from psycopg_pool import ConnectionPool
from pydantic import BaseModel

from demo_app.common import create_app, log

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://shop:shop@postgres:5432/shop")
PAYMENTS_URL = os.getenv("PAYMENTS_URL", "http://payments:8002")
POOL_MAX = int(os.getenv("DB_POOL_MAX", "5"))

pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=POOL_MAX, timeout=3, open=False)
client = httpx.Client(timeout=5.0)


@asynccontextmanager
async def lifespan(app):
    pool.open()
    yield
    pool.close()


app = create_app(lifespan=lifespan)


class OrderRequest(BaseModel):
    user_id: int
    item: str
    amount: float


def set_status(order_id: int, status: str) -> None:
    with pool.connection() as conn:
        conn.execute("UPDATE orders SET status = %s WHERE id = %s", (status, order_id))


@app.post("/orders")
def create_order(body: OrderRequest, request: Request) -> dict:
    request_id = request.state.request_id
    headers = {"x-request-id": request_id}
    try:
        with pool.connection() as conn:
            row = conn.execute(
                "INSERT INTO orders (user_id, item, amount, status) "
                "VALUES (%s, %s, %s, 'pending') RETURNING id",
                (body.user_id, body.item, body.amount),
            ).fetchone()
    except Exception as exc:
        log(logging.ERROR, "database error", request_id=request_id, error=str(exc))
        raise HTTPException(status_code=503, detail="database unavailable") from exc

    order_id = row[0]
    try:
        resp = client.post(
            f"{PAYMENTS_URL}/charge",
            json={"order_id": order_id, "amount": body.amount},
            headers=headers,
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        set_status(order_id, "payment_failed")
        log(
            logging.ERROR,
            "payment failed",
            request_id=request_id,
            order_id=order_id,
            error=str(exc),
        )
        raise HTTPException(status_code=502, detail="payment failed") from exc

    set_status(order_id, "paid")
    log(logging.INFO, "order paid", request_id=request_id, order_id=order_id, amount=body.amount)
    return {"order_id": order_id, "status": "paid"}
