from pathlib import Path

from rag.models import Document


def _parse_list(value: str) -> list[str]:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_document(path: Path) -> Document:
    lines = path.read_text().splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{path}: missing front matter")
    end = lines.index("---", 1)
    meta: dict[str, str] = {}
    for line in lines[1:end]:
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    body = "\n".join(lines[end + 1 :]).strip()
    return Document(
        doc_id=meta["id"],
        doc_type=meta["type"],
        title=meta["title"],
        services=_parse_list(meta.get("services", "")),
        tags=_parse_list(meta.get("tags", "")),
        body=body,
        source=path.as_posix(),
    )


def load_documents(kb_dir: Path) -> list[Document]:
    paths = sorted(p for p in kb_dir.rglob("*.md") if p.name != "README.md")
    return [parse_document(p) for p in paths]
