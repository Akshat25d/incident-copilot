import zlib
from pathlib import Path

import pytest

from rag.chunking import chunk_document
from rag.ingest import ingest
from rag.loader import load_documents
from rag.retriever import MODES, HybridRetriever, rrf_fuse, tokenize
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
    def score(self, query: str, texts: list[str]) -> list[float]:
        words = set(query.lower().split())
        return [float(sum(1 for word in words if word in text.lower())) for text in texts]


def build(reranker=None) -> HybridRetriever:
    chunks = [chunk for doc in load_documents(KB) for chunk in chunk_document(doc)]
    embedder = FakeEmbedder()
    store = QdrantStore(url=None, collection="test_retrieval")
    ingest(KB, store, embedder)
    return HybridRetriever(chunks, embedder, store, reranker)


def test_tokenizer_splits_camel_case_and_underscores():
    assert tokenize("HighErrorRate KeyError") == ["high", "error", "rate", "key", "error"]
    assert tokenize("process_resident_memory_bytes") == ["process", "resident", "memory", "bytes"]


def test_rrf_prefers_items_ranked_well_in_both_lists():
    fused = rrf_fuse([["a", "b", "c"], ["b", "a", "d"]])
    assert {item for item, _ in fused[:2]} == {"a", "b"}


def test_rrf_rewards_agreement_between_lists():
    fused = rrf_fuse([["a", "b"], ["c", "b"]])
    assert fused[0][0] == "b"


def test_bm25_finds_exact_terms():
    retriever = build()
    hits = retriever.search("KeyError unhandled exception stack trace", mode="bm25", k=5)
    assert {hit["doc_id"] for hit in hits} & {"RB-001", "PM-001", "SD-004"}


def test_every_mode_returns_cited_results():
    retriever = build(FakeReranker())
    for mode in MODES:
        hits = retriever.search("connection pool timeout", mode=mode, k=3)
        assert 0 < len(hits) <= 3
        for hit in hits:
            assert hit["doc_id"] in hit["citation"]
            assert hit["section"] in hit["citation"]
        scores = [hit["score"] for hit in hits]
        assert scores == sorted(scores, reverse=True)


def test_rerank_mode_requires_a_reranker():
    retriever = build()
    with pytest.raises(ValueError):
        retriever.search("anything", mode="hybrid_rerank")
