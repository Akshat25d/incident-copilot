---
id: PM-010
type: postmortem
title: Orders pointed at the wrong payments port
date: 2026-06-23
services: [orders, api-gateway]
tags: [config, endpoint, port, connection-refused, rollback]
synthetic: true
---
# PM-010: Orders pointed at the wrong payments port

## Summary
Orders v0.7.2 included a configuration change that set the payments port to one nothing listens on.

## Impact
Every payment step failed, so checkouts returned 502.

## Detection
HighErrorRate on orders and api-gateway. Orders logged connection errors. Payments was up and healthy with no errors of its own.

## Root cause
Incorrect endpoint configuration in the release.

## Resolution
Rolled orders back to v0.7.1.

## Follow-ups
Add a startup check that calls the payments health endpoint.
