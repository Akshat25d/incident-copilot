---
id: SD-006
type: service_doc
title: Observability, alerts and useful queries
services: [api-gateway, orders, payments]
tags: [alerts, metrics, logs, prometheus, loki, queries]
---
# SD-006: Observability, alerts and useful queries

## Alerts
- HighErrorRate: more than 20% of a service's requests return 5xx over one minute, for 15 seconds.
- HighLatencyP95: p95 request latency above 1 second, for 15 seconds.
- HighMemory: resident memory above 250 MiB, for 15 seconds.
- ServiceDown: a metrics target is unreachable for 10 seconds.

## Where to look
- Prometheus on port 9090 for metrics and alert state.
- Alertmanager on port 9093.
- Loki on port 3100. Logs carry the label `service`.

## Metrics
- `http_requests_total{service, method, path, status}`
- `http_request_duration_seconds` (histogram)
- `process_resident_memory_bytes{job}`
- `up{job}`

## Log fields
Every log line is JSON with `ts`, `level`, `service`, `version`, `msg` and, for request-related lines, `request_id`.

## Useful queries
- Errors for one service: `{service="orders"} |~ "ERROR"`
- One request across services: `{service=~"api-gateway|orders|payments"} |= "<request_id>"`
- Error ratio: see RB-001.
- Latency: see RB-004.
