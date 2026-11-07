---
id: RB-010
type: runbook
title: Slow database queries and lock contention
services: [orders]
tags: [database, slow-query, index, lock, latency]
---
# RB-010: Slow database queries and lock contention

## Symptoms
- Orders latency rises while payments latency stays normal.
- Sessions in Postgres run for a long time or wait on locks.
- The connection pool runs hot and may be exhausted (see RB-002).

## How to confirm
- List sessions: `docker compose -f demo_app/docker-compose.yml exec postgres psql -U shop -d shop -c "select pid, state, wait_event_type, now() - query_start as age, left(query, 60) as query from pg_stat_activity where datname = 'shop' order by age desc;"`
- Look for queries that scan a large table without an index.

## Likely causes
- A missing index after a schema change.
- A long transaction blocking others.
- A heavy report query on the live database.

## Remediation
1. Terminate the blocking or runaway query: `select pg_terminate_backend(<pid>);`
2. Add the missing index.
3. Move heavy queries off the live path.

## Verify recovery
- Orders latency returns to normal and the pool is no longer saturated.
