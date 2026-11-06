import os
import random
import time

import httpx

TARGET = os.getenv("TARGET_URL", "http://localhost:8000")
RPS = float(os.getenv("RPS", "2"))
WARMUP_SECONDS = 30
ITEMS = ["keyboard", "mouse", "monitor", "laptop-stand", "headphones", "webcam"]


def main() -> None:
    ok = 0
    fail = 0
    started = time.monotonic()
    with httpx.Client(timeout=10.0) as client:
        while True:
            body = {
                "user_id": random.randint(1, 50),
                "item": random.choice(ITEMS),
                "amount": round(random.uniform(10, 500), 2),
            }
            try:
                success = client.post(f"{TARGET}/checkout", json=body).is_success
            except httpx.HTTPError:
                success = False
            warming_up = time.monotonic() - started < WARMUP_SECONDS
            if success:
                ok += 1
            elif warming_up:
                time.sleep(1 / RPS)
                continue
            else:
                fail += 1
            if (ok + fail) % 20 == 0:
                print(f"sent={ok + fail} ok={ok} failed={fail}", flush=True)
            time.sleep(1 / RPS)


if __name__ == "__main__":
    main()
