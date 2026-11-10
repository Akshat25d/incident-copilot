import argparse
import json
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from evals import metrics
from evals.golden import Incident, load_golden
from evals.retrieval_eval import RANK_LIMIT, aggregate, score_mode
from rag.chunking import chunk_document
from rag.embeddings import FastEmbedEmbedder
from rag.loader import load_documents
from rag.rerank import FastEmbedReranker
from rag.retriever import HybridRetriever, RetrievalConfig
from rag.store import QdrantStore

REPORT_DIR = Path("evals/reports")
WORDINGS = ("original", "paraphrase")
TIE_MARGIN = 0.03
BASELINE_RERANK = "rerank pool=30 dw=1.0 boost=1.0 (D8 baseline)"
RULE = (
    "highest average MRR over both wordings on the dev split; among configurations "
    "within 0.03 of the best, the simplest (no reranker first, then fewest changed settings); "
    "remaining ties go to the higher paraphrase-wording MRR (amended after the first dev run, "
    "before any test-split evaluation, because the original tie-break was alphabetical)"
)
COLUMNS = [
    "Config",
    "Hit@1",
    "Hit@3",
    "Recall@5",
    "MRR",
    "Look-alike above answer",
    "Median latency",
]
HEADER = "| " + " | ".join(COLUMNS) + " |"
SEPARATOR = "|" + "---|" * len(COLUMNS)


@dataclass(frozen=True)
class Experiment:
    name: str
    mode: str
    config: RetrievalConfig

    def complexity(self) -> tuple[int, int]:
        default = RetrievalConfig()
        changed = sum(
            getattr(self.config, field) != getattr(default, field)
            for field in ("dense_weight", "bm25_weight", "runbook_boost", "pool")
        )
        fused = 1 if self.mode in ("hybrid", "hybrid_rerank") else 0
        return (1 if self.mode == "hybrid_rerank" else 0, fused + changed)


def stage_one() -> list[Experiment]:
    experiments = [
        Experiment("bm25", "bm25", RetrievalConfig()),
        Experiment("dense", "dense", RetrievalConfig()),
    ]
    for boost in (1.0, 1.25):
        for weight in (1.0, 0.5, 0.25, 0.0):
            config = RetrievalConfig(dense_weight=weight, runbook_boost=boost)
            name = f"hybrid dw={weight} boost={boost}"
            experiments.append(Experiment(name, "hybrid", config))
    return experiments


def stage_two(best: Experiment) -> list[Experiment]:
    weight = best.config.dense_weight
    boost = best.config.runbook_boost
    experiments = [Experiment(BASELINE_RERANK, "hybrid_rerank", RetrievalConfig())]
    seen = {RetrievalConfig()}
    for pool in (10, 20, 30):
        config = RetrievalConfig(dense_weight=weight, runbook_boost=boost, pool=pool)
        if config in seen:
            continue
        seen.add(config)
        name = f"rerank pool={pool} dw={weight} boost={boost}"
        experiments.append(Experiment(name, "hybrid_rerank", config))
    return experiments


def run_wording(
    retriever: HybridRetriever,
    incidents: list[Incident],
    experiments: list[Experiment],
    wording: str,
) -> dict:
    rows = []
    for incident in incidents:
        text = incident.query if wording == "original" else incident.query_paraphrase
        row = {
            "id": incident.id,
            "fault": incident.fault,
            "difficulty": incident.difficulty,
            "modes": {},
        }
        for exp in experiments:
            started = time.perf_counter()
            hits = retriever.search(text, mode=exp.mode, k=exp.config.list_depth, config=exp.config)
            latency = time.perf_counter() - started
            ranking = metrics.to_doc_ranking(hits, limit=RANK_LIMIT)
            row["modes"][exp.name] = score_mode(incident, ranking, latency)
        rows.append(row)
    return {"rows": rows, "aggregate": {e.name: aggregate(rows, e.name) for e in experiments}}


def merge(results: dict, extra: dict) -> None:
    for wording, data in extra.items():
        base = results[wording]
        for row, new_row in zip(base["rows"], data["rows"], strict=True):
            row["modes"].update(new_row["modes"])
        base["aggregate"].update(data["aggregate"])


def average_mrr(results: dict, name: str) -> float:
    total = sum(results[wording]["aggregate"][name]["mrr"] for wording in WORDINGS)
    return total / len(WORDINGS)


def pick(experiments: list[Experiment], results: dict) -> Experiment:
    scores = {exp.name: average_mrr(results, exp.name) for exp in experiments}
    best = max(scores.values())
    close = [exp for exp in experiments if best - scores[exp.name] <= TIE_MARGIN]
    return min(
        close,
        key=lambda exp: (
            exp.complexity(),
            -results["paraphrase"]["aggregate"][exp.name]["mrr"],
            exp.name,
        ),
    )


def table_row(name: str, agg: dict) -> str:
    n = agg["n"]
    cells = [
        name,
        f"{agg['top1']}/{n}",
        f"{agg['hit3']}/{n}",
        f"{agg['recall5']:.2f}",
        f"{agg['mrr']:.2f}",
        f"{agg['distractor_outranks']}/{agg['distractor_n']}",
        f"{agg['median_latency_s']:.2f}s",
    ]
    return "| " + " | ".join(cells) + " |"


