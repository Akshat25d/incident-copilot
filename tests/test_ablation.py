import zlib
from pathlib import Path

from evals.ablation import Experiment, pick, run_wording, stage_one
from evals.golden import load_golden
from rag.chunking import chunk_document
from rag.ingest import ingest
from rag.loader import load_documents
from rag.retriever import HybridRetriever, RetrievalConfig
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


def make_results(values: dict[str, float]) -> dict:
    aggregate = {name: {"mrr": mrr} for name, mrr in values.items()}
    return {"original": {"aggregate": aggregate}, "paraphrase": {"aggregate": aggregate}}


def test_pick_prefers_simpler_config_within_margin():
    experiments = [
        Experiment("bm25", "bm25", RetrievalConfig()),
        Experiment("rerank", "hybrid_rerank", RetrievalConfig()),
    ]
    results = make_results({"bm25": 0.80, "rerank": 0.82})
    assert pick(experiments, results).name == "bm25"


def test_pick_takes_clear_winner_beyond_margin():
    experiments = [
        Experiment("bm25", "bm25", RetrievalConfig()),
        Experiment("rerank", "hybrid_rerank", RetrievalConfig()),
    ]
    results = make_results({"bm25": 0.70, "rerank": 0.80})
    assert pick(experiments, results).name == "rerank"


def test_complexity_orders_bm25_before_reranker():
    plain = Experiment("a", "bm25", RetrievalConfig())
    rerank = Experiment("b", "hybrid_rerank", RetrievalConfig())
    assert plain.complexity() < rerank.complexity()


def test_run_wording_covers_every_dev_incident():
    chunks = [chunk for doc in load_documents(KB) for chunk in chunk_document(doc)]
    embedder = FakeEmbedder()
    store = QdrantStore(url=None, collection="test_ablation")
    ingest(KB, store, embedder)
    retriever = HybridRetriever(chunks, embedder, store, None)
    incidents = [i for i in load_golden() if i.split == "dev" and i.answerable]
    experiments = [e for e in stage_one() if e.mode in ("bm25", "hybrid")][:3]
    for wording in ("original", "paraphrase"):
        result = run_wording(retriever, incidents, experiments, wording)
        assert len(result["rows"]) == len(incidents) == 15
        assert set(result["aggregate"]) == {e.name for e in experiments}


def test_pick_breaks_complexity_ties_by_paraphrase_mrr():
    experiments = [
        Experiment("a", "hybrid", RetrievalConfig(dense_weight=0.0, runbook_boost=1.25)),
        Experiment("b", "hybrid", RetrievalConfig(dense_weight=0.25, runbook_boost=1.25)),
    ]
    results = {
        "original": {"aggregate": {"a": {"mrr": 1.0}, "b": {"mrr": 0.97}}},
        "paraphrase": {"aggregate": {"a": {"mrr": 0.73}, "b": {"mrr": 0.79}}},
    }
    assert experiments[0].complexity() == experiments[1].complexity()
    assert pick(experiments, results).name == "b"
