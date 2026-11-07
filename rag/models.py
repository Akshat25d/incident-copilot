from dataclasses import dataclass


@dataclass
class Document:
    doc_id: str
    doc_type: str
    title: str
    services: list[str]
    tags: list[str]
    body: str
    source: str


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    doc_type: str
    title: str
    section: str
    services: list[str]
    tags: list[str]
    source: str
    text: str
    embed_text: str
