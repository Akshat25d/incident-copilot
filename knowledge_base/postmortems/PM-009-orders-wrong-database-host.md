---
id: PM-009
type: postmortem
title: Orders could not reach the database after a config change
date: 2026-06-05
services: [orders]
tags: [config, database, 503, hostname, rollback]
synthetic: true
---
# PM-009: Orders could not reach the database after a config change

## Summary
A configuration cleanup set the wrong database host for orders.

## Impact
All checkouts failed with 503.

## Detection
HighErrorRate on orders right after the change. The error text said the hostname could not be resolved.

## Root cause
A typo in the database host setting.

## Resolution
Rolled the orders configuration back.

## Follow-ups
Validate configuration values at startup and fail fast.
