---
id: PM-008
type: postmortem
title: Orders latency after a schema change removed an index
date: 2026-05-18
services: [orders]
tags: [database, latency, slow-query, index]
synthetic: true
---
# PM-008: Orders latency after a schema change removed an index

## Summary
A migration dropped an index used by order status lookups.

## Impact
Slow checkouts. The connection pool ran hot.

## Detection
HighLatencyP95 on orders while payments latency stayed normal.

## Root cause
The migration recreated the table without the index.

## Resolution
Recreated the index and latency recovered.

## Follow-ups
Review query plans for schema migrations.
