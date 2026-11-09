import argparse
import json
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path

from evals import metrics
from evals.golden import Incident, load_golden
from rag.chunking import chunk_document
from rag.embeddings import FastEmbedEmbedder
from rag.loader import load_documents
from rag.rerank import FastEmbedReranker
from rag.retriever import MODES, HybridRetriever
from rag.store import QdrantStore

REPORT_DIR = Path("evals/reports")
RANK_LIMIT = 10


def score_mode(incident: Incident, ranking: list[str], latency: float) -> dict:
    expected = incident.expected_docs
    return {
        "ranking": ranking,
        "first_rank": metrics.first_rank(ranking, expected),
        "top1": metrics.hit_at(ranking, expected, 1),
        "top1_acceptable": metrics.hit_at(ranking, expected + incident.also_relevant, 1),
        "hit3": metrics.hit_at(ranking, expected, 3),
        "recall5": metrics.recall_at(ranking, expected, 5),
        "mrr": metrics.reciprocal_rank(ranking, expected),
        "distractor_outranks": metrics.distractor_outranks(ranking, expected, incident.distractors),
        "latency_s": round(latency, 3),
    }


def aggregate(rows: list[dict], mode: str) -> dict:
    cells = [row["modes"][mode] for row in rows]
    count = len(cells)
    flags = [c["distractor_outranks"] for c in cells if c["distractor_outranks"] is not None]
    return {
        "n": count,
        "top1": int(sum(c["top1"] for c in cells)),
        "top1_acceptable": int(sum(c["top1_acceptable"] for c in cells)),
        "hit3": int(sum(c["hit3"] for c in cells)),
        "recall5": sum(c["recall5"] for c in cells) / count,
        "mrr": sum(c["mrr"] for c in cells) / count,
        "distractor_outranks": sum(1 for flag in flags if flag),
        "distractor_n": len(flags),
        "median_latency_s": statistics.median(c["latency_s"] for c in cells),
    }


def evaluate(
    retriever: HybridRetriever, incidents: list[Incident], modes: list[str], depth: int
) -> dict:
    for mode in modes:
        retriever.search("warm up", mode=mode, k=3, candidates=3)
    rows = []
    for incident in incidents:
        row = {
            "id": incident.id,
            "fault": incident.fault,
            "difficulty": incident.difficulty,
            "query": incident.query,
            "expected": incident.expected_docs,
            "modes": {},
        }
        for mode in modes:
            started = time.perf_counter()
            hits = retriever.search(incident.query, mode=mode, k=depth, candidates=depth)
            latency = time.perf_counter() - started
            ranking = metrics.to_doc_ranking(hits, limit=RANK_LIMIT)
            row["modes"][mode] = score_mode(incident, ranking, latency)
        rows.append(row)
    return {"rows": rows, "aggregate": {mode: aggregate(rows, mode) for mode in modes}}


def fmt_rank(rank: int | None) -> str:
    return str(rank) if rank else ">10"


