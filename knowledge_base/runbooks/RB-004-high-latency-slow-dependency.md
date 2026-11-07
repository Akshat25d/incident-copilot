---
id: RB-004
type: runbook
title: High latency or slow downstream dependency
services: [api-gateway, orders, payments]
tags: [latency, slow, timeout, dependency, p95]
---
# RB-004: High latency or slow downstream dependency

## Symptoms
- HighLatencyP95 alert on one or more services.
- Latency rises at the gateway and orders, with the cause further down the call chain.
- Orders logs the warning "slow downstream call".
- Errors appear only when calls exceed their timeouts.

## How to confirm
- p95 per service: `histogram_quantile(0.95, sum by (le, service) (rate(http_request_duration_seconds_bucket[1m])))`
- The slow service is the one whose own latency is high while the services it calls are fast.
- Search logs: `{service="orders"} |= "slow downstream call"`

## Likely causes
- A slow dependency or provider.
- A degraded service after long uptime.
- Slow database queries (see RB-010).
- CPU saturation (see RB-008).

## Remediation
1. Identify the slowest service in the chain.
2. If latency began after a deploy, roll back (RB-001).
3. Otherwise restart the slow service to drop stuck connections and state.
4. For a slow external provider, tighten timeouts and wait for recovery.

## Verify recovery
- p95 returns below 1 second and the alert resolves.

## Escalate if
- Timeouts start causing errors: follow RB-001 for the failing service.
