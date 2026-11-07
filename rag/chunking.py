import re

from rag.models import Chunk, Document

MAX_CHARS = 1200


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def split_sections(body: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    heading = "Overview"
    buffer: list[str] = []
    for line in body.splitlines():
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            if "".join(buffer).strip():
                sections.append((heading, "\n".join(buffer).strip()))
            heading = line[3:].strip()
            buffer = []
        else:
            buffer.append(line)
    if "".join(buffer).strip():
        sections.append((heading, "\n".join(buffer).strip()))
    return sections


def split_long(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    pieces: list[str] = []
    current: list[str] = []
    size = 0
    for line in text.splitlines():
        if current and size + len(line) > max_chars:
            pieces.append("\n".join(current))
            current, size = [], 0
        current.append(line)
        size += len(line) + 1
    if current:
        pieces.append("\n".join(current))
    return pieces


def chunk_document(doc: Document) -> list[Chunk]:
    chunks: list[Chunk] = []
    for heading, text in split_sections(doc.body):
        for index, piece in enumerate(split_long(text)):
            header = f"{doc.title} ({doc.doc_id}) - {heading}"
            services = ", ".join(doc.services)
            chunks.append(
                Chunk(
                    chunk_id=f"{doc.doc_id}#{slugify(heading)}-{index}",
                    doc_id=doc.doc_id,
                    doc_type=doc.doc_type,
                    title=doc.title,
                    section=heading,
                    services=doc.services,
                    tags=doc.tags,
                    source=doc.source,
                    text=piece,
                    embed_text=f"{header}\nServices: {services}\n{piece}",
                )
            )
    return chunks
