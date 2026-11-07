---
id: RB-003
type: runbook
title: Memory growth and suspected memory leak
services: [api-gateway, orders, payments]
tags: [memory, leak, oom, cache, restart]
---
# RB-003: Memory growth and suspected memory leak

## Symptoms
- HighMemory alert.
- `process_resident_memory_bytes` rises steadily with traffic and does not fall.
- Possible out-of-memory kill later (container exit code 137).
- Warning logs about a cache or buffer growing.

## How to confirm
- Plot `process_resident_memory_bytes{job="<service>"}` over the last hour.
- Check that growth tracks request volume rather than a single step change.
- Search logs: `{service="<service>"} |= "cache"`

## Likely causes
- An in-memory cache with no size limit or expiry.
- Objects created per request and never released.
- Large payloads buffered in memory.

## Remediation
1. Restart the service to reclaim memory. This is a mitigation, not a fix.
2. Fix the cause: bound the cache, add expiry, release per-request objects.
3. Do not just raise the memory limit; it only delays the failure.

## Verify recovery
- Memory returns to baseline after the restart and stays flat under normal traffic.

## Escalate if
- Memory jumped right after a deploy: see RB-001.
- The container keeps being killed: see RB-005.
