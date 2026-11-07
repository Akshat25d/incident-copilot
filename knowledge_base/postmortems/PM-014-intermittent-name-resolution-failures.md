---
id: PM-014
type: postmortem
title: Intermittent name resolution failures between services
date: 2026-09-17
services: [orders, payments]
tags: [dns, network, connection-error, 502]
synthetic: true
---
# PM-014: Intermittent name resolution failures between services

## Summary
After a network change, orders intermittently failed to resolve the payments hostname.

## Impact
Some checkouts failed with 502.

## Detection
HighErrorRate on orders. Connection errors mentioned name resolution. Payments was up and its own error ratio stayed at zero.

## Root cause
A misconfigured DNS resolver after the network change.

## Resolution
Rolled back the network change and restarted the resolver.

## Follow-ups
Add a DNS health check.