def render_report(meta: dict, result: dict) -> str:
    modes = list(result["aggregate"])
    n = meta["incidents"]
    lines = [
        f"# Retrieval evaluation: {meta['split']} split, {meta['label']}",
        "",
        f"- date: {meta['date']}",
        f"- incidents evaluated: {n} (unanswerable skipped: {meta['skipped']})",
        f"- knowledge base: {meta['documents']} documents, {meta['chunks']} chunks",
        f"- embedding model: {meta['embedder']}; reranker: {meta['reranker']}",
        f"- depth: {meta['depth']} chunks per ranking; results are scored per document "
        "(a document counts once, at its best-ranked chunk)",
        "",
        "| Mode | Hit@1 | Hit@3 | Recall@5 | MRR | Look-alike above answer | Median latency |",
        "|---|---|---|---|---|---|---|",
    ]
    for mode, agg in result["aggregate"].items():
        lines.append(
            f"| {mode} | {agg['top1']}/{agg['n']} | {agg['hit3']}/{agg['n']} "
            f"| {agg['recall5']:.2f} | {agg['mrr']:.2f} "
            f"| {agg['distractor_outranks']}/{agg['distractor_n']} "
            f"| {agg['median_latency_s']:.2f}s |"
        )
    lines += [
        "",
        f"With {n} incidents, one incident moves a rate by about {100 / n:.0f} points, "
        "so small differences are not meaningful.",
        "",
        "Hit@k: a correct document is among the top k. Recall@5: share of expected "
        "documents in the top 5. MRR: mean of 1/rank of the first correct document "
        "(0 if outside the top 10). Look-alike above answer: a listed look-alike "
        "document ranks above the first correct one.",
        "",
        "## Rank of the first correct document per incident",
        "",
        "| ID | Fault | Difficulty | " + " | ".join(modes) + " |",
        "|---|---|---|" + "---|" * len(modes),
    ]
    for row in result["rows"]:
        ranks = " | ".join(fmt_rank(row["modes"][m]["first_rank"]) for m in modes)
        lines.append(f"| {row['id']} | {row['fault']} | {row['difficulty']} | {ranks} |")
    failures = [r for r in result["rows"] if any(r["modes"][m]["top1"] == 0 for m in modes)]
    lines += ["", "## Incidents where at least one mode missed at rank 1", ""]
    if not failures:
        lines.append("None.")
    for row in failures:
        lines += [
            f"### {row['id']} ({row['fault']}, {row['difficulty']})",
            "",
            f"Query: {row['query']}",
            "",
            f"Expected: {', '.join(row['expected'])}",
            "",
        ]
        for mode in modes:
            lines.append(f"- {mode}: {', '.join(row['modes'][mode]['ranking'][:5])}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate retrieval on the golden set")
    parser.add_argument("--split", choices=["dev", "test"], default="dev")
    parser.add_argument(
        "--final", action="store_true", help="required to evaluate the held-out test split"
    )
    parser.add_argument("--label", default="baseline")
    parser.add_argument("--depth", type=int, default=30)
    parser.add_argument("--modes", nargs="+", choices=MODES, default=list(MODES))
    parser.add_argument("--kb", default="knowledge_base")
    parser.add_argument("--qdrant-url", default="http://localhost:6333")
    parser.add_argument("--collection", default="incident_kb")
    args = parser.parse_args()
    if args.split == "test" and not args.final:
        parser.error("the test split is held out; pass --final to evaluate it once")

    in_split = [i for i in load_golden() if i.split == args.split]
    incidents = [i for i in in_split if i.answerable]
    documents = load_documents(Path(args.kb))
    chunks = [chunk for doc in documents for chunk in chunk_document(doc)]
    embedder = FastEmbedEmbedder()
    reranker = FastEmbedReranker() if "hybrid_rerank" in args.modes else None
    store = QdrantStore(url=args.qdrant_url, collection=args.collection)
    if store.count() != len(chunks):
        raise SystemExit(
            f"index has {store.count()} chunks but the knowledge base has {len(chunks)}; "
            "run: uv run python -m rag.ingest"
        )
    retriever = HybridRetriever(chunks, embedder, store, reranker)
    result = evaluate(retriever, incidents, args.modes, args.depth)
    meta = {
        "split": args.split,
        "label": args.label,
        "date": datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        "incidents": len(incidents),
        "skipped": len(in_split) - len(incidents),
        "documents": len(documents),
        "chunks": len(chunks),
        "embedder": embedder.model_name,
        "reranker": reranker.model_name if reranker else "none",
        "depth": args.depth,
    }
    report = render_report(meta, result)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"retrieval_{args.split}_{args.label}"
    (REPORT_DIR / f"{stem}.md").write_text(report)
    (REPORT_DIR / f"{stem}.json").write_text(json.dumps({"meta": meta, **result}, indent=2) + "\n")
    print(report)
    print(f"saved to {REPORT_DIR / stem}.md and .json")


if __name__ == "__main__":
    main()
