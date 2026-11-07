from pathlib import Path
from typing import Protocol

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"
CACHE_DIR = Path(".cache/fastembed")


class Embedder(Protocol):
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class FastEmbedEmbedder:
    def __init__(self, model_name: str = DEFAULT_MODEL, cache_dir: Path = CACHE_DIR):
        from fastembed import TextEmbedding

        cache_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name
        self._model = TextEmbedding(model_name=model_name, cache_dir=str(cache_dir))
        self.dim = len(next(iter(self._model.embed(["dimension probe"]))))

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.embed(texts)]
