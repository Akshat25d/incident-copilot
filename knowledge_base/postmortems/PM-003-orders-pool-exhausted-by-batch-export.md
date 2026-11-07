---
id: PM-003
type: postmortem
title: Orders connection pool exhausted by a batch export
date: 2026-02-21
services: [orders]
tags: [database, pool, 503, connections, batch]
synthetic: true
---
# PM-003: Orders connection pool exhausted by a batch export

## Summary
A new order export endpoint held database connections for long periods.

## Impact
Checkout returned 503 while the pool was drained.

## Detection
HighErrorRate on orders. Logs showed timeouts waiting for a connection. Postgres CPU was normal.

## Root cause
The export ran long queries on the same connection pool as checkout.

## Resolution
Restarted orders to release the connections and disabled the export.

## Follow-ups
Give batch jobs their own pool or a read replica.
