
## D8 baseline, dev split (before any tuning)

Setup: 15 answerable dev incidents from the golden set, 174 chunks, bge-small embeddings and the bge-reranker-base reranker. The held-out test split was not touched. With 15 incidents, one incident moves a rate by about 7 points, so small gaps mean nothing.

| Mode | Hit@1 | Hit@3 | Recall@5 | MRR | Look-alike above answer | Median latency |
|---|---|---|---|---|---|---|
| dense | 4/15 | 8/15 | 0.67 | 0.44 | 2/12 | 0.02s |
| bm25 | 11/15 | 15/15 | 1.00 | 0.86 | 0/12 | under 0.01s |
| hybrid | 7/15 | 12/15 | 0.87 | 0.62 | 1/12 | 0.02s |
| hybrid_rerank | 10/15 | 14/15 | 0.93 | 0.81 | 0/12 | 2.45s |

Hit@1 when I also accept documents I had listed as acceptable before seeing results (for example the postmortem of the same fault): dense 12/15, bm25 13/15, hybrid 15/15, hybrid_rerank 15/15.

### What I see

1. Best mode: keyword search (BM25) had the best MRR (0.86), was correct at rank 1 in 11 of 15 incidents and inside the top 3 in all 15. The reranker came next (0.81); its 0.05 gap to BM25 is smaller than what one incident can change, so I treat them as roughly tied. Hybrid (0.62) and dense (0.44) were clearly behind. Dense was never the only method correct at rank 1, while BM25 was the only one in 7 incidents.

2. Failures: only G-008 missed at rank 1 in every mode. All four put PM-005, the postmortem about an unbounded in-memory cache, ahead of runbook RB-003. PM-005 describes almost exactly the symptom in the query (warnings about a growing cache), and I had listed it as acceptable on D7, so I left the label alone. No incident missed the top 3 in every mode. Every rank-1 miss of the reranker (5) and of hybrid (8) was a document I had listed as acceptable; dense had 3 top results that were not on that list (G-001, G-014, G-017).

3. Look-alikes: a listed look-alike beat the right document three times. G-013: dense and hybrid put RB-005 (service down) above RB-006 (misconfiguration). G-014: dense put RB-001 (release regression) above RB-006. Both pairs share "errors began after a change" language. BM25 and the reranker had 0/12.

4. Reranker: compared with plain hybrid it improved the rank of the first correct document in 7 incidents, made it worse in 3 (G-002, G-005, G-010) and left 5 unchanged. MRR went from 0.62 to 0.81. It did not beat BM25 alone (0.81 vs 0.86).

5. Cost: dense and hybrid were under 0.03s per query, BM25 under 0.01s, the reranker 2.45s on CPU. On the dev split it does not pay for itself yet.

6. What matters for the agent: it will read the top 5 results, not only the first, so Hit@3 and Recall@5 matter more than Hit@1. BM25 (15/15 in the top 3) and the reranker (14/15) look fine; dense alone (8/15) is not good enough.

### Caveats

- Dev queries are in the wording I drafted together with the documents. The 8 queries I rewrote in my own words are all in the held-out test split. BM25 rewards shared vocabulary, so its lead on dev may be inflated, and the test split is the fairer measure.
- Fifteen incidents is a small set.
- This is a baseline with no tuning.

### Plan for D9

1. Rewrite the dev queries in my own words and rerun the baseline. Keep both result sets, and say which wording each came from.
2. Weighted fusion. Hybrid is worse than BM25 alone because RRF treats the weak dense list as an equal. For example, a passage ranked 1 in one list scores 1/61 = 0.016, while a passage ranked 3 in both scores 2/63 = 0.032, so documents that both lists like a little beat the keyword search's first choice.
3. Document-type and service awareness: prefer runbooks, or filter by the service named in the alert.
