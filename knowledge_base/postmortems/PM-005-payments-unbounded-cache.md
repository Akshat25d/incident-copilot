---
id: PM-005
type: postmortem
title: Payments memory grew without bound
date: 2026-03-27
services: [payments]
tags: [memory, leak, cache, restart]
synthetic: true
---
# PM-005: Payments memory grew without bound

## Summary
Payments memory climbed with each request until the HighMemory alert fired.

## Impact
No customer errors yet. An out-of-memory kill was likely within hours.

## Detection
HighMemory alert. Warning logs showed a receipt cache growing.

## Root cause
An in-process receipt cache had no size limit or expiry.

## Resolution
Restarted payments, then replaced the cache with a bounded LRU cache with an expiry time.

## Follow-ups
Add a memory trend alert in addition to the fixed threshold.
