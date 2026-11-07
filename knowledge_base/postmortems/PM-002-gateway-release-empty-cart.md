---
id: PM-002
type: postmortem
title: Gateway release failed on empty cart requests
date: 2026-02-03
services: [api-gateway]
tags: [release, regression, 500, gateway, rollback]
synthetic: true
---
# PM-002: Gateway release failed on empty cart requests

## Summary
api-gateway v1.2.0 changed request parsing and raised a TypeError when the item list was empty.

## Impact
Checkout requests with an empty item list returned 500 from the gateway.

## Detection
HighErrorRate on api-gateway only. Orders and payments showed no errors and slightly lower traffic.

## Root cause
The parsing change did not handle an empty list.

## Resolution
Rolled api-gateway back to v1.1.3.

## Follow-ups
Add edge-case tests (empty and oversized input) to the release pipeline.
