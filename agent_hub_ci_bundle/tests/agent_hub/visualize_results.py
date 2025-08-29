
#!/usr/bin/env python3
import argparse, os, json, csv
from typing import List, Dict
import matplotlib.pyplot as plt

def load_results(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def plot_curves(results_json: str, out_dir: str):
    data = load_results(results_json)
    rows = data["results"]
    xs = [r["concurrency"] for r in rows]
    rps = [r["rps"] for r in rows]
    p50 = [r["p50_ms"] for r in rows]
    p95 = [r["p95_ms"] for r in rows]

    os.makedirs(out_dir, exist_ok=True)

    # RPS curve
    plt.figure()
    plt.plot(xs, rps, marker="o")
    plt.title("RPS vs Concurrency")
    plt.xlabel("Concurrency")
    plt.ylabel("RPS")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.savefig(os.path.join(out_dir, "rps_curve.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # Latency curve
    plt.figure()
    plt.plot(xs, p50, marker="o", label="p50 (ms)")
    plt.plot(xs, p95, marker="o", label="p95 (ms)")
    plt.title("Latency vs Concurrency")
    plt.xlabel("Concurrency")
    plt.ylabel("Latency (ms)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.savefig(os.path.join(out_dir, "latency_curve.png"), dpi=150, bbox_inches="tight")
    plt.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("results_json", help="Path to artifacts/.../results.json")
    ap.add_argument("--out-dir", default="", help="Output directory (default = same folder)")
    args = ap.parse_args()

    out_dir = args.out_dir or os.path.dirname(os.path.abspath(args.results_json))
    plot_curves(args.results_json, out_dir)
    print(f"Saved plots into {out_dir}")
