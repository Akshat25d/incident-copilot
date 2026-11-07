---
id: SD-002
type: service_doc
title: api-gateway service
services: [api-gateway]
tags: [gateway, checkout, endpoints, config, errors]
---
# SD-002: api-gateway service

## Purpose
Public entry point for checkout requests.

## Interface
- `POST /checkout` with `user_id`, `item` and `amount`.
- `GET /health` and `GET /metrics`.

## Dependencies
- orders, at the address in `ORDERS_URL` (default `http://orders:8001`), with a 5 second timeout.

## Responses
- 200 with the order result on success.
- 502 "orders service failed" when the call to orders fails.

## Logs
- "orders call failed" with the underlying error.
- One "request" line per request with method, path, status and duration.

## Configuration
`ORDERS_URL`, `APP_VERSION`, `SERVICE_NAME`.
