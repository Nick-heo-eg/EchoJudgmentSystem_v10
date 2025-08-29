import json
from pathlib import Path
import yaml
from typing import List
from .registry import MetricRegistry, MetricSpec, MetricResult
from .report import format_table, weighted_total


def load_config(cfg_path: str) -> dict:
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_health(registry: MetricRegistry, include: List[str], weights: dict) -> dict:
    results: List[MetricResult] = []
    for key in include:
        spec = registry.get(key)
        res = spec.runner()
        results.append(res)
    table = format_table(results)
    total = weighted_total(results, weights)
    return {
        "results": [res.__dict__ for res in results],
        "table": table,
        "total": total,
    }


def save_json(report: dict, out_path: str):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
