---
id: RB-007
type: runbook
title: Disk space low or full
services: [orders]
tags: [disk, storage, database, no-space, logs]
---
# RB-007: Disk space low or full

## Symptoms
- Database writes fail with "no space left on device".
- Orders returns 503 and logs a database error mentioning the disk.
- Containers fail to start or log shipping stops.

## How to confirm
- Check free space: `df -h`
- Check Docker usage: `docker system df`
- Look for very large log files or unused images.

## Likely causes
- Logs that are never rotated.
- Accumulated unused images and volumes.
- Database growth.

## Remediation
1. Free space first: remove old logs and prune unused images.
2. Expand the volume if space keeps running out.
3. Restart the affected service only after space is available.

## Verify recovery
- Writes succeed and the error ratio drops.

## Note
- Restarting before freeing space does not help.
