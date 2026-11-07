---
id: PM-011
type: postmortem
title: Payments was OOM-killed and restarted repeatedly
date: 2026-07-11
services: [payments]
tags: [crash, oom, restart, memory, exit-137]
synthetic: true
---
# PM-011: Payments was OOM-killed and restarted repeatedly

## Summary
Payments exited with code 137 several times in a few hours.

## Impact
Brief gaps in checkout whenever the container restarted.

## Detection
ServiceDown alert flapping. Memory had risen for hours beforehand.

## Root cause
A slow memory leak reached the container memory limit.

## Resolution
Restarted payments and temporarily raised the memory limit while the leak was fixed.

## Follow-ups
Alert on memory trend.
