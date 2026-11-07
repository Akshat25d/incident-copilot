---
id: RB-002
type: runbook
title: Database connection pool exhaustion
services: [orders]
tags: [database, pool, connections, 503, timeout]
---
# RB-002: Database connection pool exhaustion

## Symptoms
- Orders returns 503 "database unavailable".
- Orders logs "database error" with a timeout waiting for a connection.
- Failing requests take about as long as the pool timeout before they fail.
- Postgres itself looks healthy and its queries are fast.

## How to confirm
- Search logs: `{service="orders"} |= "database error"`
- List active sessions: `docker compose -f demo_app/docker-compose.yml exec postgres psql -U shop -d shop -c "select pid, state, now() - query_start as age, left(query, 60) as query from pg_stat_activity where datname = 'shop' order by age desc;"`
- Many sessions that stay busy or idle for a long time point to held connections.

## Likely causes
- Connections held by long-running work or never returned (a leak).
- A traffic spike beyond the pool size.
- A slow dependency while a connection is held.

## Remediation
1. Restart orders to release all connections. This is the fast mitigation.
2. Stop or terminate any long-running job holding connections.
3. Raise the pool size only as a temporary measure, after checking the Postgres connection limit.

## Verify recovery
- 503 responses stop and orders latency returns to normal.

## Escalate if
- It returns after a restart: a leak is likely and needs a code fix so connections are always released.
- Queries themselves are slow: see RB-010.
