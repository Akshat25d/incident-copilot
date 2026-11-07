import argparse
import time
from pathlib import Path

from rag.chunking import chunk_document
from rag.embeddings import FastEmbedEmbedder
from rag.loader import load_documents
from rag.rerank import FastEmbedReranker
from rag.retriever import MODES, HybridRetriever
from rag.store import QdrantStore


def build_retriever(
    kb: str, qdrant_url: str, collection: str, use_reranker: bool
) -> HybridRetriever:
    chunks = [chunk for doc in load_documents(Path(kb)) for chunk in chunk_document(doc)]
    reranker = FastEmbedReranker() if use_reranker else None
    return HybridRetriever(
        chunks,
        FastEmbedEmbedder(),
        QdrantStore(url=qdrant_url, collection=collection),
        reranker,
    )


def show(retriever: HybridRetriever, query: str, mode: str, k: int, candidates: int) -> None:
    started = time.perf_counter()
    hits = retriever.search(query, mode=mode, k=k, candidates=candidates)
    elapsed = time.perf_counter() - started
    print(f"[{mode}]  {elapsed:.2f}s")
    for hit in hits:
        print(f"  {hit['rank']}. {hit['score']:.3f}  {hit['citation']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Search the indexed knowledge base")
    parser.add_argument("query")
    parser.add_argument("--mode", choices=MODES, default="hybrid_rerank")
    parser.add_argument("--all-modes", action="store_true")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--candidates", type=int, default=20)
    parser.add_argument("--kb", default="knowledge_base")
    parser.add_argument("--qdrant-url", default="http://localhost:6333")
    parser.add_argument("--collection", default="incident_kb")
    args = parser.parse_args()

    modes = MODES if args.all_modes else (args.mode,)
    retriever = build_retriever(
        args.kb, args.qdrant_url, args.collection, use_reranker="hybrid_rerank" in modes
    )
    print(f'query: "{args.query}"')
    for mode in modes:
        show(retriever, args.query, mode, args.limit, args.candidates)


if __name__ == "__main__":
    main()
