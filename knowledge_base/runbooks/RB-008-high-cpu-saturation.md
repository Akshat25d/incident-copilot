---
id: RB-008
type: runbook
title: High CPU saturation
services: [api-gateway, orders, payments]
tags: [cpu, saturation, load, latency, traffic]
---
# RB-008: High CPU saturation

## Symptoms
- Latency rises for all requests with few or no errors.
- CPU of one container sits near its limit.
- Throughput stops growing even as traffic rises.

## How to confirm
- Check container usage: `docker stats --no-stream`
- Compare request rate with the usual level to see whether this is a traffic spike.

## Likely causes
- A traffic spike.
- A hot loop or expensive code path.
- A release that made request handling heavier.

## Remediation
1. If traffic spiked, rate-limit or add capacity.
2. If it began after a release, roll back (RB-001).
3. Otherwise profile the service to find the hot path.

## Verify recovery
- CPU returns to normal and p95 latency drops below 1 second.
