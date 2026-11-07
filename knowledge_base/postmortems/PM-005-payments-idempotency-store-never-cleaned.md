---
id: PM-005
type: postmortem
title: Payments memory grew because processed request keys were never cleaned up
date: 2026-03-27
services: [payments]
tags: [memory, leak, cache, restart]
synthetic: true
---
# PM-005: Payments memory grew because processed request keys were never cleaned up

## Summary
To avoid charging a customer twice, payments remembered the key of every request it had handled. Nothing ever removed old keys, so memory kept rising with traffic.

## Impact
No customer saw errors yet. The process was heading towards an out-of-memory kill, which would have caused outages.

## Detection
The HighMemory alert fired on payments. The memory graph rose in a steady line that followed request volume. Payments also logged warnings about the size of its key store.

## Root cause
The keys were stored in an in-memory dictionary with no size limit and no expiry time.

## Resolution
Restarted payments, which freed the memory straight away. Later the dictionary was replaced with a store that expires keys after a fixed time.

## Follow-ups
Alert on the memory trend as well as the fixed limit. Add a review rule: every in-memory collection needs a size bound or an expiry.
