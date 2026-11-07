---
id: PM-007
type: postmortem
title: Slow payment provider raised latency across the stack
date: 2026-04-30
services: [payments, orders, api-gateway]
tags: [latency, slow, dependency, timeout, p95]
synthetic: true
---
# PM-007: Slow payment provider raised latency across the stack

## Summary
A third-party card network responded slowly, so charge calls took several seconds.

## Impact
Checkout was slow for all users. Few requests failed outright.

## Detection
HighLatencyP95 on payments, orders and api-gateway. Orders logged "slow downstream call".

## Root cause
Provider degradation outside our control. Our timeouts were too generous.

## Resolution
Waited for the provider to recover and restarted payments to drop stuck connections.

## Follow-ups
Tighter timeouts and a circuit breaker around the provider.
