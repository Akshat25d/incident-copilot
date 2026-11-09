from evals import metrics


def test_doc_ranking_dedupes_in_order():
    hits = [{"doc_id": "A"}, {"doc_id": "B"}, {"doc_id": "A"}, {"doc_id": "C"}]
    assert metrics.to_doc_ranking(hits) == ["A", "B", "C"]


def test_doc_ranking_respects_limit():
    hits = [{"doc_id": f"D{i}"} for i in range(20)]
    assert len(metrics.to_doc_ranking(hits, limit=10)) == 10


def test_first_rank_and_hit_at():
    ranking = ["X", "Y", "RB-001", "Z"]
    assert metrics.first_rank(ranking, ["RB-001"]) == 3
    assert metrics.first_rank(ranking, ["NOPE"]) is None
    assert metrics.hit_at(ranking, ["RB-001"], 1) == 0.0
    assert metrics.hit_at(ranking, ["RB-001"], 3) == 1.0


def test_recall_with_two_expected_documents():
    ranking = ["RB-005", "X", "Y", "Z", "RB-003"]
    assert metrics.recall_at(ranking, ["RB-005", "RB-003"], 3) == 0.5
    assert metrics.recall_at(ranking, ["RB-005", "RB-003"], 5) == 1.0


def test_reciprocal_rank():
    assert metrics.reciprocal_rank(["A", "B", "C"], ["C"]) == 1 / 3
    assert metrics.reciprocal_rank(["A"], ["Z"]) == 0.0


def test_distractor_outranks():
    assert metrics.distractor_outranks(["D", "A"], ["A"], ["D"]) is True
    assert metrics.distractor_outranks(["A", "D"], ["A"], ["D"]) is False
    assert metrics.distractor_outranks(["D"], ["A"], ["D"]) is True
    assert metrics.distractor_outranks(["X"], ["A"], ["D"]) is False
    assert metrics.distractor_outranks(["A"], ["A"], []) is None
