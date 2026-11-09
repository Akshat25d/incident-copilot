# Retrieval evaluation: dev split, baseline

- date: 2026-11-09 13:48 UTC
- incidents evaluated: 15 (unanswerable skipped: 0)
- knowledge base: 30 documents, 174 chunks
- embedding model: BAAI/bge-small-en-v1.5; reranker: BAAI/bge-reranker-base
- depth: 30 chunks per ranking; results are scored per document (a document counts once, at its best-ranked chunk)

| Mode | Hit@1 | Hit@3 | Recall@5 | MRR | Look-alike above answer | Median latency |
|---|---|---|---|---|---|---|
| dense | 4/15 | 8/15 | 0.67 | 0.44 | 2/12 | 0.02s |
| bm25 | 11/15 | 15/15 | 1.00 | 0.86 | 0/12 | 0.00s |
| hybrid | 7/15 | 12/15 | 0.87 | 0.62 | 1/12 | 0.02s |
| hybrid_rerank | 10/15 | 14/15 | 0.93 | 0.81 | 0/12 | 2.45s |

With 15 incidents, one incident moves a rate by about 7 points, so small differences are not meaningful.

Hit@k: a correct document is among the top k. Recall@5: share of expected documents in the top 5. MRR: mean of 1/rank of the first correct document (0 if outside the top 10). Look-alike above answer: a listed look-alike document ranks above the first correct one.

## Rank of the first correct document per incident

| ID | Fault | Difficulty | dense | bm25 | hybrid | hybrid_rerank |
|---|---|---|---|---|---|---|
| G-001 | bad_deploy | easy | 6 | 2 | 3 | 1 |
| G-002 | bad_deploy | medium | 6 | 1 | 3 | 7 |
| G-004 | db_pool_exhaustion | easy | 1 | 1 | 1 | 1 |
| G-005 | db_pool_exhaustion | medium | 3 | 1 | 1 | 2 |
| G-007 | memory_leak | easy | 3 | 1 | 2 | 1 |
| G-008 | memory_leak | medium | 4 | 2 | 3 | 2 |
| G-010 | slow_payments | easy | 2 | 2 | 1 | 2 |
| G-011 | slow_payments | medium | 4 | 1 | 3 | 1 |
| G-013 | config_error | easy | >10 | 1 | 6 | 2 |
| G-014 | config_error | medium | >10 | 1 | 8 | 1 |
| G-016 | service_crash | easy | 1 | 1 | 1 | 1 |
| G-017 | service_crash | medium | 9 | 3 | 4 | 1 |
| G-019 | disk_full | medium | 2 | 1 | 1 | 1 |
| G-020 | cpu_saturation | medium | 1 | 1 | 1 | 1 |
| G-021 | tls_expiry | hard | 1 | 1 | 1 | 1 |

## Incidents where at least one mode missed at rank 1

### G-001 (bad_deploy, easy)

Query: Checkout started failing with 502s right after the payments release went out. Error rate alerts on all three services.

Expected: RB-001

- dense: PM-009, PM-014, PM-004, PM-001, PM-012
- bm25: PM-004, RB-001, PM-009, PM-001, SD-001
- hybrid: PM-001, PM-004, RB-001, PM-009, SD-003
- hybrid_rerank: RB-001, PM-001, PM-014, PM-010, SD-003

### G-002 (bad_deploy, medium)

Query: Some charge requests in payments blow up with a KeyError in the logs, but others succeed. What should we do?

Expected: RB-001

- dense: SD-004, PM-001, PM-005, SD-003, PM-010
- bm25: RB-001, SD-004, PM-001, PM-005, SD-005
- hybrid: SD-004, PM-001, RB-001, PM-005, SD-003
- hybrid_rerank: PM-001, SD-004, SD-003, PM-005, PM-011

### G-005 (db_pool_exhaustion, medium)

Query: Requests to orders hang for about three seconds and then fail. The logs say it timed out waiting for a connection.

Expected: RB-002

