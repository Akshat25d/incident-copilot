from pathlib import Path

KB = Path(__file__).resolve().parent.parent / "knowledge_base"
REQUIRED = {"id", "type", "title", "services", "tags"}


def parse(path: Path) -> dict[str, str]:
    lines = path.read_text().splitlines()
    assert lines[0] == "---", f"{path.name} must start with front matter"
    end = lines.index("---", 1)
    meta = {}
    for line in lines[1:end]:
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta


def kb_files() -> list[Path]:
    return sorted(p for p in KB.rglob("*.md") if p.name != "README.md")


def test_every_document_has_required_metadata():
    for path in kb_files():
        missing = REQUIRED - parse(path).keys()
        assert not missing, f"{path.name} is missing {missing}"


def test_ids_are_unique_and_match_filenames():
    seen = set()
    for path in kb_files():
        doc_id = parse(path)["id"]
        assert doc_id not in seen, f"duplicate id {doc_id}"
        seen.add(doc_id)
        assert path.name.startswith(doc_id), f"{path.name} should start with {doc_id}"


def test_expected_document_counts():
    types = [parse(p)["type"] for p in kb_files()]
    assert types.count("runbook") >= 10
    assert types.count("service_doc") >= 6
    assert types.count("postmortem") >= 14
