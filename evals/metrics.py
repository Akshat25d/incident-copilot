def to_doc_ranking(hits: list[dict], limit: int = 10) -> list[str]:
    ranking: list[str] = []
    for hit in hits:
        doc_id = hit["doc_id"]
        if doc_id not in ranking:
            ranking.append(doc_id)
        if len(ranking) == limit:
            break
    return ranking


def first_rank(ranking: list[str], relevant: list[str]) -> int | None:
    for position, doc_id in enumerate(ranking, start=1):
        if doc_id in relevant:
            return position
    return None


def hit_at(ranking: list[str], relevant: list[str], k: int) -> float:
    return 1.0 if any(doc_id in relevant for doc_id in ranking[:k]) else 0.0


def recall_at(ranking: list[str], relevant: list[str], k: int) -> float:
    return len(set(ranking[:k]) & set(relevant)) / len(relevant)


def reciprocal_rank(ranking: list[str], relevant: list[str]) -> float:
    rank = first_rank(ranking, relevant)
    return 1.0 / rank if rank else 0.0


def distractor_outranks(
    ranking: list[str], relevant: list[str], distractors: list[str]
) -> bool | None:
    if not distractors:
        return None
    distractor_rank = first_rank(ranking, distractors)
    if distractor_rank is None:
        return False
    answer_rank = first_rank(ranking, relevant)
    return answer_rank is None or distractor_rank < answer_rank
