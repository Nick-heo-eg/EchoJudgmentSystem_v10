
#!/usr/bin/env python3
import argparse, json, os, sys, math
from typing import Dict, Any

try:
    import yaml  # type: ignore
except Exception:
    print("Please install pyyaml: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def key_of(rec: Dict[str, Any]) -> str:
    return f"{rec['concurrency']}x{rec['total_requests']}"

def to_map(rows):
    return { key_of(r): r for r in rows }

def compare(current: Dict[str, Any], baseline: Dict[str, Any], reference: Dict[str, Any] | None, guards: Dict[str, float] | None):
    cur_map = to_map(current["results"])
    failures = []
    notes = []

    th = baseline.get("thresholds", {})
    for k, v in cur_map.items():
        thr = th.get(k, {})
        min_rps = thr.get("min_rps")
        max_p95 = thr.get("max_p95_ms")
        rps = v["rps"]
        p95 = v["p95_ms"]

        if min_rps is not None and rps < float(min_rps):
            failures.append(f"{k}: RPS {rps:.1f} < min {min_rps}")
        if max_p95 is not None and p95 > float(max_p95):
            failures.append(f"{k}: p95 {p95:.1f}ms > max {max_p95}ms")

    if reference and guards:
        ref_map = to_map(reference["results"])
        max_drop = float(guards.get("max_rps_drop_pct", 0.0))
        max_p95_inc = float(guards.get("max_p95_increase_pct", 0.0))
        for k, v in cur_map.items():
            ref = ref_map.get(k)
            if not ref:
                continue
            rps_drop_pct = ((ref["rps"] - v["rps"]) / ref["rps"]) * 100.0 if ref["rps"] > 0 else 0.0
            p95_inc_pct = ((v["p95_ms"] - ref["p95_ms"]) / ref["p95_ms"]) * 100.0 if ref["p95_ms"] > 0 else 0.0
            notes.append(f"{k}: ΔRPS={-rps_drop_pct:.2f}% Δp95={p95_inc_pct:.2f}% vs reference")
            if rps_drop_pct > max_drop:
                failures.append(f"{k}: RPS drop {rps_drop_pct:.2f}% > {max_drop}% guard")
            if p95_inc_pct > max_p95_inc:
                failures.append(f"{k}: p95 increase {p95_inc_pct:.2f}% > {max_p95_inc}% guard")

    summary = {
        "meta": current.get("meta", {}),
        "failures": failures,
        "notes": notes,
        "ok": len(failures) == 0
    }
    return summary

def main():
    ap = argparse.ArgumentParser(description="Check bench results against baseline thresholds")
    ap.add_argument("results_json", help="Path to artifacts/.../results.json")
    ap.add_argument("--baseline", default="tests/agent_hub/bench_baseline.yaml")
    ap.add_argument("--reference", default="", help="Optional reference results.json to compare against")
    ap.add_argument("--out", default="", help="Optional path to write summary.json")
    ap.add_argument("--fail-on-violation", action="store_true")
    args = ap.parse_args()

    current = load_json(args.results_json)
    baseline = load_yaml(args.baseline)
    reference = load_json(args.reference) if args.reference else None
    guards = baseline.get("guards", {}) if baseline else {}

    summary = compare(current, baseline, reference, guards)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

    if args.fail_on_violation and not summary["ok"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
