---
id: PM-012
type: postmortem
title: Database disk filled up
date: 2026-08-02
services: [orders]
tags: [disk, database, 503, storage, logs]
synthetic: true
---
# PM-012: Database disk filled up

## Summary
The volume holding Postgres data and logs ran out of space.

## Impact
Checkout returned 503 because writes failed.

## Detection
HighErrorRate on orders. The database error mentioned no space left on the device.

## Root cause
Log files were never rotated.

## Resolution
Pruned old logs and images, then expanded the volume.

## Follow-ups
Add log rotation and a disk usage alert.
