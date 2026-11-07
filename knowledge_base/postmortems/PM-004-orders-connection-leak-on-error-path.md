---
id: PM-004
type: postmortem
title: Orders slowly ran out of connections after a code change
date: 2026-03-09
services: [orders]
tags: [database, pool, leak, 503, gradual]
synthetic: true
---
# PM-004: Orders slowly ran out of connections after a code change

## Summary
Over several hours the orders pool drained and 503 responses increased gradually.

## Impact
Intermittent checkout failures that worsened over time.

## Detection
HighErrorRate fired late in the day. Earlier minor errors went unnoticed.

## Root cause
An error path in the payment step returned without releasing its database connection.

## Resolution
Restarted orders to recover, then shipped a fix that uses a context manager so connections are always released.

## Follow-ups
Alert on pool utilisation before it reaches 100%.
