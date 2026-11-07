import uuid
from typing import Protocol

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from rag.models import Chunk


class VectorStore(Protocol):
    def recreate(self, dim: int) -> None: ...

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None: ...

    def search(self, vector: list[float], limit: int = 5) -> list[dict]: ...

    def count(self) -> int: ...


def point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


class QdrantStore:
    def __init__(self, url: str | None = None, collection: str = "incident_kb"):
        self.collection = collection
        self.client = QdrantClient(url=url) if url else QdrantClient(":memory:")

    def recreate(self, dim: int) -> None:
        if self.client.collection_exists(self.collection):
            self.client.delete_collection(self.collection)
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        points = [
            PointStruct(
                id=point_id(chunk.chunk_id),
                vector=vector,
                payload={
                    "chunk_id": chunk.chunk_id,
                    "doc_id": chunk.doc_id,
                    "doc_type": chunk.doc_type,
                    "title": chunk.title,
                    "section": chunk.section,
                    "services": chunk.services,
                    "tags": chunk.tags,
                    "source": chunk.source,
                    "text": chunk.text,
                },
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, vector: list[float], limit: int = 5) -> list[dict]:
        response = self.client.query_points(
            collection_name=self.collection,
            query=vector,
            limit=limit,
            with_payload=True,
        )
        return [{"score": point.score, **(point.payload or {})} for point in response.points]

    def count(self) -> int:
        return self.client.count(collection_name=self.collection, exact=True).count
