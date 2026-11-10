# Retrieval evaluation: held-out test split (final)

- date: 2026-11-10 04:25 UTC
- incidents evaluated: 9 (the unanswerable incident is skipped)
- queries: original wording
- evaluated once; configurations were fixed on the dev split beforehand
- one incident moves a rate by about 11 points

| Config | Hit@1 | Hit@3 | Recall@5 | MRR | Look-alike above answer | Median latency |
|---|---|---|---|---|---|---|
| bm25 | 2/9 | 4/9 | 0.56 | 0.36 | 3/7 | 0.00s |
| D8 baseline: hybrid_rerank | 2/9 | 6/9 | 0.78 | 0.47 | 1/7 | 2.47s |
| selected: hybrid dw=0.25 boost=1.25 | 5/9 | 6/9 | 0.78 | 0.63 | 2/7 | 0.02s |

## Rank of the first correct document

| ID | Fault | bm25 | D8 baseline: hybrid_rerank | selected: hybrid dw=0.25 boost=1.25 |
|---|---|---|---|---|
| G-003 | bad_deploy | 4 | 2 | 1 |
| G-006 | db_pool_exhaustion | >10 | >10 | >10 |
| G-009 | memory_leak | >10 | 4 | 1 |
| G-012 | slow_payments | >10 | 3 | >10 |
| G-015 | config_error | 1 | 1 | 1 |
| G-018 | service_crash | 3 | 9 | 2 |
| G-022 | slow_query | 1 | 1 | 1 |
| G-023 | dns_intermittent | 6 | 2 | 5 |
| G-024 | oom_crash_loop | 2 | 2 | 1 |
