---
id: PM-001
type: postmortem
title: Payments release failed on orders with a missing currency field
date: 2026-01-14
services: [payments, orders, api-gateway]
tags: [release, regression, 5xx, rollback]
synthetic: true
---
# PM-001: Payments release failed on orders with a missing currency field

## Summary
Release v0.9.4 of payments added currency handling that read a field missing from some orders.

## Impact
A share of checkouts failed with 502 until the release was rolled back.

## Detection
HighErrorRate fired on payments, then orders and api-gateway, minutes after the deploy.

## Root cause
The new code assumed the currency field was always present and raised a KeyError. No test covered a missing field.

## Resolution
Rolled payments back to v0.9.3. The error ratio returned to normal within two minutes.

## Follow-ups
Add a test for missing fields. Roll releases out to a small share of traffic first.
