---
id: PM-010
type: postmortem
title: Orders used the staging payments port after a config copy
date: 2026-06-23
services: [orders, api-gateway]
tags: [config, endpoint, port, connection-refused, rollback]
synthetic: true
---
# PM-010: Orders used the staging payments port after a config copy

## Summary
Orders v0.7.2 shipped with a configuration file copied from the staging environment. In staging, payments listens on a different port from production.

## Impact
Every payment step failed, so every checkout returned 502 until the rollback.

## Detection
The HighErrorRate alert fired on orders and api-gateway. Orders logged connection errors on the call to payments. Payments itself looked fine: it was up, its health endpoint answered and its own error ratio stayed at zero, because it was not receiving any requests.

## Root cause
An environment-specific value, the payments address, was copied from staging into the production release.

## Resolution
Rolled orders back to v0.7.1.

## Follow-ups
Keep settings for each environment in separate files. Add a startup check where orders calls the payments health endpoint and refuses to start if it can't be reached.
