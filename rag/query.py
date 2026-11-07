import argparse

from rag.embeddings import FastEmbedEmbedder
from rag.store import QdrantStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Search the indexed knowledge base")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--qdrant-url", default="http://localhost:6333")
    parser.add_argument("--collection", default="incident_kb")
    args = parser.parse_args()

    embedder = FastEmbedEmbedder()
    store = QdrantStore(url=args.qdrant_url, collection=args.collection)
    vector = embedder.embed([args.query])[0]
    for rank, hit in enumerate(store.search(vector, limit=args.limit), start=1):
        print(f"{rank}. {hit['score']:.3f}  {hit['chunk_id']}  ({hit['title']})")


if __name__ == "__main__":
    main()
