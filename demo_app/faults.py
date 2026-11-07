import threading

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/admin")

_lock = threading.Lock()
_active: dict[str, dict] = {}


class FaultRequest(BaseModel):
    name: str
    params: dict = {}


def get(name: str) -> dict | None:
    with _lock:
        return _active.get(name)


@router.post("/faults")
def set_fault(body: FaultRequest) -> dict:
    with _lock:
        _active[body.name] = body.params
        return {"active": list(_active)}


@router.delete("/faults")
def clear_faults() -> dict:
    with _lock:
        _active.clear()
        return {"active": []}
