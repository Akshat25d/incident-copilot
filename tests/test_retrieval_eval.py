import zlib
from pathlib import Path

from evals.golden import load_golden
from evals.retrieval_eval import evaluate, render_report
from rag.chunking import chunk_document
from rag.ingest import ingest
from rag.loader import load_documents
from rag.retriever import MODES, HybridRetriever
from rag.store import QdrantStore

KB = Path(__file__).resolve().parent.parent / "knowledge_base"


class FakeEmbedder:
    dim = 64
    model_name = "fake"

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            vector = [0.0] * self.dim
            for word in text.lower().split():
                vector[zlib.crc32(word.encode()) % self.dim] += 1.0
            vectors.append(vector)
        return vectors


class FakeReranker:
    model_name = "fake"

    def score(self, query: str, texts: list[str]) -> list[float]:
        words = set(query.lower().split())
        return [float(sum(1 for word in words if word in text.lower())) for text in texts]


def build() -> HybridRetriever:
    chunks = [chunk for doc in load_documents(KB) for chunk in chunk_document(doc)]
    embedder = FakeEmbedder()
    store = QdrantStore(url=None, collection="test_eval")
    ingest(KB, store, embedder)
    return HybridRetriever(chunks, embedder, store, FakeReranker())


def dev_incidents():
    return [i for i in load_golden() if i.split == "dev" and i.answerable]


def test_evaluate_produces_metrics_for_every_mode():
    incidents = dev_incidents()
    result = evaluate(build(), incidents, list(MODES), depth=15)
    assert len(result["rows"]) == len(incidents) == 15
    for mode in MODES:
        agg = result["aggregate"][mode]
        assert agg["n"] == 15
        assert 0.0 <= agg["mrr"] <= 1.0
        assert 0 <= agg["top1"] <= agg["hit3"] <= 15


def test_report_lists_every_mode_and_incident():
    result = evaluate(build(), dev_incidents(), list(MODES), depth=15)
    meta = {
        "split": "dev",
        "label": "test",
        "date": "today",
        "incidents": 15,
        "skipped": 0,
        "documents": 30,
        "chunks": 100,
        "embedder": "fake",
        "reranker": "fake",
        "depth": 15,
    }
    report = render_report(meta, result)
    for mode in MODES:
        assert f"| {mode} |" in report
    assert "G-001" in report
