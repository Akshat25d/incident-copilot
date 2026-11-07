---
id: SD-005
type: service_doc
title: Deploy and rollback procedure
services: [orders, payments]
tags: [deploy, rollback, restart, version, config]
---
# SD-005: Deploy and rollback procedure

## How versions work
- Each service reports its version in the `version` field of every log line and in its `/health` response.
- The version of orders and payments is chosen by the variables `ORDERS_VERSION` and `PAYMENTS_VERSION`. The default is `v1.0.0`.

## Deploy
- A deploy recreates the container with the new settings: `docker compose -f demo_app/docker-compose.yml up -d --force-recreate --no-deps <service>`
- A configuration change (for example `PAYMENTS_URL`) is deployed the same way.
- Every deploy is recorded in the deploy log, one JSON line with time, service, from-version, to-version and a note.

## Rollback
- Recreate the service with the previous version, which is the `from` value of its latest deploy log entry.
- Roll back the service that causes the failure first, not the services that only show its errors.

## Restart
- `docker compose -f demo_app/docker-compose.yml restart <service>`
- A restart clears in-memory state and held connections but does not fix a code or config problem.

## After any action
- Check the error ratio and the `version` field in new logs to confirm recovery.
