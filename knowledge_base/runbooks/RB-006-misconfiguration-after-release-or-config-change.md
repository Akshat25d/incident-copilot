---
id: RB-006
type: runbook
title: Misconfiguration after a release or config change
services: [api-gateway, orders, payments]
tags: [config, endpoint, url, port, connection-refused, rollback]
---
# RB-006: Misconfiguration after a release or config change

## Symptoms
- Errors start exactly when a release or configuration change was applied.
- One service fails to reach a dependency: connection refused or the wrong host.
- The dependency itself is up, healthy and shows no errors of its own.

## How to confirm
- Compare the time of the change in the deploy log with the first error.
- Inspect the caller's effective settings: `docker compose -f demo_app/docker-compose.yml exec <service> env | grep -i url`
- Check the dependency's health directly. If it is healthy, the problem is on the caller side.

## Likely causes
- A wrong host, port or URL in an environment variable.
- A missing or mistyped setting.

## Remediation
1. Roll the caller back to its previous version and configuration (SD-005). This is the safest action during an incident.
2. Alternatively correct the value and redeploy, if the correct value is certain.

## Verify recovery
- Calls reach the dependency again and the error ratio drops.

## Key difference from a crash
- Here the dependency is up. If it is down, follow RB-005.
