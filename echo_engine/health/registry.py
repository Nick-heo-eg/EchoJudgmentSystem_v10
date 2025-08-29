from dataclasses import dataclass
from typing import Callable, Dict, List, Optional


@dataclass
class MetricResult:
    key: str
    score: float
    max_score: float
    summary: str
    details: Optional[dict] = None


@dataclass
class MetricSpec:
    key: str
    weight: float
    runner: Callable[[], MetricResult]  # no-arg closure for lazy deps


class MetricRegistry:
    def __init__(self):
        self._items: Dict[str, MetricSpec] = {}

    def register(self, spec: MetricSpec):
        self._items[spec.key] = spec

    def keys(self) -> List[str]:
        return list(self._items.keys())

    def get(self, key: str) -> MetricSpec:
        return self._items[key]
