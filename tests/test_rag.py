import zlib
from pathlib import Path

from rag.chunking import chunk_document, split_long, split_sections
from rag.ingest import ingest
from rag.loader import load_documents, parse_document
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


def test_loader_reads_every_document():
    docs = load_documents(KB)
    ids = [doc.doc_id for doc in docs]
    assert len(docs) >= 30
    assert len(ids) == len(set(ids))


def test_runbook_sections_follow_headings():
    doc = parse_document(next(KB.glob("runbooks/RB-001-*.md")))
    headings = [heading for heading, _ in split_sections(doc.body)]
    assert headings[:2] == ["Symptoms", "How to confirm"]


def test_chunks_carry_context_and_stay_small():
    chunks = [c for doc in load_documents(KB) for c in chunk_document(doc)]
    assert len(chunks) >= 100
    assert len({c.chunk_id for c in chunks}) == len(chunks)
    for chunk in chunks:
        assert len(chunk.text) <= 1200
        assert chunk.doc_id in chunk.embed_text
        assert chunk.section in chunk.embed_text


def test_long_sections_are_split_without_losing_text():
    text = "\n".join(f"- item {i} " + "x" * 80 for i in range(40))
    pieces = split_long(text, max_chars=500)
    assert len(pieces) > 1
    assert all(len(piece) <= 500 for piece in pieces)
    assert "\n".join(pieces) == text


def test_ingest_and_search_in_memory():
    store = QdrantStore(url=None, collection="test_kb")
    result = ingest(KB, store, FakeEmbedder())
    assert result["documents"] >= 30
    assert result["stored"] == result["chunks"]
    query = FakeEmbedder().embed(["connection pool exhausted database timeout"])[0]
    hits = store.search(query, limit=10)
    assert any(hit["doc_id"] in {"RB-002", "PM-003", "PM-004"} for hit in hits)
