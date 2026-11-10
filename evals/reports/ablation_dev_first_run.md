# Ablation experiments on the dev split

- date: 2026-11-10 04:18 UTC
- incidents: 15, each evaluated with two wordings (original and paraphrase)
- sanity check: reproduces the D8 baseline (original wording)
- one incident moves a rate by about 7 points

## Wording: original

| Config | Hit@1 | Hit@3 | Recall@5 | MRR | Look-alike above answer | Median latency |
|---|---|---|---|---|---|---|
| bm25 | 11/15 | 15/15 | 1.00 | 0.86 | 0/12 | 0.00s |
| dense | 4/15 | 8/15 | 0.67 | 0.44 | 2/12 | 0.01s |
| hybrid dw=1.0 boost=1.0 | 7/15 | 12/15 | 0.87 | 0.62 | 1/12 | 0.01s |
| hybrid dw=0.5 boost=1.0 | 8/15 | 12/15 | 0.87 | 0.69 | 1/12 | 0.02s |
| hybrid dw=0.25 boost=1.0 | 8/15 | 12/15 | 0.93 | 0.70 | 1/12 | 0.02s |
| hybrid dw=0.0 boost=1.0 | 11/15 | 15/15 | 1.00 | 0.86 | 0/12 | 0.02s |
| hybrid dw=1.0 boost=1.25 | 13/15 | 13/15 | 0.87 | 0.89 | 1/12 | 0.01s |
| hybrid dw=0.5 boost=1.25 | 13/15 | 13/15 | 0.93 | 0.89 | 1/12 | 0.01s |
| hybrid dw=0.25 boost=1.25 | 14/15 | 15/15 | 1.00 | 0.97 | 1/12 | 0.02s |
| hybrid dw=0.0 boost=1.25 | 15/15 | 15/15 | 1.00 | 1.00 | 0/12 | 0.01s |
| rerank pool=30 dw=1.0 boost=1.0 (D8 baseline) | 10/15 | 14/15 | 0.93 | 0.81 | 0/12 | 2.13s |
| rerank pool=10 dw=0.0 boost=1.25 | 10/15 | 14/15 | 1.00 | 0.82 | 0/12 | 0.59s |
| rerank pool=20 dw=0.0 boost=1.25 | 10/15 | 14/15 | 1.00 | 0.81 | 0/12 | 1.46s |
| rerank pool=30 dw=0.0 boost=1.25 | 10/15 | 14/15 | 0.93 | 0.81 | 0/12 | 2.25s |

## Wording: paraphrase

| Config | Hit@1 | Hit@3 | Recall@5 | MRR | Look-alike above answer | Median latency |
|---|---|---|---|---|---|---|
| bm25 | 4/15 | 7/15 | 0.73 | 0.44 | 1/12 | 0.00s |
| dense | 2/15 | 7/15 | 0.73 | 0.34 | 1/12 | 0.01s |
| hybrid dw=1.0 boost=1.0 | 5/15 | 9/15 | 0.80 | 0.53 | 1/12 | 0.02s |
| hybrid dw=0.5 boost=1.0 | 5/15 | 9/15 | 0.80 | 0.52 | 1/12 | 0.01s |
| hybrid dw=0.25 boost=1.0 | 4/15 | 8/15 | 0.67 | 0.47 | 1/12 | 0.01s |
| hybrid dw=0.0 boost=1.0 | 4/15 | 7/15 | 0.73 | 0.44 | 1/12 | 0.02s |
| hybrid dw=1.0 boost=1.25 | 10/15 | 13/15 | 0.87 | 0.79 | 1/12 | 0.02s |
| hybrid dw=0.5 boost=1.25 | 10/15 | 13/15 | 1.00 | 0.79 | 1/12 | 0.02s |
| hybrid dw=0.25 boost=1.25 | 10/15 | 14/15 | 1.00 | 0.79 | 1/12 | 0.01s |
| hybrid dw=0.0 boost=1.25 | 9/15 | 13/15 | 0.87 | 0.73 | 1/12 | 0.01s |
| rerank pool=30 dw=1.0 boost=1.0 (D8 baseline) | 6/15 | 12/15 | 0.87 | 0.59 | 1/12 | 2.23s |
| rerank pool=10 dw=0.0 boost=1.25 | 7/15 | 12/15 | 0.80 | 0.63 | 1/12 | 0.73s |
| rerank pool=20 dw=0.0 boost=1.25 | 6/15 | 13/15 | 0.93 | 0.65 | 1/12 | 1.49s |
| rerank pool=30 dw=0.0 boost=1.25 | 6/15 | 13/15 | 0.87 | 0.62 | 1/12 | 2.38s |

## Average MRR across both wordings

| Config | Original | Paraphrase | Average |
|---|---|---|---|
| hybrid dw=0.25 boost=1.25 | 0.97 | 0.79 | 0.88 |
| hybrid dw=0.0 boost=1.25 | 1.00 | 0.73 | 0.87 |
| hybrid dw=0.5 boost=1.25 | 0.89 | 0.79 | 0.84 |
| hybrid dw=1.0 boost=1.25 | 0.89 | 0.79 | 0.84 |
| rerank pool=20 dw=0.0 boost=1.25 | 0.81 | 0.65 | 0.73 |
| rerank pool=10 dw=0.0 boost=1.25 | 0.82 | 0.63 | 0.72 |
| rerank pool=30 dw=0.0 boost=1.25 | 0.81 | 0.62 | 0.72 |
| rerank pool=30 dw=1.0 boost=1.0 (D8 baseline) | 0.81 | 0.59 | 0.70 |
| bm25 | 0.86 | 0.44 | 0.65 |
| hybrid dw=0.0 boost=1.0 | 0.86 | 0.44 | 0.65 |
| hybrid dw=0.5 boost=1.0 | 0.69 | 0.52 | 0.61 |
| hybrid dw=0.25 boost=1.0 | 0.70 | 0.47 | 0.59 |
| hybrid dw=1.0 boost=1.0 | 0.62 | 0.53 | 0.58 |
| dense | 0.44 | 0.34 | 0.39 |

Selected: hybrid dw=0.0 boost=1.25

Rule: highest average MRR over both wordings on the dev split; among configurations within 0.03 of the best, the simplest (no reranker first, then fewest changed settings)