- dense: SD-003, PM-004, RB-002, PM-003, PM-009
- bm25: RB-002, SD-003, PM-003, SD-006, RB-007
- hybrid: RB-002, PM-003, PM-004, SD-003, PM-010
- hybrid_rerank: PM-003, RB-002, SD-003, PM-004, SD-002

### G-007 (memory_leak, easy)

Query: HighMemory alert on payments, resident memory keeps climbing as traffic comes in.

Expected: RB-003

- dense: PM-005, PM-011, RB-003, PM-007, PM-006
- bm25: RB-003, PM-005, PM-006, PM-011, SD-006
- hybrid: PM-005, RB-003, PM-011, PM-006, SD-006
- hybrid_rerank: RB-003, SD-006, PM-005, PM-011, PM-006

### G-008 (memory_leak, medium)

Query: Payments is logging warnings about a cache getting bigger. No customer errors yet but memory has climbed all morning.

Expected: RB-003

- dense: PM-005, PM-011, PM-006, RB-003, RB-007
- bm25: PM-005, RB-003, PM-006, RB-008, SD-004
- hybrid: PM-005, PM-006, RB-003, PM-011, RB-008
- hybrid_rerank: PM-005, RB-003, PM-011, RB-008, PM-006

### G-010 (slow_payments, easy)

Query: p95 latency alert above one second on api-gateway, orders and payments.

Expected: RB-004

- dense: PM-007, RB-004, SD-006, PM-008, RB-008
- bm25: SD-006, RB-004, RB-008, PM-008, PM-007
- hybrid: RB-004, PM-007, SD-006, PM-008, RB-008
- hybrid_rerank: SD-006, RB-004, RB-008, PM-007, PM-008

### G-011 (slow_payments, medium)

Query: Orders keeps logging slow downstream call to payments. No errors, checkout just feels sluggish.

Expected: RB-004

- dense: SD-003, PM-007, PM-004, RB-004, PM-008
- bm25: RB-004, PM-007, SD-003, RB-010, PM-010
- hybrid: PM-007, SD-003, RB-004, PM-010, RB-010
- hybrid_rerank: RB-004, PM-007, SD-003, PM-010, RB-008

### G-013 (config_error, easy)

Query: Orders cannot connect to payments, connection refused, but payments is up and its health check passes.

Expected: RB-006

- dense: PM-010, PM-009, SD-003, PM-014, PM-004
- bm25: RB-006, PM-010, SD-005, PM-014, RB-005
- hybrid: PM-010, PM-014, RB-005, PM-004, RB-002
- hybrid_rerank: PM-010, RB-006, PM-014, SD-005, RB-005

### G-014 (config_error, medium)

Query: Errors began the moment orders v1.0.1 was deployed. Payments shows no errors at all and seems to get no traffic.

Expected: RB-006

- dense: SD-003, PM-004, PM-010, PM-001, RB-001
- bm25: RB-006, RB-008, SD-001, PM-002, PM-005
- hybrid: PM-010, PM-014, PM-002, PM-007, PM-005
- hybrid_rerank: RB-006, RB-001, SD-005, PM-010, PM-002

### G-017 (service_crash, medium)

Query: The gateway returns 502 and orders can't resolve the payments hostname. The payments container isn't running.

Expected: RB-005

- dense: PM-010, PM-014, PM-004, PM-009, PM-001
- bm25: PM-010, PM-014, RB-005, SD-001, PM-009
- hybrid: PM-014, PM-010, PM-009, RB-005, SD-002
- hybrid_rerank: RB-005, PM-010, PM-014, SD-001, PM-009

### G-019 (disk_full, medium)

Query: Database writes fail with no space left on device and orders returns 503.

Expected: RB-007

- dense: PM-012, RB-007, PM-009, SD-003, RB-010
- bm25: RB-007, PM-012, RB-002, RB-010, PM-009
- hybrid: RB-007, PM-012, PM-009, RB-002, RB-010
- hybrid_rerank: RB-007, PM-012, PM-009, SD-003, RB-002

