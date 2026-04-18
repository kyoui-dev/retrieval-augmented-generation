from typing import Any

from sentence_transformers import CrossEncoder


def rerank(
    query: str,
    results: list[dict[str, Any]],
    cross_encoder: CrossEncoder,
    top_n: int = 5,
) -> list[dict[str, Any]]:
    pairs = [(query, item["content"]) for item in results]
    scores = cross_encoder.predict(pairs)
    reranked = [
        {**item, "score": float(score)}
        for item, score in zip(results, scores)
    ]
    return sorted(reranked, key=lambda x: x["score"], reverse=True)[:top_n]