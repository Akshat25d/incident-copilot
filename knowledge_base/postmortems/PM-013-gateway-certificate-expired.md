---
id: PM-013
type: postmortem
title: Gateway certificate expired
date: 2026-08-26
services: [api-gateway]
tags: [tls, certificate, handshake, expiry, edge]
synthetic: true
---
# PM-013: Gateway certificate expired

## Summary
The TLS certificate on the public edge expired.

## Impact
External users could not connect.

## Detection
Customer reports. Internal dashboards looked healthy.

## Root cause
Renewal automation had silently stopped.

## Resolution
Issued a new certificate and reloaded the proxy.

## Follow-ups
Alert thirty days before expiry.
