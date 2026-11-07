---
id: RB-009
type: runbook
title: TLS certificate expiry
services: [api-gateway]
tags: [tls, certificate, handshake, expiry, edge]
---
# RB-009: TLS certificate expiry

## Symptoms
- External clients fail during the TLS handshake.
- Internal health checks and metrics look normal.
- The gateway sees little or no traffic, so its own error ratio stays low.

## How to confirm
- Check the certificate dates: `openssl s_client -connect <host>:443 | openssl x509 -noout -dates`

## Likely causes
- Automated renewal stopped working.
- The renewed certificate was not loaded by the proxy.

## Remediation
1. Issue or install a new certificate.
2. Reload the proxy.
3. Repair the renewal automation.

## Verify recovery
- Clients connect and gateway traffic returns to normal.
