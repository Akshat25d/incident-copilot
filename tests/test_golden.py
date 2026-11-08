from collections import Counter, defaultdict
from pathlib import Path

from evals.golden import load_golden
from rag.loader import load_documents

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "knowledge_base"
FAULT_SCRIPT = ROOT / "demo_app" / "faults.sh"


def test_golden_set_shape():
    incidents = load_golden()
    assert [i.id for i in incidents] == [f"G-{n:03d}" for n in range(1, 26)]
    assert Counter(i.split for i in incidents) == {"dev": 15, "test": 10}


def test_each_scripted_fault_has_two_dev_and_one_test():
    by_fault = defaultdict(list)
    for incident in load_golden():
        if incident.scenario.type == "scripted":
            by_fault[incident.fault].append(incident.split)
    assert len(by_fault) == 6
    for fault, splits in by_fault.items():
        assert Counter(splits) == {"dev": 2, "test": 1}, fault


def test_referenced_documents_exist():
    known = {doc.doc_id for doc in load_documents(KB)}
    for incident in load_golden():
        referenced = set(incident.expected_docs + incident.also_relevant + incident.distractors)
        assert referenced <= known, f"{incident.id}: unknown {referenced - known}"


def test_scripted_commands_exist_in_fault_script():
    script = FAULT_SCRIPT.read_text()
    for incident in load_golden():
        if incident.scenario.type == "scripted":
            assert f"{incident.scenario.command})" in script, incident.id


def test_expected_docs_are_never_distractors():
    for incident in load_golden():
        assert not set(incident.expected_docs) & set(incident.distractors), incident.id
        assert not set(incident.expected_docs) & set(incident.also_relevant), incident.id


def test_queries_are_unique_and_long_enough():
    queries = [i.query for i in load_golden()]
    assert len(set(queries)) == len(queries)
    assert all(len(query.split()) >= 8 for query in queries)


def test_unanswerable_incident_is_marked_and_empty():
    unanswerable = [i for i in load_golden() if not i.answerable]
    assert [i.id for i in unanswerable] == ["G-025"]
    assert unanswerable[0].expected_docs == []
