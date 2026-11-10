import json
import re
from dataclasses import dataclass
from pathlib import Path

from rank_bm25 import BM25Okapi

from rag.embeddings import Embedder
from rag.models import Chunk
from rag.rerank import Reranker
from rag.store import VectorStore

MODES = ("dense", "bm25", "hybrid", "hybrid_rerank")
SELECTED_PATH = Path(__file__).resolve().parent / "selected_config.json"


@dataclass(frozen=True)
class RetrievalConfig:
    dense_weight: float = 1.0
    bm25_weight: float = 1.0
    rrf_k: int = 60
    runbook_boost: float = 1.0
    list_depth: int = 30
    pool: int = 30


def load_selected() -> tuple[str, RetrievalConfig]:
    data = json.loads(SELECTED_PATH.read_text())
    return data["mode"], RetrievalConfig(**data["config"])


def tokenize(text: str) -> list[str]:
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text)
    return re.findall(r"[a-z0-9]+", spaced.lower())


def rrf_fuse(
    rankings: list[list[str]], k: int = 60, weights: list[float] | None = None
) -> list[tuple[str, float]]:
    weights = weights or [1.0] * len(rankings)
    scores: dict[str, float] = {}
    for ranking, weight in zip(rankings, weights, strict=True):
        for rank, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0.0) + weight / (k + rank)
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

    def _apply_boost(self, fused: list[tuple[str, float]], boost: float) -> list[tuple[str, float]]:
        if boost == 1.0:
            return fused
        boosted = [
            (cid, score * boost if self.chunks[cid].doc_type == "runbook" else score)
            for cid, score in fused
        ]
        return sorted(boosted, key=lambda pair: pair[1], reverse=True)

    def search(
        self,
        query: str,
        mode: str = "hybrid_rerank",
        k: int = 5,
        candidates: int = 20,
        config: RetrievalConfig | None = None,
    ) -> list[dict]:
        if mode not in MODES:
            raise ValueError(f"unknown mode {mode!r}, expected one of {MODES}")
        cfg = config or RetrievalConfig(rrf_k=self.rrf_k, list_depth=candidates, pool=candidates)
        if mode == "dense":
            pairs = self._dense_pairs(query, k)
        elif mode == "bm25":
            pairs = self._bm25_pairs(query, k)
        else:
            dense_ids = [cid for cid, _ in self._dense_pairs(query, cfg.list_depth)]
            bm25_ids = [cid for cid, _ in self._bm25_pairs(query, cfg.list_depth)]
            weights = [cfg.dense_weight, cfg.bm25_weight]
            fused = rrf_fuse([dense_ids, bm25_ids], cfg.rrf_k, weights)
            fused = self._apply_boost(fused, cfg.runbook_boost)
            if mode == "hybrid":
                pairs = fused[:k]
            else:
                if self.reranker is None:
                    raise ValueError("hybrid_rerank needs a reranker")
                top = [cid for cid, _ in fused[: cfg.pool]]
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
