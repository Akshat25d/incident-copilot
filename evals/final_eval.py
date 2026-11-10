import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from evals.ablation import HEADER, SEPARATOR, Experiment, run_wording, table_row
from evals.golden import load_golden
from rag.chunking import chunk_document
from rag.embeddings import FastEmbedEmbedder
from rag.loader import load_documents
from rag.rerank import FastEmbedReranker
from rag.retriever import SELECTED_PATH, HybridRetriever, RetrievalConfig
from rag.store import QdrantStore

FINAL_MD = Path("evals/reports/retrieval_test_final.md")
FINAL_JSON = Path("evals/reports/retrieval_test_final.json")


def render(meta: dict, experiments: list[Experiment], result: dict) -> str:
    n = meta["incidents"]
    names = [exp.name for exp in experiments]
    lines = [
        "# Retrieval evaluation: held-out test split (final)",
        "",
        f"- date: {meta['date']}",
        f"- incidents evaluated: {n} (the unanswerable incident is skipped)",
        "- queries: original wording",
        "- evaluated once; configurations were fixed on the dev split beforehand",
        f"- one incident moves a rate by about {100 / n:.0f} points",
        "",
        HEADER,
        SEPARATOR,
    ]
    for exp in experiments:
        lines.append(table_row(exp.name, result["aggregate"][exp.name]))
    lines += [
        "",
        "## Rank of the first correct document",
        "",
        "| ID | Fault | " + " | ".join(names) + " |",
        "|---|---|" + "---|" * len(names),
    ]
    for row in result["rows"]:
        ranks = " | ".join(str(row["modes"][name]["first_rank"] or ">10") for name in names)
        lines.append(f"| {row['id']} | {row['fault']} | {ranks} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="One-time evaluation on the held-out test split")
    parser.add_argument("--final", action="store_true", help="confirm this is the single test run")
    parser.add_argument("--kb", default="knowledge_base")
    parser.add_argument("--qdrant-url", default="http://localhost:6333")
    parser.add_argument("--collection", default="incident_kb")
    args = parser.parse_args()
    if not args.final:
        parser.error("this evaluates the held-out test split once; pass --final to confirm")
    if FINAL_JSON.exists():
        raise SystemExit("the test split was already evaluated; not running it a second time")

    selected = json.loads(SELECTED_PATH.read_text())
    experiments = [
        Experiment("bm25", "bm25", RetrievalConfig()),
        Experiment("D8 baseline: hybrid_rerank", "hybrid_rerank", RetrievalConfig()),
        Experiment(
            f"selected: {selected['name']}",
            selected["mode"],
            RetrievalConfig(**selected["config"]),
        ),
    ]
    incidents = [i for i in load_golden() if i.split == "test" and i.answerable]
    documents = load_documents(Path(args.kb))
    chunks = [chunk for doc in documents for chunk in chunk_document(doc)]
    store = QdrantStore(url=args.qdrant_url, collection=args.collection)
    if store.count() != len(chunks):
        raise SystemExit("index is out of date; run: uv run python -m rag.ingest")
    retriever = HybridRetriever(chunks, FastEmbedEmbedder(), store, FastEmbedReranker())
    for mode in ("dense", "bm25", "hybrid", "hybrid_rerank"):
        retriever.search("warm up", mode=mode, k=3, candidates=3)

    result = run_wording(retriever, incidents, experiments, "original")
    meta = {
        "date": datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        "incidents": len(incidents),
        "selected": selected,
    }
    report = render(meta, experiments, result)
    FINAL_MD.write_text(report)
    FINAL_JSON.write_text(json.dumps({"meta": meta, **result}, indent=2) + "\n")
    print(report)
    print(f"saved to {FINAL_MD} and .json")


if __name__ == "__main__":
    main()
