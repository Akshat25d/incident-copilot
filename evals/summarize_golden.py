from collections import Counter
from pathlib import Path

from evals.golden import load_golden
from rag.loader import load_documents


def main() -> None:
    incidents = load_golden()
    known = {doc.doc_id for doc in load_documents(Path("knowledge_base"))}
    referenced = {
        doc_id
        for incident in incidents
        for doc_id in incident.expected_docs + incident.also_relevant + incident.distractors
    }
    print(f"incidents: {len(incidents)}")
    print("by split:", dict(Counter(i.split for i in incidents)))
    print("by difficulty:", dict(Counter(i.difficulty for i in incidents)))
    print("by fault:", dict(Counter(i.fault for i in incidents)))
    print("scripted:", sum(1 for i in incidents if i.scenario.type == "scripted"))
    print("unanswerable:", sum(1 for i in incidents if not i.answerable))
    print("unknown doc ids:", sorted(referenced - known) or "none")


if __name__ == "__main__":
    main()
