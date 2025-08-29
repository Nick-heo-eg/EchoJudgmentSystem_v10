import argparse
import json
import os
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from echo_engine.response_runner import answer


def load_scenarios(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            yield json.loads(line)


def rule_based_score(expected: dict, output: str) -> float:
    """Very light scoring: length>min, contains some keywords, no empty."""
    if not output:
        return 0.0
    score = 3.5
    if len(output) > 200:
        score += 0.5
    kws = expected.get("keywords", [])
    hits = sum(1 for k in kws if k in output)
    score += min(1.0, hits * 0.3)
    return min(5.0, score)


def run_eval(scenarios_path: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    results = []
    for sc in load_scenarios(scenarios_path):
        sys_prompt = sc.get("system")
        user = sc["input"]
        out = answer(user, sys_prompt=sys_prompt)
        score = rule_based_score(sc.get("expect", {}), out)
        results.append({"input": user, "output": out, "score": score})

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(out_dir, f"eval_{ts}.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    avg = sum(r["score"] for r in results) / max(1, len(results))
    print(f"Avg score: {avg:.2f} on {len(results)} scenarios.\nSaved → {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", default="tools/evals/scenarios.sample.jsonl")
    ap.add_argument("--out", default="eval_runs")
    args = ap.parse_args()
    run_eval(args.scenarios, args.out)
