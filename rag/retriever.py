import re

from rank_bm25 import BM25Okapi

from rag.embeddings import Embedder
from rag.models import Chunk
from rag.rerank import Reranker
from rag.store import VectorStore

MODES = ("dense", "bm25", "hybrid", "hybrid_rerank")


def tokenize(text: str) -> list[str]:
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text)
    return re.findall(r"[a-z0-9]+", spaced.lower())


def rrf_fuse(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda pair: pair[1], reverse=True)


def format_citation(hit: dict) -> str:
    return f"[{hit['doc_id']}] {hit['title']} > {hit['section']} ({hit['source']})"


def chunk_to_hit(chunk: Chunk) -> dict:
    return {
        "chunk_id": chunk.chunk_id,
        "doc_id": chunk.doc_id,
        "doc_type": chunk.doc_type,
        "title": chunk.title,
        "section": chunk.section,
        "services": chunk.services,
        "tags": chunk.tags,
        "source": chunk.source,
        "text": chunk.text,
    }


class HybridRetriever:
    def __init__(
        self,
        chunks: list[Chunk],
        embedder: Embedder,
        store: VectorStore,
        reranker: Reranker | None = None,
        rrf_k: int = 60,
    ):
        self.chunks = {chunk.chunk_id: chunk for chunk in chunks}
        self._ids = [chunk.chunk_id for chunk in chunks]
        self.embedder = embedder
        self.store = store
        self.reranker = reranker
        self.rrf_k = rrf_k
        self._bm25 = BM25Okapi([tokenize(chunk.embed_text) for chunk in chunks])

    def _dense_pairs(self, query: str, n: int) -> list[tuple[str, float]]:
        vector = self.embedder.embed([query])[0]
        return [
            (hit["chunk_id"], float(hit["score"])) for hit in self.store.search(vector, limit=n)
        ]

    def _bm25_pairs(self, query: str, n: int) -> list[tuple[str, float]]:
        scores = self._bm25.get_scores(tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [(self._ids[i], float(scores[i])) for i in order[:n] if scores[i] > 0]

    def search(
        self, query: str, mode: str = "hybrid_rerank", k: int = 5, candidates: int = 20
    ) -> list[dict]:
        if mode not in MODES:
            raise ValueError(f"unknown mode {mode!r}, expected one of {MODES}")
        if mode == "dense":
            pairs = self._dense_pairs(query, k)
        elif mode == "bm25":
            pairs = self._bm25_pairs(query, k)
        else:
            dense_ids = [cid for cid, _ in self._dense_pairs(query, candidates)]
            bm25_ids = [cid for cid, _ in self._bm25_pairs(query, candidates)]
            fused = rrf_fuse([dense_ids, bm25_ids], self.rrf_k)
            if mode == "hybrid":
                pairs = fused[:k]
            else:
                if self.reranker is None:
                    raise ValueError("hybrid_rerank needs a reranker")
                top = [cid for cid, _ in fused[:candidates]]
                texts = [self.chunks[cid].embed_text for cid in top]
                scores = self.reranker.score(query, texts)
                ranked = sorted(zip(top, scores, strict=True), key=lambda p: p[1], reverse=True)
                pairs = ranked[:k]
        results = []
        for rank, (chunk_id, score) in enumerate(pairs, start=1):
            hit = chunk_to_hit(self.chunks[chunk_id])
            hit.update(rank=rank, score=float(score), mode=mode, citation=format_citation(hit))
            results.append(hit)
        return results
