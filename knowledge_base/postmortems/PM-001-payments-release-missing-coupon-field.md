---
id: PM-001
type: postmortem
title: Payments release crashed on checkouts without a coupon code
date: 2026-01-14
services: [payments, orders, api-gateway]
tags: [release, regression, 5xx, rollback]
synthetic: true
---
# PM-001: Payments release crashed on checkouts without a coupon code

## Summary
Payments v0.9.4 added support for coupon codes. The new code read the coupon field from every charge request, but most customers never send one, so those requests crashed.

## Impact
Every checkout without a coupon failed with a 502. That was most of our traffic, until the release was rolled back.

## Detection
The HighErrorRate alert fired on payments first, then on orders and api-gateway, which were only passing the failures along. Payments logs showed "unhandled exception" with a KeyError on the coupon field. Orders logged "payment failed".

## Root cause
The code looked up the coupon field directly instead of treating it as optional. The test data used in the release always included a coupon, so the tests passed.

## Resolution
Rolled payments back to v0.9.3. The error ratio dropped within a few minutes and the alert resolved.

## Follow-ups
Add tests for requests with optional fields missing. Release to a small share of traffic first. During an incident, read the payments logs before the others, because the other services only show symptoms.
