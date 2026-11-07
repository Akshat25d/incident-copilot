---
id: SD-003
type: service_doc
title: orders service
services: [orders]
tags: [orders, database, pool, payments, config, errors]
---
# SD-003: orders service

## Purpose
Creates orders in Postgres and charges them through payments.

## Interface
- `POST /orders` with `user_id`, `item` and `amount`.
- `GET /health` and `GET /metrics`.

## Database
- Table `orders` with the status values `pending`, `paid` and `payment_failed`.
- Connection pool with 1 to 5 connections (`DB_POOL_MAX`). Waiting for a connection times out after 3 seconds.

## Dependencies
- Postgres.
- payments, at the address in `PAYMENTS_URL` (default `http://payments:8002`), with a 5 second timeout.

## Responses
- 503 "database unavailable" when a database operation fails, including a pool timeout.
- 502 "payment failed" when the payments call fails. The order is saved as `payment_failed`.

## Logs
- "database error" with the error text.
- "payment failed" with the error text.
- WARNING "slow downstream call" when payments takes longer than 1 second.
- "order paid" on success.

## Configuration
`DATABASE_URL`, `PAYMENTS_URL`, `DB_POOL_MAX`, `APP_VERSION`, `SERVICE_NAME`.
