---
id: SD-001
type: service_doc
title: Architecture overview
services: [api-gateway, orders, payments]
tags: [architecture, dependencies, request-flow, request-id]
---
# SD-001: Architecture overview

## Services
- api-gateway (port 8000): public entry point.
- orders (port 8001): creates orders and calls payments. It is the only service that uses Postgres.
- payments (port 8002): charges an order. It has no dependencies of its own.

## Call chain
A client calls api-gateway, which calls orders, which writes to Postgres and then calls payments.

## How failures propagate
- A failure in payments shows up as 502 from orders, then 502 from the gateway.
- A database failure shows up as 503 from orders, then 502 from the gateway.
- Errors at the gateway therefore often mirror a problem further down the chain.

## Request tracing
Every request carries an `x-request-id` header. The same id appears in the logs of all three services, so one request can be followed end to end.

## Observability
Prometheus scrapes each service's `/metrics`. Container logs are shipped to Loki. Alertmanager sends alerts to the alert receiver. See SD-006.
