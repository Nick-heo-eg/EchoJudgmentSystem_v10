from typing import List
from .registry import MetricResult


def format_table(results: List[MetricResult]) -> str:
    lines = []
    lines.append(
        "┌───────────────────────────────┬────────┬────────┬──────────────────────────┐"
    )
    lines.append(
        "│ Metric                        │ Score  │ Max    │ Summary                  │"
    )
    lines.append(
        "├───────────────────────────────┼────────┼────────┼──────────────────────────┤"
    )
    for r in results:
        lines.append(
            f"│ {r.key:<29} │ {r.score:>5.2f} │ {r.max_score:>5.2f} │ {r.summary[:24]:<24} │"
        )
    lines.append(
        "└───────────────────────────────┴────────┴────────┴──────────────────────────┘"
    )
    return "\n".join(lines)


def weighted_total(results: List[MetricResult], weights: dict) -> float:
    # weights dict: {key: weight_in_points}, sum(weights)=target cap (e.g., 100)
    total = 0.0
    for r in results:
        w = weights.get(r.key, 0.0)
        # r.score is already scaled to r.max_score; we use proportion of max * weight
        proportion = (r.score / r.max_score) if r.max_score > 0 else 0.0
        total += proportion * w
    return round(total, 2)