def sanity_check(results: dict) -> str:
    path = REPORT_DIR / "retrieval_dev_baseline.json"
    if not path.exists():
        return "no D8 baseline report found, check skipped"
    baseline = json.loads(path.read_text())["aggregate"]
    pairs = {
        "bm25": "bm25",
        "dense": "dense",
        "hybrid dw=1.0 boost=1.0": "hybrid",
        BASELINE_RERANK: "hybrid_rerank",
    }
    mismatches = []
    for name, base_mode in pairs.items():
        mine = results["original"]["aggregate"].get(name)
        if mine is None:
            continue
        theirs = baseline[base_mode]
        if mine["top1"] != theirs["top1"] or round(mine["mrr"], 4) != round(theirs["mrr"], 4):
            mismatches.append(name)
    if mismatches:
        return f"DIFFERS from the D8 baseline for: {mismatches}"
    return "reproduces the D8 baseline (original wording)"


def render(meta: dict, experiments: list[Experiment], results: dict, selected: Experiment) -> str:
    n = meta["incidents"]
    lines = [
        "# Ablation experiments on the dev split",
        "",
        f"- date: {meta['date']}",
        f"- incidents: {n}, each evaluated with two wordings (original and paraphrase)",
        f"- sanity check: {meta['sanity']}",
        f"- one incident moves a rate by about {100 / n:.0f} points",
        "",
    ]
    for wording in WORDINGS:
        lines += [f"## Wording: {wording}", "", HEADER, SEPARATOR]
        for exp in experiments:
            lines.append(table_row(exp.name, results[wording]["aggregate"][exp.name]))
        lines.append("")
    lines += [
        "## Average MRR across both wordings",
        "",
        "| Config | Original | Paraphrase | Average |",
        "|---|---|---|---|",
    ]
    ranked = sorted(experiments, key=lambda e: average_mrr(results, e.name), reverse=True)
    for exp in ranked:
        original = results["original"]["aggregate"][exp.name]["mrr"]
        paraphrase = results["paraphrase"]["aggregate"][exp.name]["mrr"]
        average = average_mrr(results, exp.name)
        lines.append(f"| {exp.name} | {original:.2f} | {paraphrase:.2f} | {average:.2f} |")
    lines += ["", f"Selected: {selected.name}", "", f"Rule: {RULE}", ""]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Ablation experiments on the dev split")
    parser.add_argument("--no-rerank", action="store_true", help="skip stage 2 (fast check)")
    parser.add_argument("--kb", default="knowledge_base")
    parser.add_argument("--qdrant-url", default="http://localhost:6333")
    parser.add_argument("--collection", default="incident_kb")
    args = parser.parse_args()

    incidents = [i for i in load_golden() if i.split == "dev" and i.answerable]
    missing = [i.id for i in incidents if not i.query_paraphrase]
    if missing:
        raise SystemExit(f"missing query_paraphrase for: {missing}")
    documents = load_documents(Path(args.kb))
    chunks = [chunk for doc in documents for chunk in chunk_document(doc)]
    embedder = FastEmbedEmbedder()
    reranker = None if args.no_rerank else FastEmbedReranker()
    store = QdrantStore(url=args.qdrant_url, collection=args.collection)
    if store.count() != len(chunks):
        raise SystemExit(
            f"index has {store.count()} chunks but the knowledge base has {len(chunks)}; "
            "run: uv run python -m rag.ingest"
        )
    retriever = HybridRetriever(chunks, embedder, store, reranker)
    for mode in ("dense", "bm25", "hybrid") + (() if reranker is None else ("hybrid_rerank",)):
        retriever.search("warm up", mode=mode, k=3, candidates=3)

    first = stage_one()
    results = {w: run_wording(retriever, incidents, first, w) for w in WORDINGS}
    experiments = list(first)
    if reranker is not None:
        best_hybrid = pick([e for e in first if e.mode == "hybrid"], results)
        second = stage_two(best_hybrid)
        extra = {w: run_wording(retriever, incidents, second, w) for w in WORDINGS}
        merge(results, extra)
        experiments += second
    selected = pick(experiments, results)
    meta = {
        "date": datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        "incidents": len(incidents),
        "documents": len(documents),
        "chunks": len(chunks),
        "embedder": embedder.model_name,
        "reranker": reranker.model_name if reranker else "none",
        "sanity": sanity_check(results),
    }
    report = render(meta, experiments, results, selected)
    payload = {
        "meta": meta,
        "experiments": [
            {"name": e.name, "mode": e.mode, "config": asdict(e.config)} for e in experiments
        ],
        "results": results,
        "selected": {
            "name": selected.name,
            "mode": selected.mode,
            "config": asdict(selected.config),
            "rule": RULE,
        },
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "ablation_dev.md").write_text(report)
    (REPORT_DIR / "ablation_dev.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(report)
    print("saved to evals/reports/ablation_dev.md and .json")


if __name__ == "__main__":
    main()
