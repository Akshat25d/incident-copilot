import argparse
import time
from collections import Counter
from pathlib import Path

from rag.chunking import chunk_document
from rag.embeddings import Embedder, FastEmbedEmbedder
from rag.loader import load_documents
from rag.store import QdrantStore, VectorStore


def ingest(kb_dir: Path, store: VectorStore, embedder: Embedder) -> dict:
    documents = load_documents(kb_dir)
    chunks = [chunk for doc in documents for chunk in chunk_document(doc)]
    vectors = embedder.embed([chunk.embed_text for chunk in chunks])
    store.recreate(embedder.dim)
    store.upsert(chunks, vectors)
    return {
        "documents": len(documents),
        "chunks": len(chunks),
        "by_type": dict(Counter(chunk.doc_type for chunk in chunks)),
        "stored": store.count(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Index the knowledge base into Qdrant")
    parser.add_argument("--kb", default="knowledge_base")
    parser.add_argument("--qdrant-url", default="http://localhost:6333")
    parser.add_argument("--collection", default="incident_kb")
    args = parser.parse_args()

    started = time.perf_counter()
    embedder = FastEmbedEmbedder()
    store = QdrantStore(url=args.qdrant_url, collection=args.collection)
    result = ingest(Path(args.kb), store, embedder)
    elapsed = time.perf_counter() - started
    print(
        f"indexed {result['documents']} documents into {result['chunks']} chunks "
        f"({result['stored']} stored)"
    )
    print(f"by type: {result['by_type']}")
    print(f"embedding model: {embedder.model_name} (dim {embedder.dim}), took {elapsed:.1f}s")


if __name__ == "__main__":
    main()
