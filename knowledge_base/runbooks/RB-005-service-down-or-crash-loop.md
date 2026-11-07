---
id: RB-005
type: runbook
title: Service down or crash loop
services: [api-gateway, orders, payments]
tags: [down, crash, restart, unreachable, oom, connection-error]
---
# RB-005: Service down or crash loop

## Symptoms
- ServiceDown alert: the metrics target stopped answering.
- Callers log connection errors or name resolution failures.
- The gateway returns 502.
- The container is exited or repeatedly restarting.

## How to confirm
- Check status: `docker compose -f demo_app/docker-compose.yml ps`
- Read the last log lines before the exit.
- Exit code 137 means the process was killed, often for memory (see RB-003).
- In Prometheus, `up{job="<service>"}` is 0 for the down service.

## Likely causes
- A crashed process or out-of-memory kill.
- A bad startup configuration.
- The service was stopped manually.

## Remediation
1. Restart the service.
2. If it crashes again, read its startup logs and roll back the latest release (RB-001, RB-006).
3. Check memory if the exit code was 137.

## Verify recovery
- The target is up, the health endpoint answers and the error ratio drops.

## Escalate if
- Callers fail but the target shows up and healthy: this is not a crash, see RB-006 or a network issue.
