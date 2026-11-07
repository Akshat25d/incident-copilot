---
id: PM-006
type: postmortem
title: Orders leaked memory through per-request HTTP clients
date: 2026-04-12
services: [orders]
tags: [memory, leak, http-client, restart]
synthetic: true
---
# PM-006: Orders leaked memory through per-request HTTP clients

## Summary
Orders memory and open connections grew steadily.

## Impact
Slower responses late in the cycle. No hard failures.

## Detection
HighMemory alert on orders. There were no cache-related log messages.

## Root cause
A new HTTP client was created for every payments call and never closed.

## Resolution
Restarted orders, then switched to one shared client.

## Follow-ups
Add client reuse to the code review checklist.
