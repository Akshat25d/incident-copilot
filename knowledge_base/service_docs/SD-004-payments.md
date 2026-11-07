---
id: SD-004
type: service_doc
title: payments service
services: [payments]
tags: [payments, charge, endpoints, baseline]
---
# SD-004: payments service

## Purpose
Charges an order.

## Interface
- `POST /charge` with `order_id` and `amount`.
- `GET /health` and `GET /metrics`.

## Behaviour
- Normal processing takes a few tens of milliseconds.
- It approves charges and logs "charge approved" with the order id and amount.
- It has no dependencies of its own.

## Logs
- "charge approved" on success.
- "unhandled exception" with a stack trace when a request raises an error.

## Configuration
`APP_VERSION`, `SERVICE_NAME`.
