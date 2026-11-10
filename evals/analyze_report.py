import json
import sys
from pathlib import Path

from evals.golden import load_golden

MISSING = 11


def rank_of(cell: dict) -> int:
    return cell["first_rank"] or MISSING


def main() -> None:
    default = "evals/reports/retrieval_dev_baseline.json"
    path = Path(sys.argv[1] if len(sys.argv) > 1 else default)
    data = json.loads(path.read_text())
    rows = data["rows"]
    agg = data["aggregate"]
    modes = list(agg)
    golden = {incident.id: incident for incident in load_golden()}
    n = len(rows)

    print(f"FILE {path.name}: {n} incidents, {data['meta']['chunks']} chunks")
    print("AGGREGATE (hit@1, hit@3, recall@5, mrr, lookalike above answer, latency)")
    for mode in modes:
        a = agg[mode]
        print(
            f"  {mode}: {a['top1']}/{n}, {a['hit3']}/{n}, {a['recall5']:.2f}, "
            f"{a['mrr']:.2f}, {a['distractor_outranks']}/{a['distractor_n']}, "
            f"{a['median_latency_s']:.2f}s"
        )
    print("HIT@1 COUNTING ALSO-RELEVANT DOCS AS ACCEPTABLE")
    for mode in modes:
        print(f"  {mode}: {agg[mode]['top1_acceptable']}/{n}")
    ordered = sorted(modes, key=lambda m: agg[m]["mrr"], reverse=True)
    if len(ordered) > 1:
        gap = agg[ordered[0]]["mrr"] - agg[ordered[1]]["mrr"]
        print(f"BEST MRR: {ordered[0]}, ahead of {ordered[1]} by {gap:.2f}")

    print("MISSED AT RANK 1 (incident: expected -> top result)")
    for mode in modes:
        misses = [r for r in rows if r["modes"][mode]["top1"] == 0]
        print(f"  {mode}: {len(misses)} misses")
        for r in misses:
            top = ",".join(r["modes"][mode]["ranking"][:1])
            print(f"    {r['id']} ({r['difficulty']}): {','.join(r['expected'])} -> {top}")

    miss1 = [r["id"] for r in rows if all(r["modes"][m]["top1"] == 0 for m in modes)]
    miss3 = [r["id"] for r in rows if all(r["modes"][m]["hit3"] == 0 for m in modes)]
    print(f"MISSED RANK 1 IN EVERY MODE: {miss1 or 'none'}")
    print(f"MISSED TOP 3 IN EVERY MODE: {miss3 or 'none'}")

    print("LOOK-ALIKE ABOVE ANSWER (incident, mode: expected vs look-alike)")
    found = False
    for r in rows:
        distractors = golden[r["id"]].distractors
        for mode in modes:
            cell = r["modes"][mode]
            if cell["distractor_outranks"]:
                found = True
                above = next((d for d in cell["ranking"] if d in distractors), "?")
                print(f"  {r['id']} {mode}: {','.join(r['expected'])} vs {above}")
    if not found:
        print("  none")

    if "hybrid" in modes and "hybrid_rerank" in modes:
        hyb = {r["id"]: rank_of(r["modes"]["hybrid"]) for r in rows}
        rer = {r["id"]: rank_of(r["modes"]["hybrid_rerank"]) for r in rows}
        better = [i for i in hyb if rer[i] < hyb[i]]
        worse = [i for i in hyb if rer[i] > hyb[i]]
        print("RERANKER VS HYBRID (rank of first correct document)")
        print(f"  better: {len(better)} {better or ''}")
        print(f"  worse: {len(worse)} {worse or ''}")
        print(f"  same: {n - len(better) - len(worse)}")

    if "dense" in modes and "bm25" in modes:
        d_only = [
            r["id"] for r in rows if r["modes"]["dense"]["top1"] and not r["modes"]["bm25"]["top1"]
        ]
        b_only = [
            r["id"] for r in rows if r["modes"]["bm25"]["top1"] and not r["modes"]["dense"]["top1"]
        ]
        print("DENSE VS BM25 AT RANK 1")
        print(f"  only dense correct: {d_only or 'none'}")
        print(f"  only bm25 correct: {b_only or 'none'}")


if __name__ == "__main__":
    main()
