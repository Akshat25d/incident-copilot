---
id: RB-001
type: runbook
title: High error rate after a release
services: [api-gateway, orders, payments]
tags: [errors, 5xx, release, deploy, regression, rollback]
---
# RB-001: High error rate after a release

## Symptoms
- HighErrorRate alert on one or more services.
- Status 500, 502 or 503 responses began shortly after a deploy.
- The failing service logs "unhandled exception" with a stack trace.
- Only some requests may fail, so the error ratio can be partial.

## How to confirm
- Compare when the errors started with the deploy log for each service.
- Compare the `version` field in log lines before and after the error start.
- Error ratio per service: `sum by (service) (rate(http_requests_total{status=~"5.."}[1m])) / sum by (service) (rate(http_requests_total[1m]))`
- Find stack traces: `{service="<service>"} |= "unhandled exception"`

## Likely causes
- A regression in the new release, such as a missing null check or an unhandled key.
- A change that is incompatible with data created by earlier versions.

## Remediation
1. Find the service whose own logs show the stack trace. Upstream services usually only mirror its failures.
2. Roll back that service to its previous version (see SD-005).
3. Do not roll forward during an incident unless the fix is trivial and already verified.

## Verify recovery
- The error ratio falls below 5% within two minutes and the alert resolves.
- New log lines show the previous `version`.

## Escalate if
- Rollback does not help: check dependencies (RB-004, RB-005) and the database (RB-002).
