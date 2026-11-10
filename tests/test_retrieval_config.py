import zlib
from pathlib import Path

from rag.chunking import chunk_document
from rag.ingest import ingest
from rag.loader import load_documents
from rag.retriever import HybridRetriever, RetrievalConfig, rrf_fuse
from rag.store import QdrantStore

KB = Path(__file__).resolve().parent.parent / "knowledge_base"
QUERY = "connection pool timeout orders database"


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
    store = QdrantStore(url=None, collection="test_config")
    ingest(KB, store, embedder)
    return HybridRetriever(chunks, embedder, store, FakeReranker())


def test_rrf_weights_change_the_winner():
    rankings = [["a", "b"], ["b", "a"]]
    assert rrf_fuse(rankings, weights=[1.0, 0.5])[0][0] == "a"
    assert rrf_fuse(rankings, weights=[0.5, 1.0])[0][0] == "b"


def test_rrf_zero_weight_ignores_a_list():
    fused = rrf_fuse([["a"], ["b"]], weights=[0.0, 1.0])
    assert fused[0][0] == "b"
    assert dict(fused)["a"] == 0.0


def test_runbook_boost_puts_runbooks_first():
    hits = build().search(QUERY, mode="hybrid", k=5, config=RetrievalConfig(runbook_boost=1000.0))
    assert hits[0]["doc_type"] == "runbook"


def test_default_config_matches_legacy_arguments():
    retriever = build()
    legacy = retriever.search(QUERY, mode="hybrid", k=5)
    explicit = retriever.search(
        QUERY, mode="hybrid", k=5, config=RetrievalConfig(list_depth=20, pool=20)
    )
    assert [h["chunk_id"] for h in legacy] == [h["chunk_id"] for h in explicit]


def test_pool_limits_reranker_candidates():
    retriever = build()
    config = RetrievalConfig(pool=3)
    fused = retriever.search(QUERY, mode="hybrid", k=3, config=config)
    reranked = retriever.search(QUERY, mode="hybrid_rerank", k=3, config=config)
    assert {h["chunk_id"] for h in fused} == {h["chunk_id"] for h in reranked}
