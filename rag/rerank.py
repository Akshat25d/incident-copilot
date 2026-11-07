import os
from pathlib import Path
from typing import Protocol

DEFAULT_RERANKER = "BAAI/bge-reranker-base"
CACHE_DIR = Path(".cache/fastembed")


class Reranker(Protocol):
    def score(self, query: str, texts: list[str]) -> list[float]: ...


class FastEmbedReranker:
    def __init__(self, model_name: str | None = None, cache_dir: Path = CACHE_DIR):
        from fastembed.rerank.cross_encoder import TextCrossEncoder

        cache_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name or os.getenv("RERANKER_MODEL", DEFAULT_RERANKER)
        self._model = TextCrossEncoder(model_name=self.model_name, cache_dir=str(cache_dir))

    def score(self, query: str, texts: list[str]) -> list[float]:
        return [float(score) for score in self._model.rerank(query, texts)]
